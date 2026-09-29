import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()


HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID")


if not HINDSIGHT_BASE_URL:
    raise ValueError("HINDSIGHT_BASE_URL is missing from .env")

if not HINDSIGHT_API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing from .env")

if not HINDSIGHT_BANK_ID:
    raise ValueError("HINDSIGHT_BANK_ID is missing from .env")


client = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY
)


def retain_memory(content: str):
    return client.retain(
        bank_id=HINDSIGHT_BANK_ID,
        content=content,
        retain_async=True
    )


def recall_memory(query: str):
    return client.recall(
        bank_id=HINDSIGHT_BANK_ID,
        query=query
    )


def format_commitment_memory(
    person: str,
    commitment: str,
    deadline: str | None,
    status: str,
    context: str | None
):
    return (
        f"{person} committed to {commitment}. "
        f"Deadline: {deadline or 'not specified'}. "
        f"Status: {status}. "
        f"Context: {context or 'not specified'}."
    )