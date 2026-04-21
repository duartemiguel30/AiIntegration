import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# --- External API ---
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_RESULTS_PER_PAGE = 10

# --- Database ---
DATABASE_URL = "sqlite:///data/findings.db"

# --- Scheduler ---
SCHEDULE_INTERVAL_MINUTES = 1

# --- MCP Server ---
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")

# --- Agent safety ---
MAX_AGENT_ITERATIONS = 20