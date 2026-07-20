SELECT  brands, COUNT(DISTINCT id) AS brands_count
FROM `gcp-project-id.sample_data_export.sample_retail_products` 
WHERE
   type = "PRIMARY"
GROUP BY
  1 
ORDER BY
  2 DESC 
LIMIT 50;
