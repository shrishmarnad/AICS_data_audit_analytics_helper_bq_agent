SELECT
  id AS product_id,                                
  primaryProductId,                              
  priceInfo.price AS max_price,                   
  priceInfo.price AS min_price,                   
  priceInfo.originalPrice AS max_orig_price,     
  priceInfo.originalPrice AS min_orig_price      
FROM
  `gcp-project-id.sample_data_export.sample_retail_products`                
ORDER BY
  min_price ASC                                   
LIMIT 10