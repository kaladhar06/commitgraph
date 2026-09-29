import os
import requests

from dotenv import load_dotenv


load_dotenv()

base_url = os.getenv("HINDSIGHT_BASE_URL")
api_key = os.getenv("HINDSIGHT_API_KEY")
bank_id = os.getenv("HINDSIGHT_BANK_ID")


if not base_url:
    raise ValueError("HINDSIGHT_BASE_URL is missing")

if not api_key:
    raise ValueError("HINDSIGHT_API_KEY is missing")

if not bank_id:
    raise ValueError("HINDSIGHT_BANK_ID is missing")


url = f"{base_url}/v1/default/banks/{bank_id}/memories"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}


response = requests.delete(
    url,
    headers=headers
)


print("Status code:", response.status_code)
print("Response:", response.text)