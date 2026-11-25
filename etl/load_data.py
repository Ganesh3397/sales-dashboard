"""
Loads customers.xlsx and orders.xlsx into PostgreSQL.

Usage:
    python -m etl.load_data
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import psycopg

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sales:sales@localhost:5432/sales_db")

CUSTOMER_COLUMNS = [
    "customer_id", "customer_name", "email", "city", "state",
    "customer_segment", "join_date", "acquisition_channel",
]
ORDER_COLUMNS = [
    "order_id", "customer_id", "order_date", "product_id", "product_name", "category",
    "quantity", "unit_price_inr", "discount_rate", "net_amount_inr",
    "payment_method", "order_status",
]


def read_excel(file_name, columns):
    df = pd.read_excel(DATA_DIR / file_name)
    df.columns = [c.strip().lower() for c in df.columns]

    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"{file_name} is missing columns: {missing}")

    df = df[columns]
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()
    return df


def validate(customers, orders):
    errors = []

    if customers["customer_id"].duplicated().any():
        errors.append("duplicate customer_id in customers")
    if orders["order_id"].duplicated().any():
        errors.append("duplicate order_id in orders")

    unknown = set(orders["customer_id"]) - set(customers["customer_id"])
    if unknown:
        errors.append(f"orders have unknown customer_id: {sorted(unknown)}")

    bad_status = set(orders["order_status"]) - {"Completed", "Returned", "Cancelled"}
    if bad_status:
        errors.append(f"unknown order_status values: {bad_status}")

    if errors:
        raise ValueError("\n".join(errors))

    # business rule: cancelled orders have zero revenue
    orders.loc[orders["order_status"] == "Cancelled", "net_amount_inr"] = 0


def wait_for_db(retries=20):
    for _ in range(retries):
        try:
            psycopg.connect(DATABASE_URL).close()
            return
        except psycopg.OperationalError:
            print("Waiting for database...")
            time.sleep(2)
    raise RuntimeError("Database is not reachable")


def insert_rows(cur, table, df):
    cols = ", ".join(df.columns)
    with cur.copy(f"COPY {table} ({cols}) FROM STDIN") as copy:
        for row in df.itertuples(index=False):
            copy.write_row(row)


def main():
    customers = read_excel("customers.xlsx", CUSTOMER_COLUMNS)
    orders = read_excel("orders.xlsx", ORDER_COLUMNS)
    validate(customers, orders)

    customers["join_date"] = pd.to_datetime(customers["join_date"]).dt.date
    orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.date

    wait_for_db()

    # everything runs in one transaction, so a failure leaves the old data untouched
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute((SQL_DIR / "01_schema.sql").read_text())
            cur.execute("TRUNCATE orders, customers")
            insert_rows(cur, "customers", customers)
            insert_rows(cur, "orders", orders)
            cur.execute((SQL_DIR / "02_views.sql").read_text())

            cur.execute("SELECT COUNT(*) FROM v_order_details")
            joined = cur.fetchone()[0]

    print(f"Loaded {len(customers)} customers and {len(orders)} orders ({joined} rows in v_order_details)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Load failed: {e}")
        sys.exit(1)
