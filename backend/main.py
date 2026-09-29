from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    Commitment,
    CommitmentResponse,
    MeetingNotes,
    MemoryQuestion
)

from backend.database import (
    create_tables,
    save_commitment,
    get_all_commitments,
    save_meeting,
    get_all_meetings,
    update_commitment_status
)

from backend.agent import (
    extract_commitments,
    answer_from_memories,
    prepare_meeting_from_memories
)

from backend.hindsight_memory import (
    retain_memory,
    recall_memory,
    format_commitment_memory
)


app = FastAPI(title="CommitGraph API")


# ---------------------------------------------------------
# CORS
# Allow the React frontend to communicate with FastAPI
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

create_tables()


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "CommitGraph API is running",
        "status": "success"
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# CREATE SINGLE COMMITMENT
# ---------------------------------------------------------

@app.post("/commitments", response_model=CommitmentResponse)
def create_commitment(commitment: Commitment):

    save_commitment(
        person=commitment.person,
        commitment=commitment.commitment,
        deadline=commitment.deadline,
        status=commitment.status,
        context=commitment.context
    )

    memory_text = format_commitment_memory(
        person=commitment.person,
        commitment=commitment.commitment,
        deadline=commitment.deadline,
        status=commitment.status,
        context=commitment.context
    )

    retain_memory(memory_text)

    return {
        "message": "Commitment created successfully",
        "commitment": commitment
    }


# ---------------------------------------------------------
# GET ALL COMMITMENTS
# ---------------------------------------------------------

@app.get("/commitments")
def get_commitments():

    commitments = get_all_commitments()

    return {
        "count": len(commitments),
        "commitments": commitments
    }


# ---------------------------------------------------------
# CREATE MEETING
# ---------------------------------------------------------

@app.post("/meetings")
def create_meeting(meeting: MeetingNotes):

    meeting_id = save_meeting(
        meeting_title=meeting.meeting_title,
        notes=meeting.notes
    )

    return {
        "message": "Meeting notes saved successfully",
        "meeting_id": meeting_id,
        "meeting": meeting
    }


# ---------------------------------------------------------
# GET ALL MEETINGS
# ---------------------------------------------------------

@app.get("/meetings")
def get_meetings():

    meetings = get_all_meetings()

    return {
        "count": len(meetings),
        "meetings": meetings
    }


# ---------------------------------------------------------
# PROCESS MEETING
# ---------------------------------------------------------

@app.post("/process-meeting")
def process_meeting(meeting: MeetingNotes):

    meeting_id = save_meeting(
        meeting_title=meeting.meeting_title,
        notes=meeting.notes
    )

    result = extract_commitments(meeting.notes)

    extracted_commitments = result.get("commitments", [])

    saved_commitments = []

    for item in extracted_commitments:

        person = item.get("person", "Unknown")
        commitment = item.get("commitment", "")
        deadline = item.get("deadline")
        status = item.get("status", "PENDING")
        context = item.get("context")

        save_commitment(
            person=person,
            commitment=commitment,
            deadline=deadline,
            status=status,
            context=context
        )

        memory_text = format_commitment_memory(
            person=person,
            commitment=commitment,
            deadline=deadline,
            status=status,
            context=context
        )

        retain_memory(memory_text)

        saved_commitments.append(item)

    return {
        "message": "Meeting processed successfully",
        "meeting_id": meeting_id,
        "commitments_found": len(saved_commitments),
        "commitments": saved_commitments
    }


# ---------------------------------------------------------
# ASK COMMITGRAPH
# ---------------------------------------------------------

@app.post("/ask")
def ask_commitgraph(question: MemoryQuestion):

    memory_result = recall_memory(question.question)

    memories = "\n".join(
        memory.text
        for memory in memory_result.results
    )

    answer = answer_from_memories(
        question=question.question,
        memories=memories
    )

    return {
        "question": question.question,
        "answer": answer,
        "memory_count": len(memory_result.results)
    }


# ---------------------------------------------------------
# PREPARE FOR FUTURE MEETING
# ---------------------------------------------------------

@app.post("/prepare-meeting/{person}")
def prepare_meeting(person: str):

    memory_result = recall_memory(
        f"previous meetings, commitments, deadlines, "
        f"dependencies, status and follow-ups involving {person}"
    )

    memories = "\n".join(
        memory.text
        for memory in memory_result.results
    )

    preparation = prepare_meeting_from_memories(
        person=person,
        memories=memories
    )

    return {
        "person": person,
        "preparation": preparation,
        "memory_count": len(memory_result.results)
    }


# ---------------------------------------------------------
# UPDATE COMMITMENT STATUS
# ---------------------------------------------------------

@app.put("/commitments/{commitment_id}/status")
def update_status(commitment_id: int, status: str):

    update_commitment_status(
        commitment_id=commitment_id,
        status=status
    )

    commitments = get_all_commitments()

    updated_commitment = None

    for item in commitments:

        if item["id"] == commitment_id:
            updated_commitment = item
            break

    if updated_commitment is None:

        return {
            "message": "Commitment not found",
            "commitment_id": commitment_id
        }

    memory_text = (
        f"Commitment status update: "
        f"{updated_commitment['person']} changed the status of "
        f"the commitment '{updated_commitment['commitment']}' "
        f"from PENDING to {status}. "
        f"Original deadline: "
        f"{updated_commitment['deadline'] or 'not specified'}. "
        f"Context: "
        f"{updated_commitment['context'] or 'not specified'}. "
        f"No completion date was recorded."
    )

    retain_memory(memory_text)

    return {
        "message": "Commitment status updated successfully",
        "commitment_id": commitment_id,
        "status": status,
        "memory_saved": True
    }