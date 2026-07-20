SELECT
  color, 
  COUNT(DISTINCT p.id) AS count 
FROM
  `gcp-project-id.sample_data_export.sample_retail_products` AS p,
  UNNEST(p.color_info.colors) AS color 
GROUP BY
  color 
ORDER BY
  count DESC 
LIMIT 50; 