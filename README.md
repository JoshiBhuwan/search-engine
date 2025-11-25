# Search Engine API

A FastAPI service that searches messages from an external API with in-memory caching for fast responses.

## Setup

Requirements:
- Python 3.11+

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the server:
```bash
python main.py
```

The API will be available at https://search-engine-api-lxt5.onrender.com/

## API Documentation

Interactive API docs are available at https://search-engine-api-lxt5.onrender.com/docs

### Search Endpoint

`GET /search`

Parameters:
- `query` (optional): Search query to filter messages
- `page` (optional, default: 1): Page number
- `size` (optional, default: 50): Items per page

Example:
```bash
curl "http://localhost:8000/search?q=paris&page=1&size=10"
```

Response:
```json
{
  "items": [
    {
      "id": "b1e9bb83-18be-4b90-bbb8-83b7428e8e21",
      "user_id": "cd3a350e-dbd2-408f-afa0-16a072f56d23",
      "user_name": "Sophia Al-Farsi",
      "timestamp": "2025-05-05T07:47:20.159073+00:00",
      "message": "Please book a private jet to Paris for this Friday."
    }
  ],
  "total": 42,
  "page": 1,
  "size": 10
}
```

## How It Works

The service fetches all messages from the upstream API on startup and caches them in memory. Searches are performed against the cached data, which keeps response times low.

The cache refreshes every 5 minutes.

## Design Considerations

### Alternative Approaches

At first I thought of using Redis or Elasticsearch but since this is a small dataset and I want to keep it simple I went with in-memory caching. I could have used an LRU cache here but for this example, storing the data in memory is enough.

**Current approach:**
Fetch all messages from the upstream API on startup and cache them in memory. Searches are performed against the cached data which keeps response times low.

### Reducing Latency Below 30ms

Current response times are around 50-100ms. To get below 30ms:

1. Use Redis or Elasticsearch for more efficient caching and searching
2. Add database indexes if I had direct database access
3. Use a CDN to serve from locations closer to users

Combining these strategies could reduce latency by 70-100ms, easily achieving sub-30ms response times.

## Deployment

The service includes a `render.yaml` file for deployment to Render. Push your code to GitHub, create a new web service on Render, and connect your repository.