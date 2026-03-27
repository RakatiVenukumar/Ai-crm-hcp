function InteractionEditor({
  form,
  onChange,
  onSave,
  saving,
  hcpItems,
  saveError,
  saveSuccessMessage,
  extractedData,
}) {
  const updateField = (field) => (event) => onChange(field, event.target.value);

  return (
    <section className="panel panel-editor">
      <div className="panel-header">
        <h2>Interaction Record</h2>
        <span className="pill">Ready to Save</span>
      </div>

      <div className="form-grid">
        <label>
          HCP
          <select value={form.hcp_id} onChange={updateField('hcp_id')}>
            <option value="">Select HCP</option>
            {hcpItems.map((hcp) => (
              <option key={hcp.id} value={hcp.id}>
                {hcp.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Interaction Type
          <input value={form.interaction_type} onChange={updateField('interaction_type')} placeholder="meeting" />
        </label>

        <label>
          Date
          <input type="date" value={form.date} onChange={updateField('date')} />
        </label>

        <label>
          Time
          <input type="time" value={form.time} onChange={updateField('time')} />
        </label>
      </div>

      <label>
        Topics Discussed
        <textarea value={form.topics_discussed} onChange={updateField('topics_discussed')} rows={3} />
      </label>

      <div className="form-grid two-col">
        <label>
          Sentiment
          <input value={form.sentiment} onChange={updateField('sentiment')} placeholder="positive / neutral / negative" />
        </label>

        <label>
          Attendees
          <input value={form.attendees} onChange={updateField('attendees')} placeholder="Dr. Smith, Nurse Lead" />
        </label>
      </div>

      <label>
        Materials Shared
        <textarea value={form.materials_shared} onChange={updateField('materials_shared')} rows={2} />
      </label>

      <label>
        Samples Distributed
        <textarea value={form.samples_distributed} onChange={updateField('samples_distributed')} rows={2} />
      </label>

      <label>
        Outcomes
        <textarea value={form.outcomes} onChange={updateField('outcomes')} rows={2} />
      </label>

      <label>
        Follow-up Actions
        <textarea value={form.follow_up_actions} onChange={updateField('follow_up_actions')} rows={3} />
      </label>

      <label>
        Summary
        <textarea value={form.summary} onChange={updateField('summary')} rows={4} />
      </label>

      {extractedData ? (
        <div className="extracted-chips">
          <span className="chip">Detected HCP: {extractedData.hcp_name || 'N/A'}</span>
          <span className="chip">Sentiment: {extractedData.sentiment || 'N/A'}</span>
        </div>
      ) : null}

      <div className="chat-actions">
        <button className="btn btn-primary" onClick={onSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Interaction'}
        </button>
      </div>

      {saveError ? <p className="error-text">{saveError}</p> : null}
      {saveSuccessMessage ? <p className="success-text">{saveSuccessMessage}</p> : null}
    </section>
  );
}

export default InteractionEditor;
