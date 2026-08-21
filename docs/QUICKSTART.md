# Quick Start Guide

## Installation & Setup

### Step 1: Build Resources
```bash
python build.py
```

This discovers all resources and generates configuration:
- ✅ 1 schema file (OS_schema.md - 1.6 MB)
- ✅ 9 ERD diagrams (50-100 KB each)
- ✅ Configuration: `mcp-resources.json`
- ✅ Artifacts: `dist/`

### Step 2: Verify Resources
```bash
# List all resources
python mcp_server.py list

# View resource index
python mcp_server.py index

# Get schemas only
python mcp_server.py category schema

# Get diagrams only
python mcp_server.py category diagram
```

## Usage Examples

### Access Schema Documentation
```bash
# Get metadata about the schema
python mcp_server.py get os_schema

# Get actual content
from mcp_server import MCPResourceServer
server = MCPResourceServer()
schema = server.get_resource("os_schema")
print(schema["content"][:500])  # First 500 chars
```

### Access ERD Diagrams
```bash
# List all diagrams
python mcp_server.py category diagram

# Get specific ERD
python mcp_server.py get products_erd_v0_5

# Get format statistics
python mcp_server.py format pdf
```

### Python Integration
```python
from mcp_server import MCPResourceServer

# Initialize server
server = MCPResourceServer()

# Get resource with content
resource = server.get_resource("os_schema")
print(f"Size: {resource['fileSize']} bytes")
print(f"Tables: {resource['metadata']['tables']}")
print(f"Columns: {resource['metadata']['totalColumns']}")

# Iterate over resources
for res in server.list_resources():
    print(f"{res['id']}: {res['name']}")

# Filter by category
schemas = server.list_by_category("schema")
diagrams = server.list_by_category("diagram")

# Filter by format
markdown = server.list_by_format("md")
pdfs = server.list_by_format("pdf")
```

## Resource Summary

| Resource | Type | Size | Status |
|----------|------|------|--------|
| OS_schema.md | Schema | 1.6 MB | ✅ |
| Products ERD v0.5 | Diagram | 82.3 KB | ✅ |
| Actions ERD v0.2 | Diagram | 73.5 KB | ✅ |
| Assessments - Assessments ERD v0.6 | Diagram | 81.5 KB | ✅ |
| Assessments - Monitoring ERD v0.3 | Diagram | 74.4 KB | ✅ |
| Assessments - Questions ERD v0.6 | Diagram | 79.0 KB | ✅ |
| Audit ERD v0.2 | Diagram | 81.8 KB | ✅ |
| Contracts ERD v0.7 | Diagram | 105.6 KB | ✅ |
| Third Party ERD v0.5 | Diagram | 106.4 KB | ✅ |
| User ERD | Diagram | 54.3 KB | ✅ |

## Key Features

✅ **10 Total Resources** - 1 schema + 9 diagrams  
✅ **1.5+ MB Combined** - Comprehensive documentation  
✅ **2 Categories** - Schemas and Diagrams  
✅ **2 Formats** - Markdown and PDF  
✅ **Fast Lookup** - O(1) access via indexed IDs  
✅ **Auto-Discovery** - Automatically finds resources on build  

## Directory Structure

```
knowledge_library/
├── Source_Schema/                 # Source database schemas
│   ├── OS_schema.csv             # Original CSV export
│   └── OS_schema.md              # Converted markdown documentation
│
├── Target_Schema/                 # Target database diagrams
│   ├── Products ERD v0.5.pdf
│   ├── Actions ERD v0.2.pdf
│   ├── Assessments - Assessments ERD v0.6.pdf
│   ├── Assessments - Monitoring ERD v0.3.pdf
│   ├── Assessments - Questions ERD v0.6.pdf
│   ├── Audit ERD v0.2.pdf
│   ├── Contracts ERD v0.7.pdf
│   ├── Third Party ERD v0.5.pdf
│   └── User ERD.pdf
│
mcp_server.py                      # Main MCP server
build.py                           # Build/discovery script
mcp-resources.json                 # Resource configuration
dist/
├── index.json                     # Lookup index
└── manifest.json                  # Build manifest
```

## Troubleshooting

### Issue: Resource not found
```bash
# Rebuild to rediscover
python build.py

# Verify file exists
ls -la knowledge_library/Source_Schema/
ls -la knowledge_library/Target_Schema/
```

### Issue: Configuration outdated
```bash
# Delete and rebuild
rm mcp-resources.json
python build.py
```

### Issue: Import errors
```bash
# Check Python version (3.9+)
python --version

# Install dependencies
pip install -r requirements.txt
```

## Next Steps

1. ✅ Resources built and indexed
2. ✅ Configuration generated
3. Now integrate with MCP clients:
   - VS Code
   - Claude
   - Cline
   - Other MCP-compatible tools

See README.md for integration examples.
