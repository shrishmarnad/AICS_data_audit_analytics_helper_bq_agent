WITH ActiveInventory AS (
  SELECT
    id,
    type,
    primaryProductId,
    priceInfo.price AS price,
    priceInfo.originalPrice AS originalPrice,
    availability,
    'default_branch' AS branch_id 
  FROM
    `gcp-project-id.sample_data_import.sample_retail_products` 
  WHERE
    availability = 'IN_STOCK' 
),
VariantParents AS (
  SELECT DISTINCT
    primaryProductId
  FROM
    ActiveInventory
  WHERE
    type = 'VARIANT'
    AND primaryProductId IS NOT NULL
)
SELECT
  base.branch_id,
  CASE
    WHEN base.originalPrice IS NULL OR base.price IS NULL THEN 'Price Info Missing'
    WHEN (base.originalPrice - base.price) > 0 THEN 'Products with Discounted Price'
    WHEN (base.originalPrice - base.price) = 0 THEN 'Products with No Discounted Price'
    WHEN (base.originalPrice - base.price) < 0 THEN 'Products with Negative Discounts'
    ELSE 'Price Info Missing'
  END AS discount,
  COUNT(DISTINCT base.id) AS total_type_count
FROM
  ActiveInventory AS base
LEFT JOIN
  VariantParents AS parents
  ON base.id = parents.primaryProductId
WHERE
  base.type = 'VARIANT'
  OR
  (base.type = 'PRIMARY' AND parents.primaryProductId IS NULL)
GROUP BY
  1, 2;