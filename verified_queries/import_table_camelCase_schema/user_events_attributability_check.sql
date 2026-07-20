WITH
  VisitorEventFlags AS (
    SELECT
      visitorId,
      LOGICAL_OR(eventType = 'purchase-complete') AS has_purchase,
      LOGICAL_OR(eventType = 'add-to-cart') AS has_add_to_cart,
      LOGICAL_OR(eventType = 'detail-page-view') AS has_detail_page_view,
      LOGICAL_OR(eventType = 'search') AS has_search
    FROM
      `gcp-project-id.retail_testing.sample_events`
    WHERE
      eventType IN (
        'purchase-complete',
        'add-to-cart',
        'detail-page-view',
        'search'
      )
    GROUP BY
      visitorId
  )
SELECT
  COUNTIF(
    has_purchase AND NOT (has_detail_page_view OR has_add_to_cart OR has_search)
  ) AS purchase_discontinuity_events_count,
  COUNTIF(
    has_add_to_cart AND NOT (has_detail_page_view OR has_search)
  ) AS add_to_cart_discontinuity_events_count,
  COUNT(visitorId) AS total_events_count
FROM
  VisitorEventFlags