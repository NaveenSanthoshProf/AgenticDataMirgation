# MCP Integration Guide

## Overview

Your Python MCP server is ready to serve resources to MCP-compatible clients. This guide shows how to integrate it with various platforms.

## Configuration Files

The server can be configured via `mcp.json` in your MCP client:

### VS Code / Copilot

Add to VS Code settings:

```json
{
  "modelContextProtocol": {
    "servers": {
      "knowledge-library": {
        "command": "python",
        "args": ["mcp_server.py"],
        "cwd": "/path/to/knowledge_library",
        "env": {
          "PYTHONUNBUFFERED": "1",
          "MCP_RESOURCES_PATH": "./dist"
        }
      }
    }
  }
}
```

### Claude / Claude.dev

Create `.claude/resources.json`:

```json
{
  "resources": [
    {
      "name": "knowledge-library-resources",
      "type": "mcp",
      "command": "python",
      "args": ["mcp_server.py"],
      "config": {
        "cwd": "/path/to/knowledge_library"
      }
    }
  ]
}
```

### Cline (VS Code Extension)

In Cline settings:

```json
{
  "mcpServers": [
    {
      "name": "knowledge-library",
      "command": "python",
      "args": ["mcp_server.py", "list"],
      "cwd": "/path/to/knowledge_library",
      "enabled": true
    }
  ]
}
```

## Resource Access Patterns

### Direct Python Integration

```python
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, "/path/to/knowledge_library")

from mcp_server import MCPResourceServer

# Initialize
server = MCPResourceServer()

# Get all resources
all_resources = server.list_resources()

# Access schema
schema = server.get_resource("os_schema")
print(schema["content"][:1000])  # First 1000 chars

# Access ERDs
products_erd = server.get_resource("products_erd_v0_5")
# Save to file if needed
with open("products.pdf", "wb") as f:
    import base64
    f.write(base64.b64decode(products_erd["content"]))
```

### MCP Protocol (Standardized)

Resources are exposed as MCP resources following the standard protocol:

```
mcp://knowledge-library/resource/os_schema
mcp://knowledge-library/resource/products_erd_v0_5
mcp://knowledge-library/resource/contracts_erd_v0_7
...
```

### CLI Interface

```bash
# List resources
python mcp_server.py list

# Get resource metadata
python mcp_server.py get os_schema

# Filter by category
python mcp_server.py category schema
python mcp_server.py category diagram

# Filter by format
python mcp_server.py format pdf
python mcp_server.py format md

# View index
python mcp_server.py index
```

## Common Use Cases

### 1. Browse Schema Documentation

```python
server = MCPResourceServer()
schema = server.get_resource("os_schema")

# Extract table information
lines = schema["content"].split("\n")
for i, line in enumerate(lines):
    if line.startswith("### dbo."):
        print(f"Table: {line}")
```

### 2. Find ERD by Module

```python
server = MCPResourceServer()

# Find all diagrams for a specific module
diagrams = server.list_by_category("diagram")

products = [d for d in diagrams if "products" in d["name"].lower()]
contracts = [d for d in diagrams if "contracts" in d["name"].lower()]
```

### 3. Analyze Schema Metadata

```python
server = MCPResourceServer()
schema = server.get_resource("os_schema")

metadata = schema["metadata"]
print(f"Database: {metadata['database']}")
print(f"Tables: {metadata['tables']}")
print(f"Total Columns: {metadata['totalColumns']}")
print(f"Source: {metadata['sourceType']}")
print(f"Target: {metadata['targetType']}")
```

### 4. Batch Export Resources

```python
import base64
from pathlib import Path

server = MCPResourceServer()
export_dir = Path("exported_resources")
export_dir.mkdir(exist_ok=True)

for resource in server.list_resources():
    res_data = server.get_resource(resource["id"])
    
    if res_data["format"] == "pdf":
        # Decode and save binary
        with open(export_dir / resource["name"], "wb") as f:
            f.write(base64.b64decode(res_data["content"]))
    else:
        # Save text content
        with open(export_dir / resource["name"], "w") as f:
            f.write(res_data["content"])
```

## Performance Considerations

### Caching

The server caches resource metadata in memory:

```python
server = MCPResourceServer()  # ~50ms initialization
schema = server.get_resource("os_schema")  # ~100ms (file I/O)
schemas = server.list_by_category("schema")  # O(1) lookup
```

### Large File Handling

For the 1.6 MB schema file:

```python
# Load in chunks
server = MCPResourceServer()
resource = server.get_resource("os_schema")

# Don't load entire content into memory for large files
# Instead, keep reference and read as needed
content_size = resource["fileSize"]
```

## Troubleshooting

### Connection Issues

```bash
# Test server directly
python mcp_server.py list

# Check if server is responsive
python mcp_server.py index

# View errors
python mcp_server.py get invalid_resource
```

### Missing Resources

```bash
# Rebuild and rediscover
python build.py

# Verify resources exist
ls -la knowledge_library/Source_Schema/
ls -la knowledge_library/Target_Schema/

# Check configuration
cat mcp-resources.json
```

### Import Errors

```bash
# Check Python version
python --version  # Should be 3.9+

# Install dependencies
pip install -r requirements.txt

# Verify import
python -c "from mcp_server import MCPResourceServer; print('OK')"
```

## API Reference

### MCPResourceServer Methods

```python
# Initialize
server = MCPResourceServer(config_path=None)

# List operations
server.list_resources() -> List[dict]
server.list_by_category(category: str) -> List[dict]
server.list_by_format(format_type: str) -> List[dict]

# Access operations
server.get_resource(resource_id: str) -> Optional[dict]
server.get_index() -> dict

# Configuration
server.save_config(output_path: Optional[Path])
```

## Support

For issues or questions:

1. Check [QUICKSTART.md](QUICKSTART.md) for basic usage
2. Review [README.md](README.md) for detailed documentation
3. Run `python mcp_server.py list` to verify resources
4. Check [BUILD_SUMMARY.txt](BUILD_SUMMARY.txt) for build status

## Next Steps

1. ✅ Server is built and resources are indexed
2. ✅ Configuration files are ready
3. Choose your integration method above
4. Test with `python mcp_server.py list`
5. Connect your MCP client
6. Access resources through your preferred interface
