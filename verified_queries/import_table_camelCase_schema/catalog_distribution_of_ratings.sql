SELECT
  rating.averageRating, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp-project-id.sample_data_import.sample_retail_products` 
WHERE
  rating.averageRating IS NOT NULL 
GROUP BY
  1 
ORDER BY
  count DESC 
LIMIT 50;