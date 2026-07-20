SELECT
  flat_color_family AS colorFamilies, 
  COUNT(DISTINCT id) AS count 
FROM
  `gcp_project_id.retail_dataset.my_catalog`, 
  UNNEST(colorInfo.colorFamilies) AS flat_color_family 
WHERE
  ARRAY_LENGTH(colorInfo.colorFamilies) > 0 
GROUP BY
  flat_color_family
ORDER BY
  count DESC
LIMIT 50;