# Claude Integration Setup

## Quick Start

You can now use Claude to query your MCP server database via tool use!

### Prerequisites

1. **MCP API Server running**
   ```bash
   python api_server.py
   ```

2. **Anthropic API Key**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Claude SDK installed**
   ```bash
   pip install anthropic
   ```

### Step 1: Start the API Server

```bash
# Terminal 1
python api_server.py

# You should see:
# ╔════════════════════════════════════════════════════╗
# ║   SQL to Snowflake MCP Server - REST API          ║
# ╚════════════════════════════════════════════════════╝
# 📡 API Server: http://127.0.0.1:5000
```

### Step 2: Run Claude Client

```bash
# Terminal 2
python claude_client.py
```

### Step 3: Chat with Claude

```
💬 You: What tables are in the database?

🔧 Tool Call: search_resources
   ✓ Got 1

🤖 Claude: Based on the available resources, I found the OS schema...
```

## Usage Examples

### Interactive Chat (Default)
```bash
python claude_client.py

# Type your questions:
# "What resources do I have?"
# "Show me the Products ERD"
# "Search for assessments"
```

### Single Question
```bash
python claude_client.py -q "What tables are in the database?"
```

### Verbose Output
```bash
python claude_client.py -v
# Shows detailed tool call input/output
```

### Custom API URL
```bash
python claude_client.py --api-url "http://example.com:5000"
```

### Custom Claude Model
```bash
python claude_client.py --model "claude-3-opus-20240229"
```

## Combining Options

```bash
# Single question with verbose output
python claude_client.py -q "List all resources" -v

# Interactive with custom API
python claude_client.py --api-url "https://api.example.com" -v
```

## Environment Variables

```bash
# Set API URL
export MCP_API_URL="http://localhost:5000"

# Set Claude Model
export CLAUDE_MODEL="claude-3-5-sonnet-20241022"

# Set API Key
export ANTHROPIC_API_KEY="sk-ant-..."

# Then run
python claude_client.py
```

## Example Questions for Claude

Claude can help you with your database schema in natural language:

### Schema Exploration
- "What tables are in the database?"
- "Show me the structure of the Products schema"
- "List all available resources"
- "What columns exist in the audit tables?"

### Module Queries
- "Explain the Contracts module"
- "Show me the Products ERD diagram"
- "Find assessments-related schemas"
- "What's the Third Party module?"

### Resource Discovery
- "Find all ERD diagrams"
- "Show me all markdown resources"
- "List schema-related resources"
- "Search for assessment-related content"

### Complex Questions
- "What's the difference between these two modules?"
- "How do the Contracts and Third Party modules relate?"
- "Which tables store user information?"
- "Show me all the diagrams for assessments"

## API Tools Available to Claude

Claude automatically has access to these tools:

| Tool | Purpose |
|------|---------|
| `list_resources` | See all 10 resources (schema + ERDs) |
| `search_resources` | Search by keyword |
| `get_resource` | Get detailed resource info |
| `get_by_category` | Filter by schema/diagram |
| `get_by_format` | Filter by markdown/PDF |
| `get_index` | Get fast resource lookup index |

## Architecture: Three-Layer Integration

```
┌─────────────────────────────────────────────────────┐
│  Layer 3: Claude Integration Client                 │
│  (claude_client.py)                                 │
│  - Interactive chat interface                       │
│  - Tool orchestration                               │
│  - Streaming responses                              │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────────────────┐
│  Layer 2: REST API Server                           │
│  (api_server.py + Flask)                            │
│  - 10 HTTP endpoints                                │
│  - OpenAPI schema generation                        │
│  - CORS support                                     │
│  - Response formatting                              │
└──────────────────┬──────────────────────────────────┘
                   │ Object Requests
                   ▼
┌─────────────────────────────────────────────────────┐
│  Layer 1: MCP Server Core                           │
│  (mcp_server.py)                                    │
│  - Auto-discovery of resources                      │
│  - Indexed lookups (O(1))                           │
│  - File management                                  │
│  - Configuration management                         │
└─────────────────────────────────────────────────────┘
```

## Error Handling

### API Connection Issues

```bash
# Error: Cannot connect to MCP API
# Solution: Make sure API server is running
python api_server.py

# Check API is accessible
curl http://localhost:5000/health
```

### Authentication Issues

```bash
# Error: 401 Unauthorized
# Solution: Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify key
echo $ANTHROPIC_API_KEY
```

### Timeout Issues

```bash
# For large files, requests might timeout
# Solution: Use smaller queries or include_content=false

# This is automatic in claude_client.py - it defaults to
# metadata-only responses for faster results
```

## Performance Tips

1. **Use search first** - Narrow down resources before fetching content
   ```
   "Search for products tables, then show me details"
   ```

2. **Metadata before content** - Get info first, content later
   ```
   "Show me what resources have 'assessments' in the name, then get the products ERD"
   ```

3. **Category filters** - Use categories for faster lookups
   ```
   "Show me all diagrams" (faster than searching all resources)
   ```

4. **Ask Claude to summarize** - Let Claude handle large responses
   ```
   "Search for all tables and summarize their categories"
   ```

## Production Deployment

### Docker Setup

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install anthropic

# Copy application
COPY mcp_server.py .
COPY api_server.py .
COPY claude_client.py .
COPY Source_Schema/ Source_Schema/
COPY Target_Schema/ Target_Schema/

# API server on port 5000
EXPOSE 5000

# Default to interactive Claude client
ENTRYPOINT ["python", "claude_client.py"]
```

Build and run:
```bash
docker build -t mcp-claude .
docker run -e ANTHROPIC_API_KEY="sk-ant-..." mcp-claude
```

### Systemd Service (Linux)

Create `/etc/systemd/system/mcp-api.service`:
```ini
[Unit]
Description=MCP API Server
After=network.target

[Service]
Type=simple
User=nobody
WorkingDirectory=/opt/mcp-server
ExecStart=/usr/bin/python3 /opt/mcp-server/api_server.py
Restart=on-failure
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mcp-api
sudo systemctl start mcp-api
sudo systemctl status mcp-api
```

### Environment Configuration

Create `.env` file:
```
# API Configuration
MCP_API_URL=http://localhost:5000
API_HOST=0.0.0.0
API_PORT=5000

# Claude Configuration
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Optional
DEBUG=False
TIMEOUT=30
```

Load before running:
```bash
set -a && source .env && set +a
python claude_client.py
```

## Integration with Other Tools

### Use with LangChain

```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatAnthropic
import requests

def call_mcp_api(query):
    """Wrapper for MCP API"""
    response = requests.get(
        "http://localhost:5000/api/v1/search",
        params={"q": query}
    )
    return response.json()

tools = [
    Tool(
        name="search_schema",
        func=call_mcp_api,
        description="Search database schema and resources"
    )
]

agent = initialize_agent(
    tools,
    ChatAnthropic(model_name="claude-3-5-sonnet-20241022"),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("What tables are available?")
```

### Use with FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(message: str):
    """Expose Claude integration as HTTP endpoint"""
    process = subprocess.Popen(
        ["python", "claude_client.py", "-q", message],
        stdout=subprocess.PIPE
    )
    return StreamingResponse(process.stdout)
```

## Troubleshooting

### Claude doesn't find resources

```bash
# Solution 1: Verify API is running
curl http://localhost:5000/api/v1/resources

# Solution 2: Rebuild resource index
python build.py

# Solution 3: Check API logs for errors
python api_server.py -v
```

### Timeouts on large files

```bash
# Solution: Set longer timeout in claude_client.py
requests.get(url, timeout=60)  # Increase from 30

# Or ask Claude to work with summaries instead of full content
```

### Claude gives incorrect responses

```bash
# Solution 1: Ask Claude to list resources first
"Show me all available resources, then answer my question"

# Solution 2: Use search to narrow down
"Search for X, then describe what you found"

# Solution 3: Use verbose mode to debug
python claude_client.py -v
```

## Advanced Usage

### Custom Tool Definitions

Edit `claude_client.py` to add more tools that call your API:

```python
TOOLS = [
    # ... existing tools ...
    {
        "name": "get_resource_stats",
        "description": "Get statistics about a resource",
        "input_schema": {
            "type": "object",
            "properties": {
                "resource_id": {"type": "string"}
            },
            "required": ["resource_id"]
        }
    }
]

def process_tool_call(tool_name, tool_input):
    # ... existing code ...
    elif tool_name == "get_resource_stats":
        # Implement custom logic
        return json.dumps({"tables": 1393, "columns": 11630})
```

### Batch Processing

```python
# Process multiple questions
questions = [
    "What resources are available?",
    "Show me the Products ERD",
    "Search for assessments"
]

for q in questions:
    print(f"\nQuestion: {q}")
    chat_with_claude(q, verbose=False)
```

### Streaming Responses

```python
# Use streaming for real-time responses
response = client.messages.stream(
    model=CLAUDE_MODEL,
    max_tokens=4096,
    tools=TOOLS,
    messages=messages
)

for text in response.text_stream:
    print(text, end="", flush=True)
```

## Support & Next Steps

1. **For ChatGPT integration** - See CHATGPT_INTEGRATION.md
2. **For API documentation** - See README.md
3. **For MCP details** - See MCP_INTEGRATION.md
4. **For quick start** - See QUICK_SETUP.md

## Resources

- [Anthropic API Docs](https://docs.anthropic.com)
- [Claude Models](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [MCP Specification](https://spec.modelcontextprotocol.io)

---

**Enjoy querying your database with Claude!** 🚀
