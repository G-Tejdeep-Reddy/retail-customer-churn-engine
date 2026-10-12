-- Step 1: Assign RFM scores using a PostgreSQL-compatible CTE for percentiles
CREATE OR REPLACE VIEW v_customer_rfm_scores AS
WITH percentiles AS (
    SELECT 
        percentile_cont(0.2) WITHIN GROUP (ORDER BY recency_days) AS p20,
        percentile_cont(0.4) WITHIN GROUP (ORDER BY recency_days) AS p40,
        percentile_cont(0.6) WITHIN GROUP (ORDER BY recency_days) AS p60,
        percentile_cont(0.8) WITHIN GROUP (ORDER BY recency_days) AS p80
    FROM v_rfm_raw_metrics
)
SELECT 
    m.customer_id,
    m.country,
    m.recency_days,
    m.frequency,
    m.monetary_value,
    -- Recency Score: Lower days is better (inverted scale: lowest recency = score 5)
    CASE 
        WHEN m.recency_days <= p.p20 THEN 5
        WHEN m.recency_days <= p.p40 THEN 4
        WHEN m.recency_days <= p.p60 THEN 3
        WHEN m.recency_days <= p.p80 THEN 2
        ELSE 1
    END AS r_score,
    -- Frequency Score: Higher frequency is better (NTILE supports OVER natively)
    NTILE(5) OVER (ORDER BY m.frequency ASC) AS f_score,
    -- Monetary Score: Higher monetary spend is better
    NTILE(5) OVER (ORDER BY m.monetary_value ASC) AS m_score
FROM v_rfm_raw_metrics m
CROSS JOIN percentiles p;

-- Step 2: Categorize customers into actionable marketing and retention segments
CREATE OR REPLACE VIEW v_customer_segments AS
SELECT 
    customer_id,
    country,
    recency_days,
    frequency,
    monetary_value,
    r_score,
    f_score,
    m_score,
    (r_score::text || f_score::text || m_score::text) AS rfm_cell_string,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk Customers'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Cant Lose Them'
        ELSE 'Hibernating / Lost'
    END AS customer_segment
FROM v_customer_rfm_scores;