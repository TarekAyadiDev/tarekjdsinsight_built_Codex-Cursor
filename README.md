# Journey Insights API

FastAPI service that accepts a list of journey events and returns raw analytics (summary, steps, graph). Intended for internal/demo use and to be called from a Vercel frontend or Postman. No authentication yet; AI-generated insights will be added later via extra endpoints.

## Endpoint

- URL: `/journey-insights`
- Method: `POST`
- Content-Type: `application/json`

### Example request

```json
{
  "events": [
    {
      "id": "evt-1",
      "time": "2025-10-23T17:08:54Z",
      "uiData": {
        "title": "💳 Payment Received",
        "subTitle": "Payment Details",
        "filterTags": ["Payments", "demo"],
        "iconType": "Payment"
      },
      "data": {
        "🧠 Sentiment": "neutral",
        "📱 Channel": "WhatsApp"
      }
    }
  ]
}
```

### Example response

```json
{
  "base": {
    "summary": {
      "totalInteractions": 5,
      "channelsUsed": ["Voice", "WhatsApp", "Online Store"],
      "firstContact": "2025-09-26T15:20:00+00:00",
      "lastContact": "2025-10-23T17:08:54+00:00"
    },
    "steps": [
      {
        "id": "evt-1",
        "label": "💳 Payment Received",
        "subtitle": "Payment Details",
        "channel": "WhatsApp",
        "time": "2025-10-23T17:08:54+00:00",
        "category": "Payment",
        "sentiment": "neutral"
      }
    ],
    "graph": {
      "nodes": [
        { "id": "Payment", "label": "Payment", "count": 1 }
      ],
      "edges": []
    }
  }
}
```

## Notes

- No authentication yet (internal/demo use).
- Provides only raw analytics (summary, steps, graph); AI integrations will be added later via additional endpoints.
