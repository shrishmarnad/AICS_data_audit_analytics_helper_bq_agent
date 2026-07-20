SELECT
  rating.average_rating, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp-project-id.sample_data_export.sample_retail_products` 
WHERE
  rating.average_rating IS NOT NULL 
GROUP BY
  1 
ORDER BY
  count DESC 
LIMIT 50; 