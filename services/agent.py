from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are an expert cybersecurity analyst. 
Fetch the latest security vulnerabilities and store a classified finding for each one.
Use CVSS score to guide severity classification.
"""