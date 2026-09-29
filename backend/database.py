import sqlite3

DATABASE_NAME = "commitgraph.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS commitments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person TEXT NOT NULL,
            commitment TEXT NOT NULL,
            deadline TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING',
            context TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_title TEXT NOT NULL,
            notes TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_commitment(person, commitment, deadline, status, context):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO commitments
        (person, commitment, deadline, status, context)
        VALUES (?, ?, ?, ?, ?)
        """,
        (person, commitment, deadline, status, context)
    )

    connection.commit()
    commitment_id = cursor.lastrowid
    connection.close()

    return commitment_id


def get_all_commitments():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM commitments
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_meeting(meeting_title, notes):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO meetings
        (meeting_title, notes)
        VALUES (?, ?)
        """,
        (meeting_title, notes)
    )

    connection.commit()
    meeting_id = cursor.lastrowid
    connection.close()

    return meeting_id


def get_all_meetings():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM meetings
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

# ---------------------------------------------------------
# UPDATE COMMITMENT STATUS
# ---------------------------------------------------------

def update_commitment_status(commitment_id, status):

    connection = get_connection()

    connection.execute(
        """
        UPDATE commitments
        SET status = ?
        WHERE id = ?
        """,
        (status, commitment_id)
    )

    connection.commit()
    connection.close()