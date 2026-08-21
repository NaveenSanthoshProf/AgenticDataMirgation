
import json
import base64
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

# Configuration
CONFIG_FILE = Path(__file__).parent / "mcp-resources.json"
RESOURCES_DIR = Path(__file__).parent / "knowledge_library"


@dataclass
class MCPResource:
    """MCP Resource definition"""
    id: str
    name: str
    description: str
    category: str
    format: str
    path: str
    metadata: dict = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "format": self.format,
            "path": self.path,
            "metadata": self.metadata or {}
        }


class MCPResourceServer:
    """Fast MCP Resource Server"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize resource server"""
        self.config_path = config_path or CONFIG_FILE
        self.base_path = RESOURCES_DIR
        self.resources = {}
        self.categories = {}
        self.index = {
            "by_category": {},
            "by_format": {},
            "by_id": {}
        }
        self._load_resources()
    
    def _load_resources(self):
        """Load resources from config"""
        if not self.config_path.exists():
            self._auto_discover()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load categories
            self.categories = config.get("categories", {})
            
            # Load resources
            for res_def in config.get("resourceDefinitions", []):
                resource = MCPResource(**res_def)
                self.resources[resource.id] = resource
                self._index_resource(resource)
        except Exception as e:
            print(f"Error loading config: {e}")
            self._auto_discover()
    
    def _auto_discover(self):
        """Auto-discover resources from file system"""
        print("Auto-discovering resources...")
        
        # Source Schema resources
        source_path = self.base_path / "Source_Schema"
        if source_path.exists():
            for file in source_path.glob("*"):
                if file.is_file():
                    self._add_resource_from_file(file, "schema")
        
        # Target Schema resources (ERDs)
        target_path = self.base_path / "Target_Schema"
        if target_path.exists():
            for file in target_path.glob("*"):
                if file.is_file():
                    self._add_resource_from_file(file, "diagram")
    
    def _add_resource_from_file(self, file_path: Path, category: str):
        """Add resource from discovered file"""
        file_name = file_path.name
        resource_id = file_path.stem.lower().replace(" ", "_").replace(".", "_")
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Determine format
        suffix = file_path.suffix.lstrip('.')
        
        # Build metadata
        metadata = {
            "fileSize": file_size,
            "lastUpdated": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # Add category-specific metadata
        if category == "schema":
            if "OS_schema" in file_name:
                metadata.update({
                    "database": "Dart_MT",
                    "sourceType": "SQL Server",
                    "targetType": "Snowflake",
                    "tables": 1393,
                    "totalColumns": 11630
                })
        elif category == "diagram":
            # Extract version and module from ERD filename
            parts = file_name.replace(".pdf", "").split(" ")
            if "ERD" in file_name:
                for i, part in enumerate(parts):
                    if part == "v" and i + 1 < len(parts):
                        metadata["version"] = parts[i + 1]
                        break
                metadata["type"] = "ERD"
                metadata["module"] = file_name.replace(" ERD", "").replace(".pdf", "")
        
        resource = MCPResource(
            id=resource_id,
            name=file_name,
            description=f"{category.title()} resource: {file_name}",
            category=category,
            format=suffix,
            path=str(file_path.relative_to(self.base_path)),
            metadata=metadata
        )
        
        self.resources[resource.id] = resource
        self._index_resource(resource)
        print(f"  ✓ {resource.id}")
    
    def _index_resource(self, resource: MCPResource):
        """Index resource for fast lookup"""
        # Index by category
        if resource.category not in self.index["by_category"]:
            self.index["by_category"][resource.category] = []
        self.index["by_category"][resource.category].append(resource.id)
        
        # Index by format
        if resource.format not in self.index["by_format"]:
            self.index["by_format"][resource.format] = []
        self.index["by_format"][resource.format].append(resource.id)
        
        # Index by ID
        self.index["by_id"][resource.id] = resource.to_dict()
    
    def get_resource(self, resource_id: str) -> Optional[dict]:
        """Get resource by ID"""
        if resource_id not in self.resources:
            return None
        
        resource = self.resources[resource_id]
        resource_path = self.base_path / resource.path
        
        if not resource_path.exists():
            return None
        
        # Read resource content
        try:
            if resource.format in ['md', 'txt', 'json', 'csv']:
                with open(resource_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(resource_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                **resource.to_dict(),
                "content": content,
                "fileSize": resource_path.stat().st_size
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_resources(self) -> list:
        """List all resources"""
        return [r.to_dict() for r in self.resources.values()]
    
    def list_by_category(self, category: str) -> list:
        """List resources by category"""
        resource_ids = self.index["by_category"].get(category, [])
        return [self.resources[rid].to_dict() for rid in resource_ids]
    
    def list_by_format(self, format_type: str) -> list:
        """List resources by format"""
        resource_ids = self.index["by_format"].get(format_type, [])
        return [self.resources[rid].to_dict() for rid in resource_ids]
    
    def get_index(self) -> dict:
        """Get full resource index"""
        return {
            "total": len(self.resources),
            "categories": list(self.index["by_category"].keys()),
            "formats": list(self.index["by_format"].keys()),
            "index": self.index
        }
    
    def save_config(self, output_path: Optional[Path] = None):
        """Save current resources to config file"""
        output_path = output_path or self.config_path
        
        config = {
            "resourceDefinitions": [r.to_dict() for r in self.resources.values()],
            "categories": self.categories or {
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
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Config saved to {output_path}")


def main():
    """CLI interface"""
    import sys
    
    server = MCPResourceServer()
    
    if len(sys.argv) < 2:
        print("MCP Resource Server")
        print("\nUsage:")
        print("  python mcp_server.py list                 - List all resources")
        print("  python mcp_server.py get <resource-id>   - Get resource content")
        print("  python mcp_server.py category <name>     - List resources by category")
        print("  python mcp_server.py format <format>     - List resources by format")
        print("  python mcp_server.py index               - Show resource index")
        print("  python mcp_server.py save                - Save config file")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        resources = server.list_resources()
        print(json.dumps(resources, indent=2))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: get <resource-id>")
            return
        resource = server.get_resource(sys.argv[2])
        if resource:
            # Don't print full content, just metadata
            result = {k: v for k, v in resource.items() if k != "content"}
            result["contentLength"] = len(resource.get("content", ""))
            print(json.dumps(result, indent=2))
        else:
            print("Resource not found")
    
    elif command == "category":
        if len(sys.argv) < 3:
            print("Usage: category <category-name>")
            return
        resources = server.list_by_category(sys.argv[2])
        print(json.dumps(resources, indent=2))
    
    elif command == "format":
        if len(sys.argv) < 3:
            print("Usage: format <format-type>")
            return
        resources = server.list_by_format(sys.argv[2])
        print(json.dumps(resources, indent=2))
    
    elif command == "index":
        index = server.get_index()
        print(json.dumps(index, indent=2))
    
    elif command == "save":
        server.save_config()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
