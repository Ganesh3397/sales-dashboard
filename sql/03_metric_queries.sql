-- Dashboard metrics (same logic as app/queries.py, without filters)

-- KPIs
SELECT
    SUM(net_amount_inr) AS total_net_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(net_amount_inr)
          / COUNT(DISTINCT order_id) FILTER (WHERE order_status <> 'Cancelled'), 2) AS avg_order_value
FROM v_order_details;

-- Monthly revenue trend
SELECT order_month, SUM(net_amount_inr) AS revenue, COUNT(DISTINCT order_id) AS orders
FROM v_order_details
GROUP BY order_month
ORDER BY order_month;

-- Revenue by category
SELECT category, SUM(net_amount_inr) AS revenue
FROM v_order_details
GROUP BY category
ORDER BY revenue DESC;

-- Revenue by customer segment
SELECT customer_segment, SUM(net_amount_inr) AS revenue
FROM v_order_details
GROUP BY customer_segment
ORDER BY revenue DESC;

-- Revenue by city
SELECT city, SUM(net_amount_inr) AS revenue
FROM v_order_details
GROUP BY city
ORDER BY revenue DESC;

-- Orders by status
SELECT order_status, COUNT(DISTINCT order_id) AS orders
FROM v_order_details
GROUP BY order_status
ORDER BY orders DESC;

-- Top 5 products
SELECT product_name, category, SUM(net_amount_inr) AS revenue
FROM v_order_details
GROUP BY product_name, category
ORDER BY revenue DESC
LIMIT 5;

-- Repeat customers (2 or more non-cancelled orders)
SELECT COUNT(*) AS repeat_customers
FROM (
    SELECT customer_id
    FROM v_order_details
    WHERE order_status <> 'Cancelled'
    GROUP BY customer_id
    HAVING COUNT(DISTINCT order_id) >= 2
) t;
