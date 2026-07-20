SELECT
  sizes, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp-project-id.sample_data_import.sample_retail_products`
GROUP BY
  sizes
ORDER BY
  count DESC 
LIMIT 50;