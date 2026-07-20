WITH 
ActiveProducts AS (
  SELECT 
    id, 
    type, 
    primary_product_id, 
    price_info 
  FROM `gcp-project-id.sample_data_export.sample_retail_products` 
  WHERE availability = 'IN_STOCK' 
),
ParentsWithVariants AS (
  SELECT DISTINCT primary_product_id
  FROM ActiveProducts
  WHERE type = 'VARIANT'
)
SELECT
  type,
  'ALL' AS meta,
  COUNT(DISTINCT id) AS total_ids,
  COUNT(DISTINCT IF(price_info IS NOT NULL, id, NULL)) AS has_price_info,
  COUNT(DISTINCT IF(price_info.price > 0, id, NULL)) AS has_price,
  COUNT(DISTINCT IF(price_info.original_price > 0, id, NULL)) AS has_orig_price,
  COUNT(DISTINCT IF(price_info.cost > 0, id, NULL)) AS has_cost
FROM ActiveProducts
GROUP BY 1, 2
UNION ALL
SELECT
  ap.type,
  'PRIMARY_WITHOUT_VARIANTS' AS meta,
  COUNT(DISTINCT ap.id) AS total_ids,
  COUNT(DISTINCT IF(ap.price_info IS NOT NULL, ap.id, NULL)) AS has_price_info,
  COUNT(DISTINCT IF(ap.price_info.price > 0, ap.id, NULL)) AS has_price,
  COUNT(DISTINCT IF(ap.price_info.original_price > 0, ap.id, NULL)) AS has_orig_price,
  COUNT(DISTINCT IF(ap.price_info.cost > 0, ap.id, NULL)) AS has_cost
FROM ActiveProducts ap
LEFT JOIN ParentsWithVariants pwv ON ap.id = pwv.primary_product_id 
WHERE ap.type = 'PRIMARY' 
  AND pwv.primary_product_id IS NULL 
GROUP BY 1, 2;