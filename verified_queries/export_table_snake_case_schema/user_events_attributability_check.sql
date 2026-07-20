WITH
  VisitorEventFlags AS (
    SELECT
      visitor_id,
      LOGICAL_OR(event_type = 'purchase-complete') AS has_purchase,
      LOGICAL_OR(event_type = 'add-to-cart') AS has_add_to_cart,
      LOGICAL_OR(event_type = 'detail-page-view') AS has_detail_page_view,
      LOGICAL_OR(event_type = 'search') AS has_search
    FROM
      `gcp-project-id.sample_data_export.sample_retail_user_events`
    WHERE
      event_type IN (
        'purchase-complete',
        'add-to-cart',
        'detail-page-view',
        'search'
      )
    GROUP BY
      visitor_id
  )
SELECT
  COUNTIF(
    has_purchase AND NOT (has_detail_page_view OR has_add_to_cart OR has_search)
  ) AS purchase_discontinuity_events_count,
  COUNTIF(
    has_add_to_cart AND NOT (has_detail_page_view OR has_search)
  ) AS add_to_cart_discontinuity_events_count,
  COUNT(visitor_id) AS total_events_count
FROM
  VisitorEventFlags