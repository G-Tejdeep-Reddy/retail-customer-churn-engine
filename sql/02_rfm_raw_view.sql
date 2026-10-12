CREATE OR REPLACE VIEW v_rfm_raw_metrics AS
SELECT 
    c.customer_id,
    c.country,
    -- Recency: Days between the absolute max transaction date in system and customer's last invoice
    (SELECT MAX(invoice_date)::date FROM fact_retail_transactions) - MAX(t.invoice_date)::date AS recency_days,
    -- Frequency: Unique order count
    COUNT(DISTINCT t.invoice_no) AS frequency,
    -- Monetary: Total revenue contributed
    SUM(t.total_amount) AS monetary_value
FROM dim_customers c
JOIN fact_retail_transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.country;