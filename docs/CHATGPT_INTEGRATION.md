# ChatGPT Integration Guide

## Overview

You can now expose your MCP server as a REST API that ChatGPT can call via Custom Actions. This allows ChatGPT to access your SQL Server schema documentation and ERD diagrams directly.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This adds Flask and Flask-CORS for API serving.

### 2. Start the API Server

```bash
# Run on default (127.0.0.1:5000)
python api_server.py

# Run on custom port
python api_server.py 8000

# Run on custom host and port
python api_server.py 8000 0.0.0.0
```

You should see:
```
╔════════════════════════════════════════════════════════╗
║   SQL to Snowflake MCP Server - REST API              ║
╚════════════════════════════════════════════════════════╝

📡 API Server: http://127.0.0.1:5000
🔍 OpenAPI Schema: http://127.0.0.1:5000/api/v1/schema
📚 Documentation: http://127.0.0.1:5000
```

### 3. Test the API

```bash
# List all resources
curl http://localhost:5000/api/v1/resources

# Get resource index
curl http://localhost:5000/api/v1/index

# Search for a resource
curl "http://localhost:5000/api/v1/search?q=schema"

# Get resource metadata
curl "http://localhost:5000/api/v1/resources/os_schema"

# Get resource content (with content query param)
curl "http://localhost:5000/api/v1/resources/os_schema?content=true"
```

## ChatGPT Custom Actions Setup

### Step 1: Make API Publicly Accessible

For ChatGPT to access your API, it needs to be accessible from the internet. Options:

**Option A: Use ngrok (Easy)**
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Expose your local server
ngrok http 5000
# Output: Forwarding https://xxxxx.ngrok.io -> http://localhost:5000
```

**Option B: Deploy to Cloud**
- AWS EC2, Google Cloud Run, Heroku, Railway, etc.
- Ensure CORS is enabled (already done in api_server.py)

### Step 2: Create Custom GPT in ChatGPT

1. Go to [ChatGPT](https://chat.openai.com)
2. Click "Explore" → "Create a GPT"
3. Name: "SQL Schema Assistant"
4. Description: "Access SQL Server schema and ERD diagrams"

### Step 3: Add Custom Action

In the GPT builder:

1. Click "Create new action"
2. Fill in the OpenAPI Schema:

**Manual approach:**

Copy the entire content from `/api/v1/schema` endpoint and paste into the "Imported Schema" section, OR:

**Use the hosted schema (easier):**

1. In "Authentication", select "None (Public)"
2. In "Schema", paste this URL (replace with your actual URL):

```
https://xxxxx.ngrok.io/api/v1/schema
```

Or manually configure:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "SQL to Snowflake MCP Resources",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-api-url.com"
    }
  ],
  "paths": {
    "/api/v1/resources": {
      "get": {
        "summary": "List all resources",
        "operationId": "listResources",
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/v1/resources/{resourceId}": {
      "get": {
        "summary": "Get resource details",
        "operationId": "getResource",
        "parameters": [
          {
            "name": "resourceId",
            "in": "path",
            "required": true,
            "schema": {"type": "string"}
          }
        ],
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/v1/resources/{resourceId}/content": {
      "get": {
        "summary": "Get resource content",
        "operationId": "getResourceContent",
        "parameters": [
          {
            "name": "resourceId",
            "in": "path",
            "required": true,
            "schema": {"type": "string"}
          }
        ],
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/api/v1/search": {
      "get": {
        "summary": "Search resources",
        "operationId": "searchResources",
        "parameters": [
          {
            "name": "q",
            "in": "query",
            "required": true,
            "schema": {"type": "string"}
          }
        ],
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    }
  }
}
```

### Step 4: Instructions for the GPT

Add these instructions to your Custom GPT:

```
You have access to a SQL Server schema database containing:
- Complete database schema documentation (1,393 tables, 11,630 columns)
- 9 Entity Relationship Diagrams for different modules

Available actions:
1. List all resources - see what's available
2. Search resources - find schemas or diagrams by name
3. Get resource details - view metadata and summary
4. Get resource content - retrieve full documentation or diagrams

When users ask about the database structure, schema, or module diagrams:
1. First search or list available resources
2. Get the resource details to show metadata
3. For full content, retrieve and present the information

Be helpful in explaining schema relationships and ERD diagrams.
```

### Step 5: Test with ChatGPT

Try these prompts:

```
"What tables are in the database?"
"Show me the Contracts ERD"
"Find all resources with 'Assessments' in the name"
"What columns are in the Products schema?"
"List all ERD diagrams available"
```

## API Endpoints Reference

### List Resources
```
GET /api/v1/resources
```
Returns all 10 resources with metadata.

### Get Resource Metadata
```
GET /api/v1/resources/{resource_id}
GET /api/v1/resources/os_schema
```
Returns resource details (without large content by default).

### Get Full Resource Content
```
GET /api/v1/resources/{resource_id}/content
GET /api/v1/resources/os_schema/content
```
Returns complete resource content (markdown, PDF as base64, etc).

### Get with Content (Alternative)
```
GET /api/v1/resources/{resource_id}?content=true
```
Includes content in the response.

### Filter by Category
```
GET /api/v1/resources/category/schema
GET /api/v1/resources/category/diagram
```

### Filter by Format
```
GET /api/v1/resources/format/md
GET /api/v1/resources/format/pdf
```

### Search
```
GET /api/v1/search?q=products
GET /api/v1/search?q=erd
```

### Get Index
```
GET /api/v1/index
```
Fast lookup of all resources by category/format/ID.

### OpenAPI Schema
```
GET /api/v1/schema
```
Full OpenAPI specification for integration.

## Environment Variables

```bash
API_HOST=127.0.0.1      # Listen address
API_PORT=5000           # Port number
API_DEBUG=False         # Debug mode
```

Or create `.env`:
```
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False
```

## Running in Background

### Using nohup
```bash
nohup python api_server.py &
```

### Using screen
```bash
screen -S mcp-api
python api_server.py
# Press Ctrl+A then D to detach
# screen -r mcp-api to reattach
```

### Using systemd (Linux)
Create `/etc/systemd/system/mcp-api.service`:
```ini
[Unit]
Description=SQL to Snowflake MCP API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 api_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl start mcp-api
sudo systemctl enable mcp-api
sudo systemctl status mcp-api
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app

# With worker processes
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 api_server:app
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

Build and run:
```bash
docker build -t mcp-api .
docker run -p 5000:5000 mcp-api
```

## Security Considerations

### For Production:

1. **Add Authentication**
```python
from flask_httpauth import HTTPBearerAuth
auth = HTTPBearerAuth()

@app.before_request
@auth.login_required
def protected():
    return True
```

2. **Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app)

@app.route('/api/v1/resources')
@limiter.limit("100 per hour")
def list_resources():
    ...
```

3. **HTTPS/TLS**
- Use ngrok: automatically handles HTTPS
- Deploy with SSL certificate (Let's Encrypt)
- Use reverse proxy (nginx)

4. **CORS Control**
Currently allows all origins. For production:
```python
CORS(app, resources={
    "/api/v1/*": {
        "origins": ["https://chat.openai.com"],
        "methods": ["GET"],
    }
})
```

## Troubleshooting

### API not accessible from ChatGPT
- Ensure server is running: `curl http://localhost:5000`
- Check ngrok is active: `ngrok http 5000`
- Verify URL in ChatGPT action matches ngrok URL
- Check firewall/network settings

### CORS errors
- Verify Flask-CORS is installed
- Check error logs for specific origin

### Slow responses
- Schema files are cached in memory
- Large PDFs are encoded to base64 (slower)
- Use `content=false` by default to get metadata only

### Resource not found errors
- Rebuild if you added new files: `python build.py`
- Check resource ID matches: `python mcp_server.py list`

## Example ChatGPT Conversation

**User:** "What tables exist for Products?"

**ChatGPT:**
1. Calls: `GET /api/v1/search?q=products`
2. Gets results showing ERD and schema
3. Calls: `GET /api/v1/resources/os_schema/content`
4. Searches markdown for "Products" table
5. Returns relevant tables and their columns

**You can now:** Ask ChatGPT questions about your database structure directly!

## Claude Integration Guide

### Overview

Beyond ChatGPT, your REST API also works with **Claude** via the new Claude API tool use (function calling). This allows Claude to directly call your API endpoints.

### Layer 3: Claude API Configuration

Claude can integrate with your API in two ways:

#### Option A: Direct API Calls via Claude's Tool Use

Claude's API supports tool calling, allowing it to make HTTP requests to your API.

**Setup:**

1. **Install Claude SDK**
```bash
pip install anthropic
```

2. **Create a Claude client script** (`claude_client.py`):
```python
from anthropic import Anthropic
import requests
import json

client = Anthropic()

# Define tools for Claude to use
tools = [
    {
        "name": "list_resources",
        "description": "List all available database resources (schema and ERDs)",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "search_resources",
        "description": "Search for resources by keyword",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query term"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_resource",
        "description": "Get detailed information about a specific resource",
        "input_schema": {
            "type": "object",
            "properties": {
                "resource_id": {
                    "type": "string",
                    "description": "ID of the resource"
                },
                "include_content": {
                    "type": "boolean",
                    "description": "Include full content (default: false)"
                }
            },
            "required": ["resource_id"]
        }
    },
    {
        "name": "get_by_category",
        "description": "Get all resources in a category (schema or diagram)",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["schema", "diagram"],
                    "description": "Resource category"
                }
            },
            "required": ["category"]
        }
    }
]

def call_api(endpoint: str, params: dict = None) -> dict:
    """Call the local MCP API"""
    base_url = "http://localhost:5000"
    try:
        response = requests.get(f"{base_url}{endpoint}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process Claude's tool calls"""
    if tool_name == "list_resources":
        result = call_api("/api/v1/resources")
        return json.dumps(result)
    
    elif tool_name == "search_resources":
        result = call_api("/api/v1/search", {"q": tool_input["query"]})
        return json.dumps(result)
    
    elif tool_name == "get_resource":
        resource_id = tool_input["resource_id"]
        include = tool_input.get("include_content", False)
        endpoint = f"/api/v1/resources/{resource_id}"
        if include:
            endpoint += "?content=true"
        result = call_api(endpoint)
        return json.dumps(result)
    
    elif tool_name == "get_by_category":
        category = tool_input["category"]
        result = call_api(f"/api/v1/resources/category/{category}")
        return json.dumps(result)
    
    return json.dumps({"error": "Unknown tool"})

def chat_with_claude(user_message: str):
    """Chat with Claude, allowing it to use tools"""
    messages = [{"role": "user", "content": user_message}]
    
    print(f"\n👤 User: {user_message}\n")
    
    # Initial request to Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=tools,
        messages=messages
    )
    
    # Handle tool use in a loop
    while response.stop_reason == "tool_use":
        # Extract tool use from response
        assistant_message = {"role": "assistant", "content": response.content}
        messages.append(assistant_message)
        
        # Process each tool call
        tool_results = []
        for content in response.content:
            if content.type == "tool_use":
                print(f"🔧 Claude using tool: {content.name}")
                print(f"   Input: {json.dumps(content.input, indent=2)}")
                
                # Call the tool
                result = process_tool_call(content.name, content.input)
                print(f"   Result: {result[:200]}..." if len(result) > 200 else f"   Result: {result}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content.id,
                    "content": result
                })
        
        # Send tool results back to Claude
        messages.append({"role": "user", "content": tool_results})
        
        # Get next response from Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
    
    # Extract final text response
    final_response = ""
    for content in response.content:
        if hasattr(content, "text"):
            final_response += content.text
    
    print(f"\n🤖 Claude: {final_response}\n")
    return final_response

if __name__ == "__main__":
    # Example conversation
    chat_with_claude("What database resources do I have available?")
    chat_with_claude("Show me the Products ERD")
    chat_with_claude("Search for assessments-related schemas")
```

3. **Run Claude client**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python claude_client.py
```

#### Option B: Claude with Anthropic's Files API

For large files like the 1.6MB schema, use Anthropic's Files API:

```python
from anthropic import Anthropic
import requests

client = Anthropic()

def upload_resource_to_claude(resource_id: str):
    """Upload a resource to Claude's Files API"""
    # Fetch the resource
    response = requests.get(
        f"http://localhost:5000/api/v1/resources/{resource_id}/content"
    )
    content = response.json()["content"]
    
    # For markdown files, create temp file
    if isinstance(content, str):
        with open(f"/tmp/{resource_id}.md", "w") as f:
            f.write(content)
        
        with open(f"/tmp/{resource_id}.md", "rb") as f:
            file_response = client.beta.files.upload(
                file=(f"{resource_id}.md", f, "text/plain"),
            )
        
        return file_response.id
    
    return None

def chat_with_uploaded_file(file_id: str, message: str):
    """Chat about an uploaded file"""
    response = client.beta.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "file",
                            "file_id": file_id
                        }
                    },
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
    )
    
    return response.content[0].text

# Example usage
# file_id = upload_resource_to_claude("os_schema")
# result = chat_with_uploaded_file(file_id, "What are the main tables?")
```

### Testing Claude Integration

**Test 1: Check API is running**
```bash
python api_server.py
# Should show: API Server running at http://127.0.0.1:5000
```

**Test 2: Run Claude client**
```bash
python claude_client.py
```

**Test 3: Example prompts for Claude**
```
"What tables are in the database?"
"Show me the structure of the Products schema"
"Find all ERD diagrams available"
"Explain the Contracts module design"
"Search for assessment-related tables"
```

### Advantages of Claude Integration

✅ **Real-time tool calling** - Claude calls your API during conversation
✅ **Streaming support** - Get responses as Claude thinks
✅ **Large file handling** - Files API for massive schemas
✅ **No external service** - Runs locally with your API
✅ **Flexible** - Use Claude's latest models
✅ **Stateful** - Maintains conversation history

### API Comparison: ChatGPT vs Claude

| Feature | ChatGPT | Claude |
|---------|---------|--------|
| **Setup** | Custom GPT UI | SDK + Code |
| **Tool Calling** | Fixed schema | Dynamic function calling |
| **Large Files** | Slow (1.6MB) | Files API (optimized) |
| **Streaming** | Yes | Yes |
| **Auth** | OAuth/API Key | API Key |
| **Cost** | Per API call | Usage-based |
| **Local Integration** | External tunnel (ngrok) | Direct connection |

### Production Setup for Claude

**Via Docker:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install anthropic

COPY claude_client.py .
COPY api_server.py .
COPY mcp_server.py .

CMD ["python", "claude_client.py"]
```

**With environment variables:**
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
MCP_API_URL=http://localhost:5000
MODEL=claude-3-5-sonnet-20241022
```

### Running Both ChatGPT and Claude

You can expose your API to both services simultaneously:

```bash
# Terminal 1: Start the MCP API server
python api_server.py

# Terminal 2: Use with ChatGPT (via ngrok)
ngrok http 5000

# Terminal 3: Use with Claude (direct connection)
python claude_client.py
```

Both will call the same API endpoints at the same time!

## Next Steps

1. ✅ Start the API server
2. ✅ Test with curl commands
3. ✅ **Create Custom GPT in ChatGPT** OR
4. ✅ **Set up Claude integration** (python claude_client.py)
5. ✅ Chat with your database documentation!

Enjoy querying your schema through ChatGPT and/or Claude! 🚀
