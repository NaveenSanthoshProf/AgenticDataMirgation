# SQL to Snowflake MCP Server 🚀

A fast, lightweight Python MCP (Model Context Protocol) server for exposing SQL Server to Snowflake migration resources including schema documentation and Entity Relationship Diagrams (ERDs).

## Three-Layer Integration Stack

```
┌─────────────────────────────────────────────────────┐
│  Layer 3: AI Integrations                            │
│  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │ ChatGPT Custom   │  │ Claude Tool Use          │ │
│  │ Actions          │  │ (claude_client.py)       │ │
│  └────────┬─────────┘  └──────────┬───────────────┘ │
└───────────┼──────────────────────────┼──────────────┘
            │ OpenAPI Schema           │ Tool Use
            ▼                          ▼
┌─────────────────────────────────────────────────────┐
│  Layer 2: REST API Server (api_server.py)           │
│  - 10 HTTP endpoints                                │
│  - OpenAPI 3.0 schema generation                    │
│  - CORS support for ChatGPT                         │
│  - Response formatting & caching                    │
└──────────────────────┬──────────────────────────────┘
                       │ REST Requests
                       ▼
┌─────────────────────────────────────────────────────┐
│  Layer 1: MCP Server Core (mcp_server.py)           │
│  - Auto-discovery of 10 resources                   │
│  - Indexed lookups (O(1) performance)               │
│  - Configuration management                        │
│  - File handling (MD, PDF)                          │
└─────────────────────────────────────────────────────┘
```

## Features

✨ **Fast Resource Access**
- Auto-discovery of resources from filesystem
- Indexed lookup for O(1) resource retrieval
- Support for multiple formats (Markdown, PDF, CSV, JSON)

📦 **Resource Types**
- **Schema Documentation**: SQL Server schema in semantic markdown format
- **ERD Diagrams**: Module-level entity relationship diagrams

🔧 **Easy Configuration**
- Auto-generates configuration from discovered resources
- JSON-based resource definitions
- Metadata support for rich resource information

🌐 **Multi-AI Integration**
- **ChatGPT**: Custom Actions with OpenAPI schema
- **Claude**: Direct tool use via Python client
- **Any OpenAPI client**: Generic REST API support

## Quick Start

### Installation

```bash
# Clone/setup project
cd sql2snowflakeMapper

# Install dependencies
pip install -r requirements.txt
```

### Build

```bash
# Auto-discover resources and generate configuration
python build.py
```

This will:
- ✓ Scan Source_Schema/ and Target_Schema/ directories
- ✓ Generate mcp-resources.json
- ✓ Create dist/index.json and dist/manifest.json
- ✓ Validate all resources

### Usage

#### List all resources
```bash
python mcp_server.py list
```

#### Get a specific resource
```bash
python mcp_server.py get os_schema_md
```

#### List by category
```bash
python mcp_server.py category schema
python mcp_server.py category diagram
```

#### List by format
```bash
python mcp_server.py format md
python mcp_server.py format pdf
```

#### View resource index
```bash
python mcp_server.py index
```

#### Save configuration
```bash
python mcp_server.py save
```

## Resource Structure

### Source Schema (sql2snowflakeMapper/Source_Schema/)

- **OS_schema.csv** - Complete SQL Server database schema export
- **OS_schema.md** - Semantic markdown documentation (auto-generated)
  - 1,393 tables
  - 11,630 columns
  - Full data type specifications
  - Nullable constraints
  - Collation information

### Target Schema (sql2snowflakeMapper/Target_Schema/)

Entity Relationship Diagrams (ERDs) for:
- Products (v0.5)
- Actions (v0.2)
- Assessments - Assessments (v0.6)
- Assessments - Monitoring (v0.3)
- Assessments - Questions (v0.6)
- Audit (v0.2)
- Contracts (v0.7)
- Third Party (v0.5)
- User

## Configuration

The server loads resource definitions from `mcp-resources.json`:

```json
{
  "resourceDefinitions": [
    {
      "id": "os_schema_md",
      "name": "OS_schema.md",
      "description": "SQL Server database schema in semantic markdown",
      "category": "schema",
      "format": "md",
      "path": "Source_Schema/OS_schema.md",
      "metadata": {
        "database": "Dart_MT",
        "tables": 1393,
        "totalColumns": 11630,
        "sourceType": "SQL Server",
        "targetType": "Snowflake"
      }
    }
  ],
  "categories": {
    "schema": {
      "name": "Database Schemas",
      "description": "SQL Server database schema documentation"
    },
    "diagram": {
      "name": "Entity Relationship Diagrams",
      "description": "ERD diagrams for database modules"
    }
  }
}
```

## Build Artifacts

After building, `dist/` contains:

- **index.json** - Fast lookup index by category, format, and ID
- **manifest.json** - Build manifest with resource metadata
- **mcp-resources.json** - Full resource configuration (in root)

## API Reference

### MCPResourceServer

```python
from mcp_server import MCPResourceServer

# Initialize
server = MCPResourceServer()

# List all resources
resources = server.list_resources()

# Get resource by ID
resource = server.get_resource("os_schema_md")

# List by category
schemas = server.list_by_category("schema")

# List by format
pdfs = server.list_by_format("pdf")

# Get full index
index = server.get_index()

# Save configuration
server.save_config("path/to/config.json")
```

## Integration with MCP Clients

### Configure in your MCP client

For VS Code, Cline, or other MCP-compatible tools:

```json
{
  "mcpServers": {
    "sql2snowflake": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## REST API Server (Layer 2)

### Quick Start

```bash
# Start the API server
python api_server.py

# OR with custom port
python api_server.py 8000
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API info and documentation |
| `/health` | GET | Health check |
| `/api/v1/resources` | GET | List all resources |
| `/api/v1/resources/{id}` | GET | Get resource metadata |
| `/api/v1/resources/{id}/content` | GET | Get full content |
| `/api/v1/search` | GET | Search resources |
| `/api/v1/resources/category/{cat}` | GET | Filter by category |
| `/api/v1/resources/format/{fmt}` | GET | Filter by format |
| `/api/v1/index` | GET | Get lookup index |
| `/api/v1/schema` | GET | Get OpenAPI specification |

### Example API Calls

```bash
# List all resources
curl http://localhost:5000/api/v1/resources

# Search for a resource
curl "http://localhost:5000/api/v1/search?q=products"

# Get resource metadata
curl "http://localhost:5000/api/v1/resources/os_schema"

# Get resource content
curl "http://localhost:5000/api/v1/resources/os_schema?content=true"

# Get OpenAPI schema for ChatGPT integration
curl http://localhost:5000/api/v1/schema
```

## ChatGPT Integration (Layer 3a)

### Quick Start

1. **Start API Server**
   ```bash
   python api_server.py
   ```

2. **Expose to Internet**
   ```bash
   ngrok http 5000
   # Get URL: https://xxxxx.ngrok.io
   ```

3. **Create Custom GPT**
   - Go to ChatGPT → Explore → Create a GPT
   - Create new action
   - Paste OpenAPI schema URL: `https://xxxxx.ngrok.io/api/v1/schema`
   - Set Authentication: None

4. **Chat with Your Database**
   ```
   "What tables are in the database?"
   "Show me the Products ERD"
   "Search for assessments schemas"
   ```

For detailed setup, see [CHATGPT_INTEGRATION.md](CHATGPT_INTEGRATION.md)

## Claude Integration (Layer 3b)

### Quick Start

1. **Set API Key**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

2. **Start API Server** (Terminal 1)
   ```bash
   python api_server.py
   ```

3. **Run Claude Client** (Terminal 2)
   ```bash
   python claude_client.py
   ```

4. **Chat Interactively**
   ```
   💬 You: What resources are available?
   
   🔧 Claude uses tools to query your API
   
   🤖 Claude: Based on your database...
   ```

### Command Line Usage

```bash
# Interactive chat
python claude_client.py

# Single question
python claude_client.py -q "What tables are in the database?"

# Verbose output (see tool calls)
python claude_client.py -v

# Custom API URL
python claude_client.py --api-url "http://example.com:5000"
```

For detailed setup, see [CLAUDE_SETUP.md](CLAUDE_SETUP.md)

## Make Commands

```bash
# Installation & Build
make install                    # Install dependencies
make build                      # Build and discover resources

# Resource Queries (CLI)
make list                       # List all resources
make get RESOURCE=os_schema     # Get specific resource
make category CATEGORY=schema   # List by category

# REST API
make api                        # Start API server (port 5000)
make api-port PORT=8000         # Start on custom port

# ChatGPT Integration
make start                       # Start with auto-build

# Claude Integration
make claude                      # Interactive Claude chat
make claude-q Q="Your question"  # Ask Claude a single question
make claude-v                    # Claude chat with verbose output

# Development
make dev                        # Development mode
make clean                      # Clean artifacts
```

## File Structure

```
sql2snowflakeMapper/
├── Source_Schema/
│   ├── OS_schema.csv          # Original SQL Server schema export
│   └── OS_schema.md           # Semantic markdown documentation
├── Target_Schema/
│   ├── Actions ERD v0.2.pdf
│   ├── Assessments - Assessments ERD v0.6.pdf
│   ├── ... (other ERDs)
│   └── User ERD.pdf
├── mcp_server.py              # Main server implementation
├── build.py                   # Build/discovery script
├── mcp-resources.json         # Resource configuration
├── pyproject.toml             # Python project config
├── requirements.txt           # Python dependencies
└── dist/                      # Build artifacts
    ├── index.json
    └── manifest.json
```

## Performance

- **Resource Discovery**: O(n) on first run, cached thereafter
- **Resource Lookup**: O(1) via indexed access
- **File Serving**: Direct file system access with caching

### Resource Sizes

- OS_schema.md: ~1.6 MB
- ERD PDFs: 50-100 KB each
- Total: ~5-6 MB

## Development

### Adding a New Resource

1. Place file in appropriate directory:
   - Schemas → `Source_Schema/`
   - Diagrams → `Target_Schema/`

2. Run build to auto-discover:
   ```bash
   python build.py
   ```

3. Verify in configuration:
   ```bash
   python mcp_server.py list
   ```

### Extending Resource Types

Edit `MCPResourceServer._add_resource_from_file()` to add custom metadata handling for new resource types.

## Troubleshooting

### Resource not found
- Check file exists in correct directory
- Run `python build.py` to regenerate configuration
- Verify path in mcp-resources.json

### Import errors
- Ensure Python 3.9+
- Check dependencies: `pip install -r requirements.txt`

### Configuration issues
- Delete `mcp-resources.json` to force regeneration
- Run `python build.py` to rebuild

## License

MIT

## Contributing

Contributions welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
