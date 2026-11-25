from app.db import fetch_all, fetch_one

# filter name from the API -> column in v_order_details
FILTER_COLUMNS = {
    "category": "category",
    "segment": "customer_segment",
    "city": "city",
    "status": "order_status",
}


def build_where(filters):
    conditions = []
    params = []

    if filters.get("start_date"):
        conditions.append("order_date >= %s")
        params.append(filters["start_date"])
    if filters.get("end_date"):
        conditions.append("order_date <= %s")
        params.append(filters["end_date"])

    for key, column in FILTER_COLUMNS.items():
        if filters.get(key):
            conditions.append(f"{column} = %s")
            params.append(filters[key])

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    return where, params


def get_kpis(filters):
    where, params = build_where(filters)
    row = fetch_one(f"""
        SELECT
            COALESCE(SUM(net_amount_inr), 0) AS total_revenue,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(DISTINCT customer_id) AS unique_customers,
            COUNT(DISTINCT order_id) FILTER (WHERE order_status <> 'Cancelled') AS valid_orders,
            COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'Cancelled') AS cancelled_orders,
            COUNT(DISTINCT order_id) FILTER (WHERE order_status = 'Returned') AS returned_orders,
            COALESCE(SUM(net_amount_inr) FILTER (WHERE order_status = 'Returned'), 0) AS returned_revenue
        FROM v_order_details {where}
    """, params)

    repeat = fetch_one(f"""
        SELECT COUNT(*) AS repeat_customers
        FROM (
            SELECT customer_id
            FROM v_order_details {where}
            {"AND" if where else "WHERE"} order_status <> 'Cancelled'
            GROUP BY customer_id
            HAVING COUNT(DISTINCT order_id) >= 2
        ) t
    """, params)

    revenue = float(row["total_revenue"])
    valid_orders = row["valid_orders"]

    return {
        "total_revenue": revenue,
        "total_orders": row["total_orders"],
        "unique_customers": row["unique_customers"],
        "valid_orders": valid_orders,
        "cancelled_orders": row["cancelled_orders"],
        "returned_orders": row["returned_orders"],
        "returned_revenue": float(row["returned_revenue"]),
        # AOV = net revenue / non-cancelled orders
        "avg_order_value": round(revenue / valid_orders, 2) if valid_orders else 0,
        "repeat_customers": repeat["repeat_customers"],
    }


def get_monthly_revenue(filters):
    where, params = build_where(filters)
    rows = fetch_all(f"""
        SELECT TO_CHAR(order_month, 'YYYY-MM') AS month,
               SUM(net_amount_inr) AS revenue,
               COUNT(DISTINCT order_id) AS orders
        FROM v_order_details {where}
        GROUP BY order_month
        ORDER BY order_month
    """, params)
    return [{**r, "revenue": float(r["revenue"])} for r in rows]


def get_revenue_by(column, filters):
    where, params = build_where(filters)
    rows = fetch_all(f"""
        SELECT {column} AS name,
               SUM(net_amount_inr) AS revenue,
               COUNT(DISTINCT order_id) AS orders
        FROM v_order_details {where}
        GROUP BY {column}
        ORDER BY revenue DESC, orders DESC
    """, params)
    return [{**r, "revenue": float(r["revenue"])} for r in rows]


def get_top_products(filters, limit=5):
    where, params = build_where(filters)
    rows = fetch_all(f"""
        SELECT product_name, category,
               SUM(net_amount_inr) AS revenue,
               COUNT(DISTINCT order_id) AS orders
        FROM v_order_details {where}
        GROUP BY product_name, category
        ORDER BY revenue DESC
        LIMIT %s
    """, params + [limit])
    return [{**r, "revenue": float(r["revenue"])} for r in rows]


def get_orders(filters, limit=500):
    where, params = build_where(filters)
    rows = fetch_all(f"""
        SELECT order_id, TO_CHAR(order_date, 'YYYY-MM-DD') AS order_date,
               customer_name, city, customer_segment, product_name, category,
               quantity, net_amount_inr, order_status
        FROM v_order_details {where}
        ORDER BY order_date DESC, order_id DESC
        LIMIT %s
    """, params + [limit])
    return [{**r, "net_amount_inr": float(r["net_amount_inr"])} for r in rows]


def get_filter_options():
    def distinct(column):
        rows = fetch_all(f"SELECT DISTINCT {column} AS value FROM v_order_details ORDER BY 1")
        return [r["value"] for r in rows]

    dates = fetch_one("SELECT MIN(order_date) AS min_date, MAX(order_date) AS max_date FROM v_order_details")

    return {
        "category": distinct("category"),
        "segment": distinct("customer_segment"),
        "city": distinct("city"),
        "status": distinct("order_status"),
        "min_date": str(dates["min_date"]),
        "max_date": str(dates["max_date"]),
    }
