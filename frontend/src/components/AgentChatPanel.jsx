import { useState, useRef, useEffect } from 'react';

function AgentChatPanel({ loading, onAnalyze, health, error, conversationHistory = [], onClearHistory }) {
  const [notes, setNotes] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversationHistory]);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!notes.trim()) {
      return;
    }
    onAnalyze(notes.trim());
    setNotes('');
  };

  return (
    <section className="panel panel-chat">
      <div className="panel-header">
        <h2>AI Interaction Assistant</h2>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className={`status-dot ${health?.ready ? 'ok' : 'warn'}`}>
            {health?.ready ? 'Agent Ready' : 'Agent Offline'}
          </span>
          {conversationHistory.length > 0 && (
            <button
              className="btn btn-soft"
              onClick={onClearHistory}
              disabled={loading}
              title="Delete conversation history"
              style={{ padding: '4px 8px', fontSize: '12px' }}
            >
              Delete Chat
            </button>
          )}
        </div>
      </div>

      <p className="panel-subtext">
        Paste raw field notes. The assistant extracts structured data, follow-up actions, and insights.
      </p>

      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        marginBottom: '12px', 
        padding: '10px',
        backgroundColor: '#f5f5f5',
        borderRadius: '4px',
        minHeight: '200px',
        maxHeight: '300px',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {conversationHistory.length === 0 ? (
          <div style={{ 
            color: '#999', 
            textAlign: 'center', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%',
          }}>
            <p>No conversation yet. Start by pasting field notes above.</p>
          </div>
        ) : (
          conversationHistory.map((message, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: '8px',
                padding: '8px',
                borderRadius: '4px',
                backgroundColor: message.role === 'user' ? '#e3f2fd' : '#f1f8e9',
                alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '90%',
                wordWrap: 'break-word',
              }}
            >
              <div style={{ fontWeight: 'bold', fontSize: '11px', marginBottom: '2px' }}>
                {message.role === 'user' ? 'You' : 'AI'}
              </div>
              <div style={{ fontSize: '12px', lineHeight: '1.3' }}>
                {typeof message.content === 'string' ? (
                  message.role === 'assistant' ? message.content : message.content.substring(0, 200)
                ) : (
                  <pre style={{ 
                    margin: '0', 
                    overflow: 'auto',
                    fontSize: '11px',
                    maxHeight: '100px',
                  }}>
                    {JSON.stringify(message.content, null, 1).substring(0, 300)}...
                  </pre>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Example: Met Dr. Chen at Central Hospital. Discussed oncology product line. Positive response, wants training in two weeks."
          rows={4}
          className="chat-input"
          disabled={loading}
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
            Clear Input
          </button>
        </div>
      </form>

      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export default AgentChatPanel;
