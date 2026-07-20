SELECT
  age_group,
  COUNT(DISTINCT id) AS count
FROM
  `gcp-project-id.sample_data_export.sample_retail_products` 
  CROSS JOIN UNNEST(audience.age_groups) AS age_group
GROUP BY
  1, 2
ORDER BY
  1, count DESC
LIMIT 50