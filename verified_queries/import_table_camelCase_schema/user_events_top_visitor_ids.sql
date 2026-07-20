SELECT
  visitorId,
  COUNT(*) AS total_events
FROM
  `gcp-project-id.retail_testing.sample_events`
GROUP BY
  visitorId
ORDER BY
  total_events DESC
LIMIT 20