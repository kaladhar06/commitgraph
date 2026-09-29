import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [meetingTitle, setMeetingTitle] = useState("");
  const [meetingNotes, setMeetingNotes] = useState("");
  const [commitments, setCommitments] = useState([]);

  const [person, setPerson] = useState("");
  const [preparation, setPreparation] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [memoryCount, setMemoryCount] = useState(0);

  const [activities, setActivities] = useState([]);

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  function addActivity(title, description) {
    setActivities((previous) => [
      {
        id: Date.now(),
        title,
        description,
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
      ...previous,
    ]);
  }

  async function processMeeting() {
    if (!meetingTitle.trim() || !meetingNotes.trim()) {
      setMessage("Please enter the meeting title and notes.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/process-meeting`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          meeting_title: meetingTitle,
          notes: meetingNotes,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to process meeting"
        );
      }

      setCommitments(data.commitments || []);

      setMessage(
        `Meeting processed successfully. ${data.commitments_found} commitment(s) found.`
      );

      addActivity(
        "Meeting processed",
        `${data.commitments_found} commitment(s) extracted and stored in Hindsight.`
      );

      setMeetingTitle("");
      setMeetingNotes("");

      await loadCommitments();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function loadCommitments() {
    try {
      const response = await fetch(`${API_URL}/commitments`);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load commitments"
        );
      }

      setCommitments(data.commitments || []);
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    }
  }

  async function updateStatus(commitmentId, newStatus) {
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        `${API_URL}/commitments/${commitmentId}/status?status=${encodeURIComponent(
          newStatus
        )}`,
        {
          method: "PUT",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to update status"
        );
      }

      setMessage(
        `Commitment status updated to ${newStatus}. Memory saved to Hindsight.`
      );

      addActivity(
        "Commitment updated",
        `Status changed to ${newStatus}. Hindsight memory saved.`
      );

      await loadCommitments();
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function prepareMeeting() {
    if (!person.trim()) {
      setMessage("Please enter a person's name.");
      return;
    }

    setLoading(true);
    setMessage("");
    setPreparation("");

    try {
      const response = await fetch(
        `${API_URL}/prepare-meeting/${encodeURIComponent(person)}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to prepare meeting"
        );
      }

      setPreparation(
        data.preparation || "No preparation available."
      );

      setMessage(
        `Meeting preparation generated using ${data.memory_count} memory result(s).`
      );

      addActivity(
        "Meeting preparation generated",
        `${data.memory_count} memory result(s) recalled for ${person}.`
      );
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function askCommitGraph() {
    if (!question.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    setLoading(true);
    setMessage("");
    setAnswer("");
    setMemoryCount(0);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to ask CommitGraph"
        );
      }

      setAnswer(
        data.answer || "No answer was returned."
      );

      setMemoryCount(data.memory_count || 0);

      setMessage(
        `Answer generated using ${data.memory_count} memory result(s).`
      );

      addActivity(
        "Hindsight memory recalled",
        `${data.memory_count} memory result(s) used to answer your question.`
      );
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  function getStatusClass(status) {
    return (
      status?.toLowerCase().replaceAll(" ", "-") ||
      "pending"
    );
  }

  return (
    <div className="app">

      <header className="header">
        <div>
          <div className="logo">
            CommitGraph
          </div>

          <p>
            Persistent Meeting Commitment Memory
          </p>
        </div>

        <div className="header-badge">
          <span className="status-dot"></span>
          Hindsight Memory Active
        </div>
      </header>


      <main className="container">

        <section className="hero">

          <div className="hero-content">

            <span className="eyebrow">
              AI MEETING MEMORY
            </span>

            <h1>
              Meetings remember.
              <br />
              <span>
                Commitments don't get lost.
              </span>
            </h1>

            <p>
              CommitGraph extracts commitments
              from meetings, remembers them over
              time, and prepares you for future
              conversations.
            </p>

          </div>


          <div className="hero-visual">

            <img
              src="/images/commitgraph-hero.png"
              alt="CommitGraph AI meeting memory visualization"
            />

          </div>

        </section>


        {message && (
          <div className="message">
            {message}
          </div>
        )}


        <section className="card process-card">

          <div className="section-heading">

            <div>
              <span className="step-number">
                01
              </span>

              <h2>
                Process a Meeting
              </h2>
            </div>

            <span className="section-description">
              Extract and remember commitments
            </span>

          </div>


          <div className="form-group">

            <label>
              Meeting Title
            </label>

            <input
              type="text"
              placeholder="Example: API Integration Meeting"
              value={meetingTitle}
              onChange={(e) =>
                setMeetingTitle(e.target.value)
              }
            />

          </div>


          <div className="form-group">

            <label>
              Meeting Notes
            </label>

            <textarea
              rows="8"
              placeholder="Paste your meeting notes here..."
              value={meetingNotes}
              onChange={(e) =>
                setMeetingNotes(e.target.value)
              }
            />

          </div>


          <button
            className="primary-button"
            onClick={processMeeting}
            disabled={loading}
          >
            {loading
              ? "Processing..."
              : "Process Meeting"}
          </button>

        </section>


        <section className="card">

          <div className="section-heading">

            <div>

              <span className="step-number">
                02
              </span>

              <h2>
                Commitments
              </h2>

            </div>

            <button
              className="secondary-button"
              onClick={loadCommitments}
            >
              Refresh
            </button>

          </div>


          {commitments.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ◌
              </div>

              <h3>
                No commitments yet
              </h3>

              <p>
                Process a meeting above
                to extract commitments.
              </p>

            </div>

          ) : (

            <div className="commitment-list">

              {commitments.map((item, index) => (

                <div
                  className="commitment-item"
                  key={item.id || index}
                >

                  <div className="commitment-main">

                    <div className="person-avatar">
                      {item.person
                        ?.charAt(0)
                        ?.toUpperCase() || "?"}
                    </div>

                    <div>

                      <h3>
                        {item.person}
                      </h3>

                      <p className="commitment-text">
                        {item.commitment}
                      </p>

                      {item.context && (
                        <p className="context">
                          {item.context}
                        </p>
                      )}

                    </div>

                  </div>


                  <div className="commitment-meta">

                    <span
                      className={`status ${getStatusClass(
                        item.status
                      )}`}
                    >
                      {item.status}
                    </span>

                    <span className="deadline">
                      {item.deadline
                        ? `Deadline: ${item.deadline}`
                        : "No deadline"}
                    </span>

                    {item.status !== "COMPLETED" && (

                      <button
                        className="complete-button"
                        onClick={() =>
                          updateStatus(
                            item.id,
                            "COMPLETED"
                          )
                        }
                        disabled={loading}
                      >
                        Mark Completed
                      </button>

                    )}

                  </div>

                </div>

              ))}

            </div>

          )}

        </section>


        <section className="card prepare-card">

          <div className="section-heading">

            <div>

              <span className="step-number">
                03
              </span>

              <h2>
                Prepare for a Meeting
              </h2>

            </div>

            <span className="section-description">
              Recall what happened before
            </span>

          </div>


          <div className="prepare-form">

            <div className="form-group">

              <label>
                Person
              </label>

              <input
                type="text"
                placeholder="Example: Ravi"
                value={person}
                onChange={(e) =>
                  setPerson(e.target.value)
                }
              />

            </div>


            <button
              className="primary-button"
              onClick={prepareMeeting}
              disabled={loading}
            >
              {loading
                ? "Preparing..."
                : "Prepare Meeting"}
            </button>

          </div>


          {preparation && (

            <div className="preparation-result">

              <div className="result-header">
                MEMORY-BASED BRIEF
              </div>

              <div className="result-content">
                {preparation}
              </div>

            </div>

          )}

        </section>


        <section className="card ask-card">

          <div className="section-heading">

            <div>

              <span className="step-number">
                04
              </span>

              <h2>
                Ask CommitGraph
              </h2>

            </div>

            <span className="section-description">
              Ask questions about remembered history
            </span>

          </div>


          <div className="form-group">

            <label>
              Your Question
            </label>

            <textarea
              rows="4"
              placeholder="Example: What commitments from Ravi are still unresolved?"
              value={question}
              onChange={(e) =>
                setQuestion(e.target.value)
              }
            />

          </div>


          <button
            className="primary-button"
            onClick={askCommitGraph}
            disabled={loading}
          >
            {loading
              ? "Thinking..."
              : "Ask CommitGraph"}
          </button>


          {answer && (

            <div className="answer-result">

              <div className="answer-header">

                <span>
                  HINDSIGHT MEMORY ANSWER
                </span>

                <span>
                  {memoryCount} memories recalled
                </span>

              </div>

              <div className="answer-content">
                {answer}
              </div>

            </div>

          )}

        </section>


        <section className="card activity-card">

          <div className="section-heading">

            <div>

              <span className="step-number">
                05
              </span>

              <h2>
                Memory Activity
              </h2>

            </div>

            <span className="section-description">
              See what CommitGraph remembers
            </span>

          </div>


          {activities.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ✦
              </div>

              <h3>
                No activity yet
              </h3>

              <p>
                Process a meeting or ask
                CommitGraph a question to
                see memory activity here.
              </p>

            </div>

          ) : (

            <div className="activity-list">

              {activities.map((activity) => (

                <div
                  className="activity-item"
                  key={activity.id}
                >

                  <div className="activity-icon">
                    ✓
                  </div>

                  <div className="activity-content">

                    <h3>
                      {activity.title}
                    </h3>

                    <p>
                      {activity.description}
                    </p>

                  </div>

                  <span className="activity-time">
                    {activity.time}
                  </span>

                </div>

              ))}

            </div>

          )}

        </section>


        <section className="memory-banner">

          <div className="memory-icon">
            ✦
          </div>

          <div>

            <h2>
              Powered by Hindsight
            </h2>

            <p>
              CommitGraph doesn't just process
              the current meeting. It remembers
              previous commitments and uses that
              history to provide context for
              future meetings.
            </p>

          </div>

        </section>

      </main>


      <footer>

        <p>
          CommitGraph · AI-powered meeting
          commitment memory
        </p>

      </footer>

    </div>
  );
}

export default App;