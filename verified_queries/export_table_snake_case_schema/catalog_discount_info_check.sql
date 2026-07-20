WITH ActiveInventory AS (
  SELECT
    id,
    type,
    primary_product_id,
    price_info.price AS price,
    price_info.original_price AS original_price,
    availability,
    'default_branch' AS branch_id 
  FROM
    `gcp-project-id.sample_data_export.sample_retail_products` 
  WHERE
    availability = 'IN_STOCK' 
),
VariantParents AS (
  SELECT DISTINCT
    primary_product_id
  FROM
    ActiveInventory
  WHERE
    type = 'VARIANT'
    AND primary_product_id IS NOT NULL
)
SELECT
  base.branch_id,
  CASE
    WHEN base.original_price IS NULL OR base.price IS NULL THEN 'Price Info Missing'
    WHEN (base.original_price - base.price) > 0 THEN 'Products with Discounted Price'
    WHEN (base.original_price - base.price) = 0 THEN 'Products with No Discounted Price'
    WHEN (base.original_price - base.price) < 0 THEN 'Products with Negative Discounts'
    ELSE 'Price Info Missing'
  END AS discount,
  COUNT(DISTINCT base.id) AS total_type_count
FROM
  ActiveInventory AS base
LEFT JOIN
  VariantParents AS parents
  ON base.id = parents.primary_product_id
WHERE
  base.type = 'VARIANT'
  OR
  (base.type = 'PRIMARY' AND parents.primary_product_id IS NULL)
GROUP BY
  1, 2;