SELECT
  title AS distinct_duplicate_title,
  ARRAY_AGG(id LIMIT 10) AS primary_product_ids_sample
FROM
  `gcp-project-id.sample_data_export.sample_retail_products` 
WHERE
  type = 'PRIMARY'
GROUP BY
  1
HAVING
  COUNT(*) > 1
ORDER BY
  COUNT(*) DESC
LIMIT
  10; 