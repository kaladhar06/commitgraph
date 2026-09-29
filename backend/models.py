from pydantic import BaseModel
from typing import Optional


class Commitment(BaseModel):
    person: str
    commitment: str
    deadline: Optional[str] = None
    status: str = "PENDING"
    context: Optional[str] = None


class CommitmentResponse(BaseModel):
    message: str
    commitment: Commitment


class MeetingNotes(BaseModel):
    meeting_title: str
    notes: str


class MemoryQuestion(BaseModel):
    question: str