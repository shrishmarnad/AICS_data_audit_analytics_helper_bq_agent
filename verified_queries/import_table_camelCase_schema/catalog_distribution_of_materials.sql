SELECT
    material, 
    COUNT(DISTINCT p.id) AS count 
FROM
    `gcp-project-id.sample_data_import.sample_retail_products` AS p, 
    UNNEST(p.materials) AS material 
GROUP BY
    material 
ORDER BY
    count DESC 
LIMIT 50;