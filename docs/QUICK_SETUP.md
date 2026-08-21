# ChatGPT + MCP Server Setup Guide

## Quick Answer: How to Run with ChatGPT

Your project is now ready to work with ChatGPT! Here's the simplest path:

## 🚀 3-Step Setup

### Step 1: Start the API Server

```bash
# Simple: Use the quick start script
bash start.sh

# Or: Use Python directly  
python api_server.py

# Or: Use Make
make api
```

The server starts on `http://localhost:5000` and will show:
```
📡 API Server: http://127.0.0.1:5000
🔍 OpenAPI Schema: http://127.0.0.1:5000/api/v1/schema
```

### Step 2: Make API Accessible to ChatGPT

**Option A: Use ngrok (Easiest - Free Tier)**

```bash
# Install (if needed)
brew install ngrok  # macOS
# or download from https://ngrok.com

# Expose your local server
ngrok http 5000
```

You'll get a URL like: `https://xxxxxx-xxxxxx.ngrok.io`

**Option B: Deploy to Cloud**
- Railway (Free tier available)
- Replit
- Heroku (paid)
- AWS EC2 (free tier)
- Google Cloud Run

### Step 3: Add to ChatGPT

1. Go to **ChatGPT** → **Explore** → **Create a GPT**
2. Name it: "SQL Schema Assistant"
3. Click **"Create new action"**
4. Under "Schema", paste your API URL:
   ```
   https://your-ngrok-url.ngrok.io/api/v1/schema
   ```
   Or manually add these endpoints:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "SQL Schema API",
    "version": "1.0.0"
  },
  "servers": [{
    "url": "https://your-ngrok-url.ngrok.io"
  }],
  "paths": {
    "/api/v1/resources": {
      "get": {
        "summary": "List all resources",
        "operationId": "listResources",
        "responses": {"200": {"description": "Success"}}
      }
    },
    "/api/v1/resources/{resourceId}": {
      "get": {
        "summary": "Get resource",
        "operationId": "getResource",
        "parameters": [{
          "name": "resourceId",
          "in": "path",
          "required": true,
          "schema": {"type": "string"}
        }],
        "responses": {"200": {"description": "Success"}}
      }
    },
    "/api/v1/search": {
      "get": {
        "summary": "Search",
        "operationId": "search",
        "parameters": [{
          "name": "q",
          "in": "query",
          "required": true,
          "schema": {"type": "string"}
        }],
        "responses": {"200": {"description": "Success"}}
      }
    }
  }
}
```

5. Set **Authentication** to **None (Public)**
6. Click **Save**

## ✅ Test It!

In ChatGPT, try:
- "What's in the Products ERD?"
- "List all available resources"
- "Show me the Contracts diagram"
- "Search for Assessments"
- "What tables are in the database?"

## 📡 Available API Endpoints

Once running, your API exposes:

| Endpoint | Purpose |
|----------|---------|
| `GET /` | API info & endpoint list |
| `GET /health` | Health check |
| `GET /api/v1/resources` | List all resources (10 total) |
| `GET /api/v1/resources/{id}` | Get resource metadata |
| `GET /api/v1/resources/{id}/content` | Get full content |
| `GET /api/v1/resources/category/{cat}` | Filter by category |
| `GET /api/v1/resources/format/{fmt}` | Filter by format |
| `GET /api/v1/search?q=query` | Search resources |
| `GET /api/v1/index` | Get resource index |
| `GET /api/v1/schema` | OpenAPI schema |

## 🎯 Example Queries in ChatGPT

### "What tables do we have?"
ChatGPT will:
1. Call: `GET /api/v1/resources`
2. See the OS_schema resource
3. Call: `GET /api/v1/resources/os_schema/content`
4. Search the markdown for table list
5. Return findings to you

### "Show me the Products ERD"
ChatGPT will:
1. Call: `GET /api/v1/search?q=products`
2. Find `products_erd_v0_5`
3. Get metadata showing it's a PDF
4. Retrieve and display

### "Search for Assessments resources"
ChatGPT will:
1. Call: `GET /api/v1/search?q=assessments`
2. Find all Assessments ERDs
3. List them with versions

## 🔒 Production Tips

For a production ChatGPT integration:

1. **Keep the API running** - Use a process manager:
   ```bash
   # Option 1: Screen
   screen -S mcp-api
   python api_server.py
   # Ctrl+A then D to detach
   
   # Option 2: Systemd (Linux)
   sudo systemctl start mcp-api
   
   # Option 3: Docker
   docker run -p 5000:5000 mcp-api
   ```

2. **Use HTTPS** - Deploy with TLS:
   - ngrok handles this automatically
   - Or use nginx reverse proxy
   - Or deploy to cloud provider

3. **Add Rate Limiting** (optional):
   ```bash
   pip install flask-limiter
   ```

4. **Monitor** - Check logs:
   ```bash
   tail -f api.log
   ```

## 🧪 Test Commands

Before ChatGPT, test the API locally:

```bash
# Health check
curl http://localhost:5000/health

# List resources
curl http://localhost:5000/api/v1/resources

# Get resource metadata (small, fast)
curl http://localhost:5000/api/v1/resources/os_schema

# Search
curl "http://localhost:5000/api/v1/search?q=products"

# Get full content (large, slower)
curl "http://localhost:5000/api/v1/resources/os_schema/content" | head -100
```

## 📝 Troubleshooting

### API won't start
```bash
# Check if port is in use
lsof -i :5000

# Use different port
python api_server.py 8000
```

### ChatGPT can't connect
- Verify ngrok is running: `ngrok http 5000`
- Check ngrok URL is correct
- Test with curl: `curl https://your-ngrok-url/api/v1/resources`
- Verify CORS is enabled (it is by default)

### ChatGPT action not working
- Verify OpenAPI schema is valid (use https://editor.swagger.io)
- Check authentication is set to "None"
- Ensure all endpoint paths match schema
- Look for error messages in ChatGPT

### Slow responses
- Large files (1.6 MB) take time
- Use `?content=false` for metadata only
- Cache results when possible

## 📚 File Reference

Your new files:
- `api_server.py` - Flask REST API wrapper (main file)
- `CHATGPT_INTEGRATION.md` - Detailed integration guide
- `start.sh` - Quick start script
- `requirements.txt` - Updated with Flask dependencies

Updated files:
- `Makefile` - New `make api` command
- `README.md` - Updated with API info

## 🎉 You're All Set!

You now have:
- ✅ MCP server with 10 resources indexed
- ✅ REST API that ChatGPT can call
- ✅ OpenAPI schema for integration
- ✅ Quick start guide and documentation
- ✅ Multiple deployment options

### Next Steps:
1. Start API: `python api_server.py`
2. Expose with ngrok
3. Create ChatGPT custom action
4. Ask ChatGPT about your schema!

---

**Need help?** Check:
- `CHATGPT_INTEGRATION.md` - Detailed guide
- `README.md` - Full API documentation
- Logs from `python api_server.py` for errors
