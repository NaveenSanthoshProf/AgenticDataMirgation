#!/usr/bin/env python3
import json
import os
import requests
from typing import Optional
from openai import OpenAI

API_BASE_URL = os.getenv("MCP_API_URL", "http://localhost:5000")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-3")

client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_resources",
            "description": "List all available database resources including schema and ERD diagrams",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_resources",
            "description": "Search for resources by keyword (e.g. 'products', 'assessments', 'audit')",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_resource",
            "description": "Get detailed information about a specific resource",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_id": {"type": "string", "description": "Resource ID"},
                    "include_content": {"type": "boolean", "description": "Include full content"},
                },
                "required": ["resource_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_by_category",
            "description": "Get all resources in a category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["schema", "diagram"],
                        "description": "Category: 'schema' or 'diagram'",
                    }
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_index",
            "description": "Get the resource index with lookups by category, format, and ID",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def call_api(endpoint: str, params: Optional[dict] = None) -> dict:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to API at {API_BASE_URL}. Run: python api_server.py"}
    except requests.exceptions.Timeout:
        return {"error": "API request timed out"}
    except Exception as e:
        return {"error": str(e)}


def process_tool_call(name: str, args: dict) -> str:
    if name == "list_resources":
        return json.dumps(call_api("/api/v1/resources"))
    elif name == "search_resources":
        return json.dumps(call_api("/api/v1/search", {"q": args.get("query", "")}))
    elif name == "get_resource":
        rid = args.get("resource_id", "")
        endpoint = f"/api/v1/resources/{rid}"
        if args.get("include_content"):
            endpoint += "?content=true"
        return json.dumps(call_api(endpoint))
    elif name == "get_by_category":
        return json.dumps(call_api(f"/api/v1/resources/category/{args.get('category', '')}"))
    elif name == "get_index":
        return json.dumps(call_api("/api/v1/index"))
    return json.dumps({"error": f"Unknown tool: {name}"})


def chat(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    print(f"\nYou: {user_message}\n")

    response = client.chat.completions.create(
        model=GROK_MODEL,
        tools=TOOLS,
        messages=messages,
    )

    while response.choices[0].finish_reason == "tool_calls":
        msg = response.choices[0].message
        messages.append(msg)

        tool_results = []
        for tc in msg.tool_calls:
            print(f"  [tool] {tc.function.name}")
            result = process_tool_call(tc.function.name, json.loads(tc.function.arguments))
            tool_results.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        messages.extend(tool_results)
        response = client.chat.completions.create(
            model=GROK_MODEL,
            tools=TOOLS,
            messages=messages,
        )

    reply = response.choices[0].message.content
    print(f"\nGrok: {reply}\n")
    return reply


def main():
    print(f"Grok SQL Schema Assistant  |  model: {GROK_MODEL}  |  api: {API_BASE_URL}")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                break
            chat(user_input)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
