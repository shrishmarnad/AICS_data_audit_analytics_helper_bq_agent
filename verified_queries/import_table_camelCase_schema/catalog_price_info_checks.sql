WITH 
ActiveProducts AS (
  SELECT 
    id, 
    type, 
    primaryProductId, 
    priceInfo 
  FROM `gcp-project-id.sample_data_import.sample_retail_products` 
  WHERE availability = 'IN_STOCK' 
),
ParentsWithVariants AS (
  SELECT DISTINCT primaryProductId
  FROM ActiveProducts
  WHERE type = 'VARIANT'
)
SELECT
  type,
  'ALL' AS meta,
  COUNT(DISTINCT id) AS total_ids,
  COUNT(DISTINCT IF(priceInfo IS NOT NULL, id, NULL)) AS has_price_info,
  COUNT(DISTINCT IF(priceInfo.price > 0, id, NULL)) AS has_price,
  COUNT(DISTINCT IF(priceInfo.originalPrice > 0, id, NULL)) AS has_orig_price,
  COUNT(DISTINCT IF(priceInfo.cost > 0, id, NULL)) AS has_cost
FROM ActiveProducts
GROUP BY 1, 2
UNION ALL
SELECT
  ap.type,
  'PRIMARY_WITHOUT_VARIANTS' AS meta,
  COUNT(DISTINCT ap.id) AS total_ids,
  COUNT(DISTINCT IF(ap.priceInfo IS NOT NULL, ap.id, NULL)) AS has_price_info,
  COUNT(DISTINCT IF(ap.priceInfo.price > 0, ap.id, NULL)) AS has_price,
  COUNT(DISTINCT IF(ap.priceInfo.originalPrice > 0, ap.id, NULL)) AS has_orig_price,
  COUNT(DISTINCT IF(ap.priceInfo.cost > 0, ap.id, NULL)) AS has_cost
FROM ActiveProducts ap
LEFT JOIN ParentsWithVariants pwv ON ap.id = pwv.primaryProductId 
WHERE ap.type = 'PRIMARY' 
  AND pwv.primaryProductId IS NULL 
GROUP BY 1, 2;