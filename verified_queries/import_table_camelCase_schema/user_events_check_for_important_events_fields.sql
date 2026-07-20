  SELECT
  eventType,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(productDetails) > 0) AS has_product_ids,
  COUNTIF(attributionToken IS NOT NULL AND attributionToken != '') AS has_attribution_token,
  COUNTIF(userInfo.userId IS NOT NULL AND userInfo.userId != '') AS has_user_id,
  COUNTIF(sessionId IS NOT NULL AND sessionId != '') AS has_session_id,
  COUNTIF(userInfo.userAgent IS NOT NULL AND userInfo.userAgent != '') AS has_user_agent,
  0 AS has_ip,
  COUNTIF(ARRAY_LENGTH(experimentIds) > 0) AS has_exp_id
FROM
  `gcp-project-id.retail_testing.sample_events`
GROUP BY
  eventType,
  meta