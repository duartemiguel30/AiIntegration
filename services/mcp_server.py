import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mcp.server.fastmcp import FastMCP
from services.fetcher import fetch_security_data
from services.storage import store_finding

mcp = FastMCP("security-aggregator", host="0.0.0.0", port=8001)


@mcp.tool()
def fetchSecurityData() -> list[dict]:
    """Fetches the latest CVE vulnerabilities from the NVD API."""
    return fetch_security_data()


@mcp.tool()
def storeFinding(id: str, topic: str, severity: str, summary: str) -> dict:
    """Stores a classified security finding in the database."""
    return store_finding({"id": id, "topic": topic, "severity": severity, "summary": summary})


if __name__ == "__main__":
    mcp.run(transport="sse")
