SELECT
  attr.key AS key,                        
  COUNT(DISTINCT id) AS count             
FROM
  `gcp_project_id.retail_export.sample_retail_products`, 
  UNNEST(attributes) AS attr              
GROUP BY
  1                                       
ORDER BY
  count DESC                              
LIMIT
  50   