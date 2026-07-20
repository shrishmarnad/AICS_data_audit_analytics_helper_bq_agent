SELECT
  COUNT(*) AS total,
  ARRAY_TO_STRING(page_categories, '-') AS page_categories,
  filter
FROM
 `gcp-project-id.sample_data_export.sample_retail_user_events`
WHERE
  event_type = 'search'
  AND (
    search_query IS NULL
    OR search_query = ''
  )
  AND ARRAY_LENGTH(page_categories) > 0
GROUP BY
  page_categories,
  filter
ORDER BY
  total DESC
LIMIT
  25