SELECT
  COUNT(*) AS experiment_id_count,
  COUNT(attribution_token) AS token_count,
  experiment_ids,
  event_type
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
GROUP BY
  experiment_ids,
  event_type
ORDER BY
  experiment_id_count DESC