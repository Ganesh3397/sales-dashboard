-- One row per order with customer details, used by the dashboard
DROP VIEW IF EXISTS v_order_details;
CREATE VIEW v_order_details AS
SELECT
    o.order_id,
    o.order_date,
    DATE_TRUNC('month', o.order_date)::DATE AS order_month,
    o.product_id,
    o.product_name,
    o.category,
    o.quantity,
    o.unit_price_inr,
    o.discount_rate,
    CASE WHEN o.order_status = 'Cancelled' THEN 0 ELSE o.net_amount_inr END AS net_amount_inr,
    o.payment_method,
    o.order_status,
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    c.customer_segment,
    c.join_date,
    c.acquisition_channel
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id;
