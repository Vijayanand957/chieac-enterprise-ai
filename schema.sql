CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100),
    region VARCHAR(50),
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS sales_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    product_category VARCHAR(50),
    order_date DATE,
    unit_price NUMERIC(10, 2),
    quantity INT,
    total_amount NUMERIC(10, 2)
);

CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_transactions(order_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_category ON sales_transactions(product_category);

CREATE OR REPLACE PROCEDURE refresh_sales_summary()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TABLE IF NOT EXISTS daily_sales_summary AS
    SELECT 
        order_date,
        product_category,
        SUM(total_amount) AS daily_revenue,
        COUNT(transaction_id) AS total_orders
    FROM sales_transactions
    GROUP BY order_date, product_category;
END;
$$;

CREATE OR REPLACE VIEW view_mom_sales_analytics AS
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS sales_month,
        product_category,
        SUM(total_amount) AS monthly_revenue,
        COUNT(DISTINCT transaction_id) AS total_orders
    FROM sales_transactions
    GROUP BY 1, 2
)
SELECT 
    sales_month,
    product_category,
    monthly_revenue,
    LAG(monthly_revenue) OVER (
        PARTITION BY product_category 
        ORDER BY sales_month
    ) AS prior_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue) OVER (PARTITION BY product_category ORDER BY sales_month)) / 
        NULLIF(LAG(monthly_revenue) OVER (PARTITION BY product_category ORDER BY sales_month), 0)) * 100, 2
    ) AS mom_growth_pct,
    DENSE_RANK() OVER (
        PARTITION BY sales_month 
        ORDER BY monthly_revenue DESC
    ) AS category_revenue_rank
FROM monthly_metrics;
