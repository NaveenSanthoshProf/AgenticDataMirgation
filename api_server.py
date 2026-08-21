#!/usr/bin/env python3
"""
OpenAPI/REST wrapper for MCP Server
Exposes resources via HTTP endpoints compatible with ChatGPT Actions
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from mcp_server import MCPResourceServer
import os

app = Flask(__name__)
CORS(app)

# Initialize MCP server
server = MCPResourceServer()

# API Information
API_INFO = {
    "title": "SQL to Snowflake MCP Server API",
    "version": "1.0.0",
    "description": "Access SQL Server schema documentation and ERD diagrams",
    "contact": {
        "name": "API Support"
    }
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "resources_count": len(server.list_resources()),
        "categories": list(server.get_index()["categories"])
    })


@app.route('/api/v1/resources', methods=['GET'])
def list_resources():
    """List all available resources"""
    resources = server.list_resources()
    return jsonify({
        "success": True,
        "count": len(resources),
        "resources": resources
    })


@app.route('/api/v1/resources/<resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get specific resource by ID"""
    # Check if we should include content
    include_content = request.args.get('content', 'false').lower() == 'true'
    
    resource = server.get_resource(resource_id)
    
    if not resource:
        return jsonify({
            "success": False,
            "error": f"Resource not found: {resource_id}"
        }), 404
    
    # Remove content if not requested (for performance)
    response = dict(resource)
    if not include_content and "content" in response:
        del response["content"]
        response["content_available"] = True
        response["content_size"] = resource.get("fileSize", 0)
    
    return jsonify({
        "success": True,
        "resource": response
    })


@app.route('/api/v1/resources/<resource_id>/content', methods=['GET'])
def get_resource_content(resource_id):
    """Get resource content directly"""
    resource = server.get_resource(resource_id)
    
    if not resource:
        return jsonify({
            "success": False,
            "error": f"Resource not found: {resource_id}"
        }), 404
    
    content = resource.get("content", "")
    
    # For text files, return as JSON
    if resource["format"] in ["md", "txt", "json", "csv"]:
        return jsonify({
            "success": True,
            "id": resource_id,
            "name": resource["name"],
            "format": resource["format"],
            "content": content
        })
    
    # For binary files (PDF), return as base64
    return jsonify({
        "success": True,
        "id": resource_id,
        "name": resource["name"],
        "format": resource["format"],
        "content": content,
        "encoding": "base64"
    })


@app.route('/api/v1/resources/category/<category>', methods=['GET'])
def get_by_category(category):
    """List resources by category"""
    resources = server.list_by_category(category)
    
    if not resources:
        return jsonify({
            "success": False,
            "error": f"Category not found: {category}"
        }), 404
    
    return jsonify({
        "success": True,
        "category": category,
        "count": len(resources),
        "resources": resources
    })


@app.route('/api/v1/resources/format/<format_type>', methods=['GET'])
def get_by_format(format_type):
    """List resources by format"""
    resources = server.list_by_format(format_type)
    
    if not resources:
        return jsonify({
            "success": False,
            "error": f"Format not found: {format_type}"
        }), 404
    
    return jsonify({
        "success": True,
        "format": format_type,
        "count": len(resources),
        "resources": resources
    })


@app.route('/api/v1/index', methods=['GET'])
def get_index():
    """Get resource index"""
    index = server.get_index()
    return jsonify({
        "success": True,
        "index": index
    })


@app.route('/api/v1/search', methods=['GET'])
def search_resources():
    """Search resources by name or ID"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Query parameter 'q' is required"
        }), 400
    
    resources = server.list_resources()
    results = [
        r for r in resources
        if query in r["id"].lower() or query in r["name"].lower()
    ]
    
    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "resources": results
    })


@app.route('/api/v1/schema', methods=['GET'])
def openapi_schema():
    """OpenAPI schema for ChatGPT integration"""
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": API_INFO["title"],
            "version": API_INFO["version"],
            "description": API_INFO["description"]
        },
        "servers": [
            {
                "url": request.host_url.rstrip('/'),
                "description": "Production server"
            }
        ],
        "paths": {
            "/api/v1/resources": {
                "get": {
                    "summary": "List all resources",
                    "operationId": "listResources",
                    "responses": {
                        "200": {
                            "description": "List of resources",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "count": {"type": "integer"},
                                            "resources": {"type": "array"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/resources/{resourceId}": {
                "get": {
                    "summary": "Get resource by ID",
                    "operationId": "getResource",
                    "parameters": [
                        {
                            "name": "resourceId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Resource ID"
                        },
                        {
                            "name": "content",
                            "in": "query",
                            "schema": {"type": "boolean"},
                            "description": "Include full content (default: false)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Resource details"
                        },
                        "404": {
                            "description": "Resource not found"
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
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Resource content"
                        }
                    }
                }
            },
            "/api/v1/resources/category/{category}": {
                "get": {
                    "summary": "List resources by category",
                    "operationId": "getByCategory",
                    "parameters": [
                        {
                            "name": "category",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Category name (schema, diagram)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Resources in category"
                        }
                    }
                }
            },
            "/api/v1/resources/format/{formatType}": {
                "get": {
                    "summary": "List resources by format",
                    "operationId": "getByFormat",
                    "parameters": [
                        {
                            "name": "formatType",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Format type (md, pdf)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Resources of format"
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
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Search query"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Search results"
                        }
                    }
                }
            },
            "/api/v1/index": {
                "get": {
                    "summary": "Get resource index",
                    "operationId": "getIndex",
                    "responses": {
                        "200": {
                            "description": "Resource index"
                        }
                    }
                }
            }
        }
    }
    
    return jsonify(schema)


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API info"""
    return jsonify({
        "name": API_INFO["title"],
        "version": API_INFO["version"],
        "description": API_INFO["description"],
        "endpoints": {
            "health": "/health",
            "list_resources": "/api/v1/resources",
            "get_resource": "/api/v1/resources/{resource_id}",
            "get_resource_content": "/api/v1/resources/{resource_id}/content",
            "by_category": "/api/v1/resources/category/{category}",
            "by_format": "/api/v1/resources/format/{format_type}",
            "search": "/api/v1/search?q=query",
            "index": "/api/v1/index",
            "openapi_schema": "/api/v1/schema"
        },
        "documentation": "See /api/v1/schema for OpenAPI specification"
    })


def run_server(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask server"""
    print(f"""
╔════════════════════════════════════════════════════════╗
║   SQL to Snowflake MCP Server - REST API              ║
╚════════════════════════════════════════════════════════╝

📡 API Server: http://{host}:{port}
🔍 OpenAPI Schema: http://{host}:{port}/api/v1/schema
📚 Documentation: http://{host}:{port}

Ready to accept requests from ChatGPT and other clients!
""")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    host = os.getenv('API_HOST', '127.0.0.1')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    # Allow CLI override
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    run_server(host=host, port=port, debug=debug)
