WITH TotalMetrics AS (
  SELECT COUNT(DISTINCT id) AS total_count FROM `gcp-project-id.sample_data_export.sample_retail_products`
)
SELECT
  cat_flat AS categories, 
  COUNT(DISTINCT t.id) AS count,
  
  (COUNT(DISTINCT t.id) / (SELECT total_count FROM TotalMetrics)) * 100 AS Percent
FROM `gcp-project-id.sample_data_export.sample_retail_products` t
LEFT JOIN UNNEST(categories) AS cat_flat 
GROUP BY 1
ORDER BY count DESC
LIMIT 50;