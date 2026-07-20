SELECT
  FORMAT_DATE("%m-%d-%Y", DATE(TIMESTAMP(eventTime))) AS date,
  COUNT(*) AS total_search_events,
  COUNTIF(LENGTH(searchQuery) > 0 AND (pageCategories IS NULL OR ARRAY_LENGTH(pageCategories) = 0)) AS is_search_event,
  COUNTIF(attributionToken IS NULL AND LENGTH(searchQuery) > 0) AS search_missing_attribution_token,
  COUNTIF((pageCategories IS NOT NULL AND ARRAY_LENGTH(pageCategories) > 0) AND (searchQuery IS NULL OR searchQuery = '')) AS is_browse_event,
  COUNTIF(attributionToken IS NULL AND (searchQuery IS NULL OR searchQuery = '')) AS browse_missing_attribution_token
FROM
  `gcp-project-id.retail_testing.sample_events`
WHERE
  eventType = 'search'
GROUP BY
  date
ORDER BY
  date DESC