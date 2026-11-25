-- One customer -> many orders (orders.customer_id -> customers.customer_id)

CREATE TABLE IF NOT EXISTS customers (
    customer_id          VARCHAR(10)  PRIMARY KEY,
    customer_name        VARCHAR(100) NOT NULL,
    email                VARCHAR(255) NOT NULL UNIQUE,
    city                 VARCHAR(60)  NOT NULL,
    state                VARCHAR(60)  NOT NULL,
    customer_segment     VARCHAR(30)  NOT NULL,
    join_date            DATE         NOT NULL,
    acquisition_channel  VARCHAR(30)  NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id         VARCHAR(10)   PRIMARY KEY,
    customer_id      VARCHAR(10)   NOT NULL
                     REFERENCES customers (customer_id)
                     ON UPDATE CASCADE
                     ON DELETE RESTRICT,
    order_date       DATE          NOT NULL,
    product_id       VARCHAR(10)   NOT NULL,
    product_name     VARCHAR(100)  NOT NULL,
    category         VARCHAR(50)   NOT NULL,
    quantity         INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price_inr   NUMERIC(12,2) NOT NULL CHECK (unit_price_inr >= 0),
    discount_rate    NUMERIC(5,4)  NOT NULL CHECK (discount_rate BETWEEN 0 AND 1),
    net_amount_inr   NUMERIC(12,2) NOT NULL CHECK (net_amount_inr >= 0),
    payment_method   VARCHAR(30)   NOT NULL,
    order_status     VARCHAR(20)   NOT NULL
                     CHECK (order_status IN ('Completed', 'Returned', 'Cancelled')),
    CONSTRAINT chk_cancelled_zero_amount
        CHECK (order_status <> 'Cancelled' OR net_amount_inr = 0)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date  ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_category    ON orders (category);
CREATE INDEX IF NOT EXISTS idx_orders_status      ON orders (order_status);
CREATE INDEX IF NOT EXISTS idx_customers_segment  ON customers (customer_segment);
CREATE INDEX IF NOT EXISTS idx_customers_city     ON customers (city);
