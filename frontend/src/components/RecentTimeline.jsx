function RecentTimeline({ interactions, onClearTimeline }) {
  return (
    <section className="panel panel-timeline">
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h2>Recent Timeline</h2>
          <span className="pill">{interactions.length} Records</span>
        </div>
        {interactions.length > 0 && (
          <button 
            onClick={onClearTimeline} 
            className="btn btn-soft" 
            style={{ padding: '6px 12px', fontSize: '0.8rem', border: '1px solid var(--danger)', color: 'var(--danger)' }}
          >
            Clear Timeline
          </button>
        )}
      </div>

      {interactions.length === 0 ? (
        <p className="panel-subtext">No interaction history yet.</p>
      ) : (
        <ul className="timeline-list">
          {interactions.slice(0, 8).map((item) => (
            <li key={item.id} className="timeline-item">
              <div className="timeline-head">
                <strong>{item.interaction_type || 'interaction'}</strong>
                <small>{item.date || 'N/A'} {item.time || ''}</small>
              </div>
              <p>{item.summary || item.topics_discussed || 'No summary available'}</p>
              <span className="chip muted">HCP ID: {item.hcp_id}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default RecentTimeline;
