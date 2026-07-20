SELECT
  sizes, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp-project-id.sample_data_export.sample_retail_products`
GROUP BY
  sizes
ORDER BY
  count DESC 
LIMIT 50; 