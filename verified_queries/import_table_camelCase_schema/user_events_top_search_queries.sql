SELECT
  COUNT(*) AS top_queries,
  searchQuery
FROM
  `gcp-project-id.retail_testing.sample_events`
WHERE
  eventType = 'search'
  AND LENGTH(searchQuery) > 0
  AND ARRAY_LENGTH(pageCategories) = 0
GROUP BY
  searchQuery
ORDER BY
  top_queries DESC