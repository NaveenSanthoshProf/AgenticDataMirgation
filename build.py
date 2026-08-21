#!/usr/bin/env python3


import json
import sys
from pathlib import Path
from datetime import datetime
from mcp_server import MCPResourceServer


def build():
    """Build MCP resources"""
    print("=" * 60)
    print("Building SQL to Snowflake MCP Server")
    print("=" * 60)
    print()
    
    # Initialize server with auto-discovery
    print("🔍 Discovering resources...")
    server = MCPResourceServer()
    
    resources = server.list_resources()
    print(f"\n📦 Found {len(resources)} resources:\n")
    
    # Display resources by category
    by_category = {}
    for resource in resources:
        category = resource["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(resource)
    
    for category, items in sorted(by_category.items()):
        print(f"  📂 {category.upper()} ({len(items)})")
        for item in items:
            size = item.get("metadata", {}).get("fileSize", 0)
            if size:
                size_str = format_bytes(size)
            else:
                size_str = "?"
            print(f"    ✓ {item['id']:<40} {size_str:>15}")
    
    # Validate all resources
    print("\n✓ Validating resources...")
    base_path = Path(__file__).parent / "knowledge_library"
    valid = 0
    missing = 0
    
    for resource in resources:
        resource_path = base_path / resource["path"]
        if resource_path.exists():
            valid += 1
        else:
            print(f"  ⚠️  Missing: {resource['path']}")
            missing += 1
    
    # Generate configuration
    print("\n✓ Generating configuration...")
    config_path = Path(__file__).parent / "mcp-resources.json"
    server.save_config(config_path)
    
    # Create build artifacts
    print("\n✓ Creating build artifacts...")
    build_dir = Path(__file__).parent / "dist"
    build_dir.mkdir(exist_ok=True)
    
    # Save index
    index = server.get_index()
    index_path = build_dir / "index.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    print(f"  - {index_path.name}")
    
    # Save manifest
    manifest = {
        "name": "knowledge-library",
        "version": "1.0.0",
        "build_date": datetime.now().isoformat(),
        "total_resources": len(resources),
        "valid_resources": valid,
        "missing_resources": missing,
        "resources": resources
    }
    manifest_path = build_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  - {manifest_path.name}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ Build Complete!")
    print("=" * 60)
    print(f"Total resources: {len(resources)}")
    print(f"Valid: {valid}")
    if missing > 0:
        print(f"Missing: {missing}")
    print(f"Config: {config_path}")
    print(f"Artifacts: {build_dir}/")
    print()


def format_bytes(bytes_val):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"❌ Build failed: {e}", file=sys.stderr)
        sys.exit(1)
