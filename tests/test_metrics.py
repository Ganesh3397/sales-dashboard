"""
Checks API numbers against values calculated directly from the Excel files with pandas.
Needs a running PostgreSQL (DATABASE_URL).
"""
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from etl import load_data

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def client():
    load_data.main()
    return TestClient(app)


@pytest.fixture(scope="module")
def df():
    customers = pd.read_excel(DATA_DIR / "customers.xlsx")
    orders = pd.read_excel(DATA_DIR / "orders.xlsx")
    data = orders.merge(customers, on="Customer_ID")
    data.loc[data["Order_Status"] == "Cancelled", "Net_Amount_INR"] = 0
    return data


def expected_kpis(data):
    revenue = data["Net_Amount_INR"].sum()
    valid = data[data["Order_Status"] != "Cancelled"]
    return {
        "total_revenue": revenue,
        "total_orders": data["Order_ID"].nunique(),
        "unique_customers": data["Customer_ID"].nunique(),
        "avg_order_value": round(revenue / valid["Order_ID"].nunique(), 2),
        "repeat_customers": (valid.groupby("Customer_ID")["Order_ID"].nunique() >= 2).sum(),
    }


def test_headline_numbers(client):
    kpis = client.get("/api/dashboard").json()["kpis"]
    assert kpis["total_revenue"] == 1159206
    assert kpis["total_orders"] == 240
    assert kpis["unique_customers"] == 59
    assert kpis["avg_order_value"] == 5682.38


@pytest.mark.parametrize("params, column, value", [
    ({"category": "Electronics"}, "Category", "Electronics"),
    ({"segment": "Corporate"}, "Customer_Segment", "Corporate"),
    ({"city": "Pune"}, "City", "Pune"),
    ({"status": "Returned"}, "Order_Status", "Returned"),
])
def test_kpis_with_filter(client, df, params, column, value):
    kpis = client.get("/api/dashboard", params=params).json()["kpis"]
    expected = expected_kpis(df[df[column] == value])
    for key, val in expected.items():
        assert kpis[key] == pytest.approx(val), key


def test_date_filter(client, df):
    params = {"start_date": "2026-02-01", "end_date": "2026-04-30"}
    kpis = client.get("/api/dashboard", params=params).json()["kpis"]
    subset = df[(df["Order_Date"] >= "2026-02-01") & (df["Order_Date"] <= "2026-04-30")]
    assert kpis["total_revenue"] == subset["Net_Amount_INR"].sum()


def test_breakdowns_add_up_to_total(client):
    data = client.get("/api/dashboard").json()
    total = data["kpis"]["total_revenue"]
    for key in ["monthly", "by_category", "by_segment", "by_city", "by_status"]:
        assert sum(row["revenue"] for row in data[key]) == pytest.approx(total)


def test_cancelled_orders_are_zero(client):
    orders = client.get("/api/orders", params={"status": "Cancelled"}).json()
    assert len(orders) == 36
    assert all(o["net_amount_inr"] == 0 for o in orders)


def test_bad_date_range(client):
    res = client.get("/api/dashboard", params={"start_date": "2026-05-01", "end_date": "2026-01-01"})
    assert res.status_code == 400
