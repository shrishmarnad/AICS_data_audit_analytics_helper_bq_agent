SELECT
  COUNT(*) AS experiment_id_count,
  COUNT(attributionToken) AS token_count,
  experimentIds,
  eventType
FROM
  `gcp-project-id.retail_testing.sample_events`
GROUP BY
  experimentIds,
  eventType
ORDER BY
  experiment_id_count DESC