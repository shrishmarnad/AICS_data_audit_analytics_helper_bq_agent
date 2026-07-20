SELECT
  eventType,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(productDetails) > 0) AS has_product_ids,
  COUNTIF(filter IS NOT NULL AND filter != '') AS has_filter,
  FORMAT('%.2f', AVG(ARRAY_LENGTH(productDetails))) AS avg_imp_per_search
FROM
  `gcp-project-id.retail_testing.sample_events`
WHERE
  eventType = 'search'
GROUP BY
  eventType