SELECT
  NET.HOST(uri) AS tld,                             
  COUNT(*) AS unique_count                          
FROM
  `gcp-project-id.sample_data_import.sample_retail_products`     
WHERE
  availability = 'IN_STOCK'                         
  AND uri IS NOT NULL AND uri != ''                 
GROUP BY
  1