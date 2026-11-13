"""Official MCP SDK stdio server, exposing fixture-only tools from the registry."""
import argparse
import asyncio
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from .runtime import Runtime, ToolError


def build_server(root):
    runtime = Runtime(root)
    server = Server("box-agentic-mock")

    @server.list_tools()
    async def list_tools():
        return [types.Tool(**{k: v for k, v in t.items()
                             if k in {"name", "description", "inputSchema", "outputSchema", "annotations"}})
                for t in runtime.tools]

    @server.call_tool()
    async def call_tool(name, arguments):
        try:
            result = runtime.call(name, arguments)
            return types.CallToolResult(content=[types.TextContent(type="text", text=json.dumps(result))],
                                        structuredContent=result, isError=False)
        except ToolError as error:
            return types.CallToolResult(content=[types.TextContent(type="text", text=str(error))], isError=True)

    return server


async def serve(root):
    server = build_server(root)
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(serve(args.root.resolve()))


if __name__ == "__main__":
    main()
