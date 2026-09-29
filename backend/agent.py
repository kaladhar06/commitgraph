import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file")


client = Groq(api_key=api_key)


# ---------------------------------------------------------
# EXTRACT COMMITMENTS FROM MEETING NOTES
# ---------------------------------------------------------

def extract_commitments(meeting_notes: str):

    system_prompt = """
You are the commitment extraction agent for CommitGraph.

Your job is to read meeting notes and identify concrete commitments.

A commitment is an action that a person agrees or promises to perform.

Extract:
- person
- commitment
- deadline
- status
- context

Rules:
1. Only extract actual commitments.
2. Do not invent information.
3. If there is no deadline, use null.
4. New commitments should have status "PENDING".
5. Return ONLY valid JSON.
6. Return an object containing a "commitments" array.
"""

    user_prompt = f"""
Meeting notes:

{meeting_notes}

Extract all concrete commitments from these notes.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format={
            "type": "json_object"
        },
        temperature=0
    )

    result = response.choices[0].message.content

    return json.loads(result)


# ---------------------------------------------------------
# ANSWER QUESTIONS USING HINDSIGHT MEMORIES
# ---------------------------------------------------------

def answer_from_memories(question: str, memories: str):

    system_prompt = """
You are CommitGraph, a meeting commitment memory assistant.

Answer the user's question using ONLY the supplied memories.

Rules:
1. Do not invent information.
2. Do not invent dates.
3. Never invent a completion date.
4. Only mention a completion date if that exact date appears
   explicitly in the supplied memories.
5. If a date is not available, do not create one.
6. If the memories do not contain enough information, clearly say so.
7. Be concise and factual.
8. Mention relevant people, commitments, deadlines, dependencies,
   and status when available.
9. Distinguish between a deadline and a completion date.
10. Do not assume that completing a commitment happened on the
    same date as the deadline.
11. Do not say that you are using an AI model.
"""

    user_prompt = f"""
User question:
{question}

Relevant memories:
{memories}

Answer the user's question using ONLY the relevant memories.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# PREPARE FOR A FUTURE MEETING
# ---------------------------------------------------------

def prepare_meeting_from_memories(
    person: str,
    memories: str
):

    system_prompt = """
You are CommitGraph, an AI meeting preparation assistant.

Your job is to prepare a project manager for an upcoming meeting
with a specific person.

Use ONLY the supplied memories.

Analyze the person's previous commitments, deadlines, dependencies,
status, and relevant meeting history.

Create a concise meeting preparation brief.

Include:

1. Previous commitments
2. Pending or unresolved items
3. Completed items if explicitly recorded
4. Overdue items only when the evidence supports that conclusion
5. Dependencies or blockers
6. Important follow-up questions

Rules:
- Do not invent information.
- Do not invent completion dates.
- Do not invent status changes.
- Do not assume a commitment is completed unless the memories
  explicitly indicate completion.
- A deadline is NOT a completion date.
- Do not call an item overdue merely because a date appears in
  the memory.
- Only call an item overdue when the supplied memories explicitly
  establish that it is overdue, or when the current date and
  deadline are both explicitly available and the status supports
  that conclusion.
- If status is unknown, say "Status unknown".
- If there are no relevant memories, clearly say so.
- Keep the response structured and easy to read.
- Focus only on information relevant to the meeting with the person.
"""

    user_prompt = f"""
Upcoming meeting with:
{person}

Relevant historical memories:
{memories}

Prepare a meeting brief for the project manager.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content