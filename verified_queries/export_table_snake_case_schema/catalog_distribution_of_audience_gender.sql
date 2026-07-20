SELECT
  TO_JSON_STRING(audience.genders) AS genders, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp-project-id.sample_data_export.sample_retail_products` 
GROUP BY
  genders
ORDER BY
  count DESC
LIMIT 50;