  SELECT
  value,
  COUNT(*) AS count
FROM
  `gcp-project-id.sample_data_export.sample_retail_products`, 
  UNNEST(attributes) AS attr,
  UNNEST(attr.CustomAttribute.text) AS value
WHERE
  attr.key = 'sportLabels'
GROUP BY
  1
ORDER BY
  count DESC
LIMIT 50