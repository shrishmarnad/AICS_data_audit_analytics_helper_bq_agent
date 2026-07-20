### Data Source Mapping and Table Usage Rules

*   **Always use the `Catalog Product` table** for any queries regarding product metadata, inventory status, descriptions, categories, brands, price details, and custom attributes.
*   **Always use the `User Events` table** for tracking visitor behavior, analyzing site traffic, measuring user clicks, checking carts, attributing purchases, and debugging A/B test splits.
*   **When checking logical data connections (orphan/unjoined events)**, you must unnest the `productDetails` array from the User Events table and perform a `LEFT JOIN` on the unnested product ID to the Catalog table's `id` field.

---

### Field Selection and Exclusions

*   **The most important fields in the Catalog Product table are:**
    *   `id` (Product ID)
    *   `title` (Product title)
    *   `type` (Determines if the item is a `"PRIMARY"` or `"VARIANT"` SKU)
    *   `primaryProductId` (Links variants back to their parents)
    *   `availability` (Current stock status, e.g., `"IN_STOCK"`, `"OUT_OF_STOCK"`)
    *   `priceInfo.price` (The active, customer-facing price)
    *   `categories` (Hierarchical category paths, e.g., `"Nest > speakers and displays"`)
    *   `attributes` (Repeated record containing custom textual and numerical key-value pairs)
*   **The most important fields in the User Events table are:**
    *   `eventType` (The stage of the shopper journey, e.g., `"search"`, `"detail-page-view"`, `"add-to-cart"`, `"purchase-complete"`)
    *   `visitorId` (Unique session-based tracker of device history)
    *   `userInfo.userId` (Persistent login-hash for signed-in users)
    *   `eventTime` (Event timestamp in string-ISO format)
    *   `experimentIds` (Repeated string field containing target A/B test group identifiers)
    *   `attributionToken` (The unique tracking token returned by Search that links event conversions)
    *   `searchQuery` (The search query typed by the shopper)
    *   `productDetails.product.id` (The unnested product IDs the shopper interacted with)
    *   `purchaseTransaction.revenue` (Transactional transaction value)
    *   `purchaseTransaction.currency_code` (The localized currency code)
*   **Never use these fields for non-purchase calculations:**
    *   Do not use `purchaseTransaction.revenue` or `purchaseTransaction.currency_code` for any events where `eventType != 'purchase-complete'`.
*   **Field context constraints:**
    *   Never use `searchQuery` for browse-only events. For browsing/site-navigation analysis, use the `pageCategories` field where `searchQuery` is empty or null.

---

### Date Grouping and Time Filtering

*   **For any question about date grouping or date filtering**, parse and cast the string `eventTime` into a `TIMESTAMP` or `DATE` format before filtering.
*   **To trace user behavior chronologically (behavior sequences)**, order raw events by `visitorId` and then chronologically by `eventTime`.

---

### Deep Catalog Data Audit Rules

*   **Duplicate Title Check:** For queries checking catalog uniqueness, count occurrences of `title` and filter for counts greater than `1` to isolate duplicate product entries.
*   **System Attribute character limits validation:** Use these character count filters to surface metadata bugs that cause ingestion rejections:
    *   `description`: Flag any entries where the string length of `description` exceeds **5,000 Unicode characters** [P.1].
    *   `materials`: Flag any array element where string length exceeds **200 Unicode characters** [P.1].
    *   `colorInfo.colors`: Flag any array element where string length exceeds **128 Unicode characters** [P.1].
*   **Character limits validation for Custom Attributes:** For attributes residing in the nested `attributes` record, flag any text string length exceeding **256 Unicode characters** [P.1].
*   **Custom Attribute Array limit validation:** 
    *   `colorInfo.colorFamilies`: Flag any products containing more than **5 values** in the array [P.1].
    *   `sizes`: Flag any products containing more than **20 values** in the array [P.1].

---

### User Events Data Audit Rules

*   **Unjoined Events Check:** To calculate the unjoined event rate, unnest the `productDetails` array on the events table and do a `LEFT JOIN` on `catalog.id`. Calculate the unjoined rate as:
    $$\text{Unjoined Rate} = \frac{\text{Count of Events with unmatched catalog IDs}}{\text{Total Ingested Events}}$$
    Flag when this rate is **greater than 5%**.
*   **Multi-Item Basket Validation:** In purchase-complete events, do not flatten multi-item baskets into separate rows. Always group by transaction or session to verify that some purchases contain multiple unique products to teach co-purchase patterns.
*   **Real-time vs Batch Latency Check:** Flag instances where there is a lag of more than **24 hours** between the actual event time and the time of successful bulk ingestion.

---

### A/B Test Debugging Rules

*   **Lane Traffic Segments:** Because `experimentIds` is a `REPEATED` array field on the events table, you must unnest `experimentIds` (or use `EXISTS` queries) when filtering for control vs. test traffic lanes. Typical lane segments are `"CONTROL"` and `"EXPERIMENT"`.
*   **Attribution Token Match Debugging:** For click-attribution debugging, match a `detail-page-view`, `add-to-cart`, or `purchase-complete` event back to the corresponding `search` event by matching their `attributionToken` strings. Flag any instances where the logged query in the event (`searchQuery`) does not match the query of the originating Search API call that issued the matching token.
*   **Traffic Fairness / Bot Ingestion Check:** To protect against bias, aggregate the count of events grouped by `visitorId` per week. Flag any `visitorId` that exceeds **250,000 writes in a single week** as an abusive/power user.
*   **Catalog Parity Audit:** To ensure test fairness, write comparison checks between control and test catalogs to flag differences in product price (`priceInfo.price`) and inventory (`availability`) for identical product IDs.

---

### Key Metric Formulations

*   **Conversion Rate (CVR):** 
    $$\text{CVR} = \frac{\text{Distinct } \texttt{visitorId} \text{s where } \texttt{eventType} = \text{'purchase-complete'}}{\text{Distinct } \texttt{visitorId} \text{s where } \texttt{eventType} = \text{'search'}}$$
*   **Click-Through Rate (CTR):** 
    $$\text{CTR} = \frac{\text{Distinct } \texttt{visitorId} \text{s with a } \texttt{detail-page-view} \text{ linked by } \texttt{attributionToken}}{\text{Total } \texttt{eventType} = \text{'search'} \text{ events}}$$
*   **Revenue Per Visitor (RPV):** 
    $$\text{RPV} = \frac{\text{SUM}(\text{purchaseTransaction.revenue})}{\text{COUNT(DISTINCT } \texttt{visitorId}\text{)}}$$
