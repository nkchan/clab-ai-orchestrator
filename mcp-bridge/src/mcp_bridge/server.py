"""MCP Bridge Server - Main entry point.

Provides MCP tools for containerlab, FRR, and Junos operations.
Runs as a STDIO-based MCP server.
"""

import asyncio
import logging

import sys
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, Prompt, GetPromptResult, PromptMessage

from mcp_bridge.tools.clab import ClabTools
from mcp_bridge.tools.frr import FrrTools
from mcp_bridge.tools.junos import JunosTools
from mcp_bridge.tools.report import ReportTools

logger = logging.getLogger(__name__)

app = Server("mcp-bridge")

# Initialize tool handlers
clab_tools = ClabTools()
frr_tools = FrrTools()
junos_tools = JunosTools()
report_tools = ReportTools()

import pathlib

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="agent",
            description="Autonomous Investigation Workflow guidelines for ClabAgent",
            arguments=[],
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
    """Get a specific prompt by name."""
    if name != "agent":
        raise ValueError(f"Unknown prompt: {name}")

    agent_path = pathlib.Path("/app/agent.md")
    if agent_path.exists():
        content = agent_path.read_text(encoding="utf-8")
    else:
        content = "Error: agent.md not found in the container at /app/agent.md_ Please ensure it is mounted."

    return GetPromptResult(
        description="Autonomous Investigation Workflow guidelines",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=content
                )
            )
        ]
    )

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        # --- Containerlab tools ---
        Tool(
            name="clab_deploy",
            description="Deploy a containerlab topology. Requires the topology YAML file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topology_file": {
                        "type": "string",
                        "description": "Path to the containerlab topology YAML file",
                    },
                    "reconfigure": {
                        "type": "boolean",
                        "description": "Reconfigure existing lab (default: false)",
                        "default": False,
                    },
                },
                "required": ["topology_file"],
            },
        ),
        Tool(
            name="clab_destroy",
            description="Destroy a running containerlab topology. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topology_file": {
                        "type": "string",
                        "description": "Path to the containerlab topology YAML file",
                    },
                    "cleanup": {
                        "type": "boolean",
                        "description": "Remove lab directory (default: false)",
                        "default": False,
                    },
                },
                "required": ["topology_file"],
            },
        ),
        Tool(
            name="clab_inspect",
            description="Inspect a running containerlab topology and return node status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topology_file": {
                        "type": "string",
                        "description": "Path to the containerlab topology YAML file (optional)",
                    },
                    "name": {
                        "type": "string",
                        "description": "Lab name to inspect (optional)",
                    },
                },
            },
        ),
        # --- FRR tools ---
        Tool(
            name="frr_show",
            description="Execute a show command on an FRR node via vtysh.",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Docker container name of the FRR node",
                    },
                    "command": {
                        "type": "string",
                        "description": "Show command to execute (e.g., 'show ip bgp summary')",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "description": "Output format (default: text)",
                        "default": "text",
                    },
                },
                "required": ["container_name", "command"],
            },
        ),
        Tool(
            name="frr_config",
            description="Push configuration to an FRR node via vtysh.",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Docker container name of the FRR node",
                    },
                    "config_commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of configuration commands to push",
                    },
                },
                "required": ["container_name", "config_commands"],
            },
        ),
        # --- Junos tools ---
        Tool(
            name="junos_show",
            description="Execute a show command on a vJunos node via CLI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Docker container name of the vJunos node",
                    },
                    "command": {
                        "type": "string",
                        "description": "Show command (e.g., 'show bgp summary')",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["text", "json"],
                        "description": "Output format (default: text)",
                        "default": "text",
                    },
                },
                "required": ["container_name", "command"],
            },
        ),
        Tool(
            name="junos_config",
            description="Push configuration to a vJunos node.",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Docker container name of the vJunos node",
                    },
                    "config_commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of set-style configuration commands",
                    },
                },
                "required": ["container_name", "config_commands"],
            },
        ),
        # --- Report tools ---
        Tool(
            name="save_report",
            description="Save a markdown report to the local filesystem.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename of the report (e.g., 'bgp_outage_cause.md')",
                    },
                    "content": {
                        "type": "string",
                        "description": "Markdown content to save",
                    },
                },
                "required": ["filename", "content"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handlers."""
    try:
        if name == "clab_deploy":
            result = await clab_tools.deploy(
                arguments["topology_file"],
                arguments.get("reconfigure", False),
            )
        elif name == "clab_destroy":
            result = await clab_tools.destroy(
                arguments["topology_file"],
                arguments.get("cleanup", False),
            )
        elif name == "clab_inspect":
            result = await clab_tools.inspect(
                arguments.get("topology_file"),
                arguments.get("name"),
            )
        elif name == "frr_show":
            result = await frr_tools.show(
                arguments["container_name"],
                arguments["command"],
                arguments.get("format", "text"),
            )
        elif name == "frr_config":
            result = await frr_tools.configure(
                arguments["container_name"],
                arguments["config_commands"],
            )
        elif name == "junos_show":
            result = await junos_tools.show(
                arguments["container_name"],
                arguments["command"],
                arguments.get("format", "text"),
            )
        elif name == "junos_config":
            result = await junos_tools.configure(
                arguments["container_name"],
                arguments["config_commands"],
            )
        elif name == "save_report":
            result = await report_tools.save(
                arguments["filename"],
                arguments["content"],
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.exception(f"Tool {name} failed")
        return [TextContent(type="text", text=f"Error: {e}")]


async def run():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

sse = SseServerTransport("/messages")

class HandleSSE:
    async def __call__(self, scope, receive, send):
        async with sse.connect_sse(scope, receive, send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

class HandleMessages:
    async def __call__(self, scope, receive, send):
        await sse.handle_post_message(scope, receive, send)

starlette_app = Starlette(routes=[
    Route("/sse", endpoint=HandleSSE()),
    Route("/messages", endpoint=HandleMessages(), methods=["POST"]),
])

def main():
    """Entry point."""
    logging.basicConfig(level=logging.INFO)
    if "--sse" in sys.argv:
        port = 9005
        logger.info(f"Starting SSE server on port {port}")
        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        asyncio.run(run())


if __name__ == "__main__":
    main()
