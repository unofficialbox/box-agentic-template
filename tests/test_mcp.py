import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("mcp"), "Install .[mcp] to run the stdio integration test")
class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_stdio_discovery_calls_and_errors(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(command=sys.executable,
            args=["-m", "box_agentic.mcp_server", "--root", str(ROOT)])
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                listing = await session.list_tools()
                registry = json.loads((ROOT / "config/tools.json").read_text())["tools"]
                self.assertEqual({t.name for t in listing.tools}, {t["name"] for t in registry})
                for tool in listing.tools:
                    contract = next(t for t in registry if t["name"] == tool.name)
                    self.assertEqual(tool.inputSchema, contract["inputSchema"])
                    self.assertEqual(tool.outputSchema, contract["outputSchema"])
                result = await session.call_tool("get_record", {"record_id": "case-demo-001"})
                self.assertFalse(result.isError)
                self.assertEqual(result.structuredContent["version"], "1")
                for name, arguments in (("get_record", {"record_id": "absent"}),
                                        ("get_record", {"record_id": "case-demo-001", "extra": True}),
                                        ("send_signature", {})):
                    failure = await session.call_tool(name, arguments)
                    self.assertTrue(failure.isError)

    async def test_server_roundtrip_in_memory(self):
        from mcp.shared.memory import create_connected_server_and_client_session
        from box_agentic.mcp_server import build_server
        async with create_connected_server_and_client_session(build_server(ROOT)) as session:
            listing = await session.list_tools()
            self.assertEqual(len(listing.tools), 5)
            for tool in listing.tools:
                self.assertTrue(tool.annotations.readOnlyHint)
                self.assertFalse(tool.annotations.destructiveHint)
            result = await session.call_tool('propose_update', {
                'record_id': 'case-demo-001', 'expected_version': '1', 'changes': {'rate': 6.85}})
            self.assertFalse(result.isError)
            self.assertFalse(result.structuredContent['applied'])
            failure = await session.call_tool('get_record', {'record_id': 'absent'})
            self.assertTrue(failure.isError)
