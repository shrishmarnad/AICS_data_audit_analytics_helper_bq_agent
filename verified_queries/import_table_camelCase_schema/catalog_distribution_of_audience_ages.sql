SELECT
  age_group,
  COUNT(DISTINCT id) AS count
FROM
  `gcp-project-id.sample_data_import.sample_retail_products` 
  CROSS JOIN UNNEST(audience.ageGroups) AS age_group
GROUP BY
  1
ORDER BY
  1, count DESC
LIMIT 50