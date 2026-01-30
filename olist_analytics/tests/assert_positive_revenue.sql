-- This test fails if any category has zero or negative revenue
SELECT
    product_category_name,
    total_revenue
FROM {{ ref('mart_category_profit') }}
WHERE total_revenue <= 0
