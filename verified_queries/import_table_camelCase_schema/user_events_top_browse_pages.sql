SELECT
  COUNT(*) AS total,
  ARRAY_TO_STRING(pageCategories, '-') AS page_categories,
  filter
FROM
 `gcp-project-id.retail_testing.sample_events`
WHERE
  eventType = 'search'
  AND (
    searchQuery IS NULL
    OR searchQuery = ''
  )
  AND ARRAY_LENGTH(pageCategories) > 0
GROUP BY
  page_categories,
  filter
ORDER BY
  total DESC
LIMIT
  25