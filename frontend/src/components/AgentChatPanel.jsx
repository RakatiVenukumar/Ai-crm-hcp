import { useState } from 'react';

function AgentChatPanel({ loading, onAnalyze, health, error }) {
  const [notes, setNotes] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!notes.trim()) {
      return;
    }
    onAnalyze(notes.trim());
  };

  return (
    <section className="panel panel-chat">
      <div className="panel-header">
        <h2>AI Interaction Assistant</h2>
        <span className={`status-dot ${health?.ready ? 'ok' : 'warn'}`}>
          {health?.ready ? 'Agent Ready' : 'Agent Offline'}
        </span>
      </div>

      <p className="panel-subtext">
        Paste raw field notes. The assistant extracts structured data, follow-up actions, and insights.
      </p>

      <form onSubmit={handleSubmit} className="chat-form">
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Example: Met Dr. Chen at Central Hospital. Discussed oncology product line. Positive response, wants training in two weeks."
          rows={11}
          className="chat-input"
        />

        <div className="chat-actions">
          <button type="submit" className="btn btn-primary" disabled={loading || !notes.trim()}>
            {loading ? 'Analyzing...' : 'Analyze with AI'}
          </button>
          <button
            type="button"
            className="btn btn-soft"
            onClick={() => setNotes('')}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </form>

      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export default AgentChatPanel;
