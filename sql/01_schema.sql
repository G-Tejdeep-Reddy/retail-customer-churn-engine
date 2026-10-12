-- Drop existing tables if re-running script
DROP TABLE IF EXISTS fact_retail_transactions CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;

-- 1. Customer Dimension Table
CREATE TABLE dim_customers (
    customer_id INT PRIMARY KEY,
    country VARCHAR(100)
);

-- 2. Product Dimension Table
CREATE TABLE dim_products (
    stock_code VARCHAR(50) PRIMARY KEY,
    description TEXT,
    unit_price NUMERIC(10, 2)
);

-- 3. Retail Transactions Fact Table
CREATE TABLE fact_retail_transactions (
    transaction_id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50),
    customer_id INT REFERENCES dim_customers(customer_id),
    stock_code VARCHAR(50) REFERENCES dim_products(stock_code),
    quantity INT,
    invoice_date TIMESTAMP,
    unit_price NUMERIC(10, 2),
    total_amount NUMERIC(12, 2)
);

-- Create indexes for fast analytical query performance
CREATE INDEX idx_fact_customer ON fact_retail_transactions(customer_id);
CREATE INDEX idx_fact_date ON fact_retail_transactions(invoice_date);