import json
import logging
from mcp import ClientSession
from mcp.client.sse import sse_client
from google.genai import types
from services.agent import client, SYSTEM_PROMPT
from config import GEMINI_MODEL, MAX_AGENT_ITERATIONS, MCP_SERVER_URL

logger = logging.getLogger(__name__)

_JSON_TYPE_MAP = {
    "string": types.Type.STRING,
    "number": types.Type.NUMBER,
    "integer": types.Type.INTEGER,
    "boolean": types.Type.BOOLEAN,
}


def _parse_mcp_content(content) -> list:
    return [
        json.loads(text)
        for item in content
        if (text := getattr(item, "text", None))
    ]


def _build_gemini_tools(mcp_tools) -> list[types.Tool]:
    declarations = []
    for tool in mcp_tools:
        schema = tool.inputSchema or {}
        properties = {
            name: types.Schema(
                type=_JSON_TYPE_MAP.get(prop.get("type", "string"), types.Type.STRING),
                description=prop.get("description", ""),
            )
            for name, prop in schema.get("properties", {}).items()
        }
        declarations.append(types.FunctionDeclaration(
            name=tool.name,
            description=tool.description or "",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties=properties,
                required=schema.get("required", []),
            ),
        ))
    return [types.Tool(function_declarations=declarations)]


async def run_agent_async() -> list[dict]:
    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools_resp = await session.list_tools()
            gemini_tools = _build_gemini_tools(mcp_tools_resp.tools)
            logger.info("[RUNNER] MCP connected. Tools: %s", [t.name for t in mcp_tools_resp.tools])

            messages = [
                types.Content(role="user", parts=[types.Part(
                    text="Fetch the latest security vulnerabilities and store a finding for each one."
                )])
            ]

            findings = []

            for _ in range(MAX_AGENT_ITERATIONS):
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=messages,
                    config=types.GenerateContentConfig(
                        # modelo é stateless logo passamos em todas as calls
                        system_instruction=SYSTEM_PROMPT,
                        # functiomn calling
                        tools=gemini_tools,
                    ),
                )

                if not response.candidates:
                    logger.warning("[RUNNER] Gemini returned no candidates.")
                    break

                content = response.candidates[0].content
                messages.append(content)

                tool_calls = [p for p in content.parts if p.function_call]
                if not tool_calls:
                    logger.info("[RUNNER] Agent finished.")
                    break

                tool_results = []

                for part in tool_calls:
                    tool_name = part.function_call.name
                    tool_input = dict(part.function_call.args)
                    logger.info("[RUNNER] Tool call: %s | input: %s", tool_name, tool_input)

                    try:
                        mcp_result = await session.call_tool(tool_name, tool_input)
                        parsed = _parse_mcp_content(mcp_result.content)
                        result = parsed[0] if len(parsed) == 1 else parsed if parsed else {}
                        if tool_name == "storeFinding":
                            findings.append(tool_input)
                            logger.info("[RUNNER] Stored: [%s] %s", tool_input.get("severity"), tool_input.get("id"))
                    except Exception as e:
                        logger.error("[RUNNER] Tool error: %s", e)
                        result = {"error": str(e)}

                    logger.info("[RUNNER] Result: %s", str(result)[:200])
                    tool_results.append(
                        types.Part(function_response=types.FunctionResponse(
                            name=tool_name,
                            response={"result": result},
                        ))
                    )

                messages.append(types.Content(role="user", parts=tool_results))

            logger.info("[RUNNER] Done. Stored %d findings.", len(findings))
            return findings


