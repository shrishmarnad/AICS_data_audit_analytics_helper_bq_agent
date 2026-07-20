SELECT
  id AS product_id,                                
  primaryProductId,                              
  priceInfo.price AS max_price,                   
  priceInfo.price AS min_price,                   
  priceInfo.originalPrice AS max_orig_price,     
  priceInfo.originalPrice AS min_orig_price      
FROM
  `gcp-project-id.sample_data_import.sample_retail_products`                
ORDER BY
  max_price DESC                                   
LIMIT 10