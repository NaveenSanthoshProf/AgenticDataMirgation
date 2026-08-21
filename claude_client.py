#!/usr/bin/env python3
"""
Claude Integration Client for MCP Server
Allows Claude to call your REST API endpoints via tool use
"""

from anthropic import Anthropic
import requests
import json
import sys
import os
from typing import Optional

# Configuration
API_BASE_URL = os.getenv("MCP_API_URL", "http://localhost:5000")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

client = Anthropic()

# Define tools for Claude to use with your MCP API
TOOLS = [
    {
        "name": "list_resources",
        "description": "List all available database resources including schema and ERD diagrams",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "search_resources",
        "description": "Search for resources by keyword (e.g., 'products', 'assessments', 'audit')",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term to find resources"
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
                    "description": "ID of the resource (e.g., 'os_schema', 'products_erd_v0_5')"
                },
                "include_content": {
                    "type": "boolean",
                    "description": "Include full content (default: false for faster response)"
                }
            },
            "required": ["resource_id"]
        }
    },
    {
        "name": "get_by_category",
        "description": "Get all resources in a specific category",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["schema", "diagram"],
                    "description": "Category: 'schema' for database schema, 'diagram' for ERD diagrams"
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "get_by_format",
        "description": "Get all resources in a specific format",
        "input_schema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["md", "pdf"],
                    "description": "Format: 'md' for markdown, 'pdf' for PDF diagrams"
                }
            },
            "required": ["format"]
        }
    },
    {
        "name": "get_index",
        "description": "Get the resource index with fast lookups by category, format, and ID",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def call_mcp_api(endpoint: str, params: Optional[dict] = None) -> dict:
    """Call the local MCP API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": f"Cannot connect to MCP API at {API_BASE_URL}",
            "hint": "Make sure the API server is running: python api_server.py"
        }
    except requests.exceptions.Timeout:
        return {"error": "API request timed out"}
    except Exception as e:
        return {"error": str(e)}


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process Claude's tool calls and return results"""
    
    if tool_name == "list_resources":
        result = call_mcp_api("/api/v1/resources")
        return json.dumps(result)
    
    elif tool_name == "search_resources":
        query = tool_input.get("query", "")
        result = call_mcp_api("/api/v1/search", {"q": query})
        return json.dumps(result)
    
    elif tool_name == "get_resource":
        resource_id = tool_input.get("resource_id", "")
        include_content = tool_input.get("include_content", False)
        endpoint = f"/api/v1/resources/{resource_id}"
        if include_content:
            endpoint += "?content=true"
        result = call_mcp_api(endpoint)
        return json.dumps(result)
    
    elif tool_name == "get_by_category":
        category = tool_input.get("category", "")
        result = call_mcp_api(f"/api/v1/resources/category/{category}")
        return json.dumps(result)
    
    elif tool_name == "get_by_format":
        format_type = tool_input.get("format", "")
        result = call_mcp_api(f"/api/v1/resources/format/{format_type}")
        return json.dumps(result)
    
    elif tool_name == "get_index":
        result = call_mcp_api("/api/v1/index")
        return json.dumps(result)
    
    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def chat_with_claude(user_message: str, verbose: bool = False) -> str:
    """
    Chat with Claude, allowing it to use tools to query the MCP API
    
    Args:
        user_message: The user's message
        verbose: Print detailed information about tool calls
    
    Returns:
        Claude's final response text
    """
    messages = [{"role": "user", "content": user_message}]
    
    print(f"\n{'='*70}")
    print(f"👤 User: {user_message}")
    print(f"{'='*70}\n")
    
    # Initial request to Claude
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        tools=TOOLS,
        messages=messages
    )
    
    # Handle tool use in a loop
    iteration = 0
    while response.stop_reason == "tool_use":
        iteration += 1
        if verbose:
            print(f"[Iteration {iteration}] Claude wants to use tools...")
        
        # Add assistant's response to messages
        assistant_message = {"role": "assistant", "content": response.content}
        messages.append(assistant_message)
        
        # Process each tool call
        tool_results = []
        for content in response.content:
            if content.type == "tool_use":
                tool_name = content.name
                tool_input = content.input
                
                print(f"🔧 Tool Call: {tool_name}")
                if verbose:
                    print(f"   Input: {json.dumps(tool_input, indent=2)}")
                
                # Call the tool
                result = process_tool_call(tool_name, tool_input)
                result_obj = json.loads(result)
                
                if verbose:
                    print(f"   Result: {result[:300]}..." if len(result) > 300 else f"   Result: {result}")
                
                if "error" in result_obj:
                    print(f"   ⚠️  Error: {result_obj['error']}")
                else:
                    print(f"   ✓ Got {result_obj.get('count', 'data')}")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content.id,
                    "content": result
                })
        
        # Send tool results back to Claude
        messages.append({"role": "user", "content": tool_results})
        
        # Get next response from Claude
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            tools=TOOLS,
            messages=messages
        )
    
    # Extract final text response
    final_response = ""
    for content in response.content:
        if hasattr(content, "text"):
            final_response += content.text
    
    print(f"{'='*70}")
    print(f"🤖 Claude: {final_response}")
    print(f"{'='*70}\n")
    
    return final_response


def interactive_chat(verbose: bool = False):
    """Interactive chat loop with Claude"""
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║            Claude SQL Schema Assistant                          ║
║   Powered by MCP Server + Claude Tool Use                       ║
╚════════════════════════════════════════════════════════════════╝

📡 API URL: {API_BASE_URL}
🤖 Model: {CLAUDE_MODEL}

Type 'exit' or 'quit' to end the session.
Type 'help' for example questions.
    """)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!\n")
                break
            
            if user_input.lower() == 'help':
                print("""
Example questions you can ask Claude:

1. "What database resources do I have available?"
2. "Show me the Products ERD"
3. "Search for assessments-related schemas"
4. "List all ERD diagrams"
5. "What tables are in the database schema?"
6. "Find all resources in the diagram category"
7. "Get details about the Contracts module"
8. "Show me all markdown documentation"
9. "Search for audit-related resources"
10. "What's the difference between schema and diagram categories?"
                """)
                continue
            
            # Chat with Claude
            chat_with_claude(user_input, verbose=verbose)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point"""
    global API_BASE_URL, CLAUDE_MODEL
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Claude Integration Client for MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat
  python claude_client.py
  
  # Single question
  python claude_client.py -q "What tables are in the database?"
  
  # Verbose output
  python claude_client.py -v
  
  # Both
  python claude_client.py -q "Show me products" -v
        """
    )
    
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="Ask a single question and exit"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information about tool calls"
    )
    
    parser.add_argument(
        "--api-url",
        type=str,
        default=API_BASE_URL,
        help=f"MCP API URL (default: {API_BASE_URL})"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=CLAUDE_MODEL,
        help=f"Claude model to use (default: {CLAUDE_MODEL})"
    )
    
    args = parser.parse_args()
    
    # Update globals if provided
    if args.api_url != API_BASE_URL:
        API_BASE_URL = args.api_url
    if args.model != CLAUDE_MODEL:
        CLAUDE_MODEL = args.model
    
    # Run single question or interactive chat
    if args.question:
        chat_with_claude(args.question, verbose=args.verbose)
    else:
        interactive_chat(verbose=args.verbose)


if __name__ == "__main__":
    main()
