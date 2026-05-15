import os
import httpx
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

BACKEND_API_URL = os.getenv("ZPAY_BACKEND_API_URL", "http://localhost:3001/api/zpay")
AGENT_PK = "GBEHFEGXWEDPATKLFIASIMCRNABYFMA322JRXXJA7W3AMIQTIKKZU4IJ"

async def main():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"Initiating Handshake for Agent: {AGENT_PK}")
        try:
            resp = await client.post(f"{BACKEND_API_URL}/auth/request", json={
                "agent_pk": AGENT_PK,
                "agent_name": "Gemini Sovereign Agent"
            })
            resp.raise_for_status()
            data = resp.json()
            print("\n🤝 **Sovereign Handshake Initiated!**")
            print(f"Verification Code: {data['verification_code']}")
            print(f"Auth URL: {data['auth_url']}")
            print(f"Session ID: {data['session_id']}")
            print("\nPlease confirm the code in your browser and authorize the agent.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
