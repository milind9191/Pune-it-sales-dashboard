-- All queries compare April to October (month_no <= 7) of FY27 with the same months of FY26.

-- 1. Headline numbers
SELECT fy,
       SUM(revenue_cr)                                  AS revenue_cr,
       SUM(person_months)                               AS person_months,
       ROUND(SUM(revenue_cr) * 100 / SUM(person_months), 2) AS avg_rate_lakh_per_pm
FROM billing
WHERE month_no <= 7
GROUP BY fy
ORDER BY fy;

-- 2. Year-over-year growth by service line (swap the column for geography)
SELECT service_line,
       ROUND(SUM(CASE WHEN fy = 'FY27' THEN revenue_cr END), 1) AS fy27,
       ROUND(SUM(CASE WHEN fy = 'FY26' THEN revenue_cr END), 1) AS fy26,
       ROUND(100.0 * (SUM(CASE WHEN fy = 'FY27' THEN revenue_cr END)
                    / SUM(CASE WHEN fy = 'FY26' THEN revenue_cr END) - 1), 1) AS yoy_pct
FROM billing
WHERE month_no <= 7
GROUP BY service_line
ORDER BY yoy_pct DESC;

-- 3. Top engagements
SELECT engagement, ROUND(SUM(revenue_cr), 1) AS revenue_cr
FROM billing
WHERE fy = 'FY27' AND month_no <= 7
GROUP BY engagement
ORDER BY revenue_cr DESC
LIMIT 3;

-- 4. Concentration: each engagement's share of revenue
SELECT engagement,
       ROUND(100 * SUM(revenue_cr) / SUM(SUM(revenue_cr)) OVER (), 1) AS share_pct
FROM billing
WHERE fy = 'FY27' AND month_no <= 7
GROUP BY engagement
ORDER BY share_pct DESC;

-- 5. Anomalies: months whose YoY change is more than 30% away from the
--    median YoY change of the same geography and service line
WITH m AS (
    SELECT geography, service_line, month_name, month_seq,
           LN(revenue_cr / LAG(revenue_cr, 12) OVER (
               PARTITION BY geography, service_line ORDER BY month_seq)) AS log_yoy
    FROM monthly_billing
),
f AS (SELECT * FROM m WHERE month_seq > 12),
med AS (
    SELECT geography, service_line,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY log_yoy) AS med_log_yoy
    FROM f GROUP BY geography, service_line
)
SELECT f.geography, f.service_line, f.month_name,
       ROUND(100 * (EXP(f.log_yoy) - 1), 1) AS yoy_pct
FROM f JOIN med USING (geography, service_line)
WHERE ABS(f.log_yoy - med.med_log_yoy) > 0.3
ORDER BY ABS(f.log_yoy - med.med_log_yoy) DESC;

-- 6. Rest-of-year baseline: last year's Nov to Mar scaled by YTD growth
WITH g AS (
    SELECT SUM(CASE WHEN fy = 'FY27' THEN revenue_cr END)
         / SUM(CASE WHEN fy = 'FY26' THEN revenue_cr END) - 1 AS growth
    FROM billing WHERE month_no <= 7
)
SELECT ROUND(SUM(b.revenue_cr) * (1 + g.growth), 1) AS forecast_nov_to_mar_cr
FROM billing b, g
WHERE b.fy = 'FY26' AND b.month_no >= 8
GROUP BY g.growth;
