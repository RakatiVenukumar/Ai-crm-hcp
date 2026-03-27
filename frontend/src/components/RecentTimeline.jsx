function RecentTimeline({ interactions }) {
  return (
    <section className="panel panel-timeline">
      <div className="panel-header">
        <h2>Recent Timeline</h2>
        <span className="pill">{interactions.length} Records</span>
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
