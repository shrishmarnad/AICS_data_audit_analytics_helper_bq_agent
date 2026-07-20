SELECT
  value,
  COUNT(*) AS count
FROM
  `gcp-project-id.sample_data_import.sample_retail_products`, 
  UNNEST(attributes) AS attr,
  UNNEST(attr.value.text) AS value
WHERE
  attr.key = 'sportLabels'
GROUP BY
  1
ORDER BY
  count DESC
LIMIT 50