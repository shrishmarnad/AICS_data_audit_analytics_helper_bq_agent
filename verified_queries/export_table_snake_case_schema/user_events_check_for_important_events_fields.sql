SELECT
  event_type,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(product_details) > 0) AS has_product_ids,
  COUNTIF(attribution_token IS NOT NULL AND attribution_token != '') AS has_attribution_token,
  COUNTIF(user_info.user_id IS NOT NULL AND user_info.user_id != '') AS has_user_id,
  COUNTIF(session_id IS NOT NULL AND session_id != '') AS has_session_id,
  COUNTIF(user_info.user_agent IS NOT NULL AND user_info.user_agent != '') AS has_user_agent,
  0 AS has_ip,
  COUNTIF(ARRAY_LENGTH(experiment_ids) > 0) AS has_exp_id
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
GROUP BY
  event_type,
  meta