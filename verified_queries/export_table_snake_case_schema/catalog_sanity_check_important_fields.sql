WITH ActiveProducts AS (
  SELECT 
    id, 
    type, 
    primary_product_id, 
    title, 
    uri, 
    description, 
    categories, 
    brands, 
    available_quantity
  FROM `gcp-project-id.sample_data_export.sample_retail_products` 
  WHERE availability = 'IN_STOCK' 
),
VariantParents AS (
  SELECT DISTINCT primary_product_id 
  FROM ActiveProducts 
  WHERE type = 'VARIANT'
)
SELECT 
  'default' AS branch_id, 
  type, 
  'ALL' AS meta,
  COUNT(DISTINCT id) AS total_ids,
  COUNT(DISTINCT IF(LENGTH(uri) > 0, id, NULL)) AS urls,
  COUNT(DISTINCT IF(STARTS_WITH(uri, 'http') OR STARTS_WITH(uri, 'www'), id, NULL)) AS valid_urls,
  COUNT(DISTINCT IF(LENGTH(title) > 0, id, NULL)) AS has_titles,
  COUNT(DISTINCT IF(LENGTH(description) > 0, id, NULL)) AS valid_description,
  COUNT(DISTINCT IF(ARRAY_LENGTH(categories) > 0, id, NULL)) AS has_categories,
  COUNT(DISTINCT IF(ARRAY_LENGTH(brands) > 0, id, NULL)) AS has_brands,
  COUNT(DISTINCT IF(available_quantity IS NOT NULL, id, NULL)) AS has_availability
FROM ActiveProducts
GROUP BY 1, 2, 3
UNION ALL
SELECT 
  'default' AS branch_id,
  p.type, 
  'PRIMARY_WITHOUT_VARIANTS' AS meta,
  COUNT(DISTINCT p.id) AS total_ids,
  COUNT(DISTINCT IF(LENGTH(p.uri) > 0, p.id, NULL)) AS urls,
  COUNT(DISTINCT IF(STARTS_WITH(p.uri, 'http') OR STARTS_WITH(p.uri, 'www'), p.id, NULL)) AS valid_urls,
  COUNT(DISTINCT IF(LENGTH(p.title) > 0, p.id, NULL)) AS has_titles,
  COUNT(DISTINCT IF(LENGTH(p.description) > 0, p.id, NULL)) AS valid_description,
  COUNT(DISTINCT IF(ARRAY_LENGTH(p.categories) > 0, p.id, NULL)) AS has_categories,
  COUNT(DISTINCT IF(ARRAY_LENGTH(p.brands) > 0, p.id, NULL)) AS has_brands,
  COUNT(DISTINCT IF(available_quantity IS NOT NULL, p.id, NULL)) AS has_availability
FROM ActiveProducts p
LEFT JOIN VariantParents v ON p.id = v.primary_product_id
WHERE p.type = 'PRIMARY' 
  AND v.primary_product_id IS NULL 
GROUP BY 1, 2, 3
ORDER BY branch_id, type, meta;