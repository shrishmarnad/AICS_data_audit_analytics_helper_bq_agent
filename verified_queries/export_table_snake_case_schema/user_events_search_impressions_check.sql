SELECT
  event_type,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(product_details) > 0) AS has_product_ids,
  COUNTIF(filter IS NOT NULL AND filter != '') AS has_filter,
  FORMAT('%.2f', AVG(ARRAY_LENGTH(product_details))) AS avg_imp_per_search
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
WHERE
  event_type = 'search'
GROUP BY
  event_type