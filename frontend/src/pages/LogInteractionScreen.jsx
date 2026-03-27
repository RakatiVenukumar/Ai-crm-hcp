import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import AgentChatPanel from '../components/AgentChatPanel';
import InteractionEditor from '../components/InteractionEditor';
import RecentTimeline from '../components/RecentTimeline';
import { checkAgentHealth, runAgentChat } from '../redux/slices/agentSlice';
import { fetchHcps } from '../redux/slices/hcpSlice';
import { fetchTimeline, saveInteraction } from '../redux/slices/interactionSlice';

const getToday = () => new Date().toISOString().slice(0, 10);

const toText = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value);
  }
  return value || '';
};

function LogInteractionScreen() {
  const dispatch = useDispatch();
  const agent = useSelector((state) => state.agent);
  const hcp = useSelector((state) => state.hcp);
  const interaction = useSelector((state) => state.interaction);

  const [saveSuccessMessage, setSaveSuccessMessage] = useState('');

  const [form, setForm] = useState({
    hcp_id: '',
    interaction_type: 'meeting',
    date: getToday(),
    time: '',
    attendees: '',
    topics_discussed: '',
    materials_shared: '',
    samples_distributed: '',
    sentiment: '',
    outcomes: '',
    follow_up_actions: '',
    summary: '',
  });

  useEffect(() => {
    dispatch(checkAgentHealth());
    dispatch(fetchHcps());
    dispatch(fetchTimeline());
  }, [dispatch]);

  useEffect(() => {
    const extracted = agent.lastResponse?.extracted_data;
    if (!extracted) {
      return;
    }

    setForm((prev) => ({
      ...prev,
      topics_discussed: toText(extracted.key_topics || extracted.products_discussed || prev.topics_discussed),
      sentiment: extracted.sentiment || prev.sentiment,
      follow_up_actions: toText(extracted.follow_up_recommendation || prev.follow_up_actions),
      summary: extracted.summary || prev.summary,
      outcomes: toText(extracted.opportunities || prev.outcomes),
    }));
  }, [agent.lastResponse]);

  const handleAnalyze = (notes) => {
    setSaveSuccessMessage('');
    dispatch(runAgentChat(notes));
  };

  const handleFormChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const canSave = useMemo(() => {
    return form.hcp_id && form.interaction_type && form.date;
  }, [form]);

  const handleSave = async () => {
    setSaveSuccessMessage('');
    if (!canSave) {
      return;
    }

    const payload = {
      ...form,
      hcp_id: Number(form.hcp_id),
    };

    const resultAction = await dispatch(saveInteraction(payload));
    if (saveInteraction.fulfilled.match(resultAction)) {
      setSaveSuccessMessage('Interaction saved successfully.');
      dispatch(fetchTimeline());
    }
  };

  return (
    <main className="screen-root">
      <header className="hero">
        <div>
          <p className="eyebrow">AI-First CRM</p>
          <h1>HCP Interaction Console</h1>
          <p>
            Analyze field notes, auto-fill structured records, and save interactions in one flow.
          </p>
        </div>
      </header>

      <section className="layout-grid">
        <AgentChatPanel
          loading={agent.loading}
          onAnalyze={handleAnalyze}
          health={agent.health}
          error={agent.error}
        />

        <InteractionEditor
          form={form}
          onChange={handleFormChange}
          onSave={handleSave}
          saving={interaction.loading}
          hcpItems={hcp.items}
          saveError={interaction.error}
          saveSuccessMessage={saveSuccessMessage}
          extractedData={agent.lastResponse?.extracted_data}
        />

        <RecentTimeline interactions={interaction.timeline} />
      </section>
    </main>
  );
}

export default LogInteractionScreen;
