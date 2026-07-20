SELECT
  flat_color_family AS color_families, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp-project-id.sample_data_export.sample_retail_products`, 
  UNNEST(color_info.color_families) AS flat_color_family 
WHERE
  ARRAY_LENGTH(color_info.color_families) > 0 
GROUP BY
  flat_color_family
ORDER BY
  count DESC
LIMIT 50;