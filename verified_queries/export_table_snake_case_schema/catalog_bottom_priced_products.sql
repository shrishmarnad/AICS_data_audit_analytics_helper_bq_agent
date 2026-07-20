SELECT
  id AS product_id,                                
  primary_product_id,                              
  price_info.price AS max_price,                   
  price_info.price AS min_price,                   
  price_info.original_price AS max_orig_price,     
  price_info.original_price AS min_orig_price      
FROM
  `gcp-project-id.sample_data_export.sample_retail_products`                
ORDER BY
  min_price ASC                                   
LIMIT 10  