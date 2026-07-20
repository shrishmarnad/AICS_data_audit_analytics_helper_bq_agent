SELECT
  type, 
  COUNT(DISTINCT id) AS total_type_count 
FROM
  `gcp-project-id.sample_data_export.sample_retail_products` 

GROUP BY
  1
ORDER BY
  1 DESC;