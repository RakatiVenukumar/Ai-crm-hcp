import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import AgentChatPanel from '../components/AgentChatPanel';
import InteractionEditor from '../components/InteractionEditor';
import RecentTimeline from '../components/RecentTimeline';
import { checkAgentHealth, runAgentChat, clearConversationHistory } from '../redux/slices/agentSlice';
import { fetchHcps } from '../redux/slices/hcpSlice';
import { fetchTimeline, saveInteraction } from '../redux/slices/interactionSlice';
import { hcpService } from '../services/hcpService';

const getToday = () => new Date().toISOString().slice(0, 10);
const getCurrentTime = () => {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
};

const toText = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value);
  }
  return value || '';
};

const parseTimePhrase = (timePhrase) => {
  if (!timePhrase) return null;
  
  const timeStr = String(timePhrase).toLowerCase().trim();
  
  // If it's already in HH:MM format, return as is
  if (/^\d{1,2}:\d{2}$/.test(timeStr)) {
    return timeStr;
  }
  
  // Parse common time phrases
  const morningRegex = /\bmorning\b/i;
  const afternoonRegex = /\bafternoon\b/i;
  const eveningRegex = /\bevening\b/i;
  
  if (morningRegex.test(timeStr)) {
    return '09:00'; // Default to 9 AM
  }
  if (afternoonRegex.test(timeStr)) {
    return '14:00'; // Default to 2 PM
  }
  if (eveningRegex.test(timeStr)) {
    return '17:00'; // Default to 5 PM
  }
  
  // Try to extract time digits (e.g., "3:30", "10 AM", "2pm")
  const timeMatch = timeStr.match(/(\d{1,2}):?(\d{2})?\s*(am|pm)?/i);
  if (timeMatch) {
    let hour = parseInt(timeMatch[1]);
    const minute = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
    const period = timeMatch[3] ? timeMatch[3].toLowerCase() : '';
    
    if (period === 'pm' && hour !== 12) {
      hour += 12;
    }
    if (period === 'am' && hour === 12) {
      hour = 0;
    }
    
    const hourStr = String(hour).padStart(2, '0');
    const minStr = String(minute).padStart(2, '0');
    return `${hourStr}:${minStr}`;
  }
  
  // If we got a time phrase but couldn't parse it, return as is
  return timePhrase;
};

const getInitialFormState = () => ({
  hcp_name: '',
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

function LogInteractionScreen() {
  const dispatch = useDispatch();
  const agent = useSelector((state) => state.agent);
  const hcp = useSelector((state) => state.hcp);
  const interaction = useSelector((state) => state.interaction);

  const [saveSuccessMessage, setSaveSuccessMessage] = useState('');
  const [lastAnalyzedNotes, setLastAnalyzedNotes] = useState('');

  const [form, setForm] = useState(getInitialFormState());

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

    const isNameCorrection = /\b(sorry|correction|name)\b/i.test(lastAnalyzedNotes)
      && /\bnot\b/i.test(lastAnalyzedNotes);

    if (isNameCorrection) {
      setForm((prev) => ({
        ...prev,
        hcp_name: extracted.hcp_name || prev.hcp_name,
      }));
      return;
    }

    setForm((prev) => ({
      ...prev,
      hcp_name: extracted.hcp_name || prev.hcp_name,
      time: parseTimePhrase(extracted.time) || prev.time || getCurrentTime(),
      attendees: toText(extracted.attendees || prev.attendees || 'Not specified'),
      topics_discussed: toText(extracted.key_topics || extracted.products_discussed || prev.topics_discussed),
      materials_shared: toText(extracted.materials_shared || prev.materials_shared || 'Not specified'),
      samples_distributed: toText(extracted.samples_distributed || prev.samples_distributed || 'Not specified'),
      sentiment: extracted.sentiment || prev.sentiment,
      follow_up_actions: toText(extracted.follow_up_recommendation || prev.follow_up_actions),
      summary: extracted.summary || prev.summary,
      outcomes: toText(extracted.outcomes || extracted.opportunities || prev.outcomes || 'Not specified'),
    }));
  }, [agent.lastResponse, lastAnalyzedNotes]);

  const handleAnalyze = (notes) => {
    setSaveSuccessMessage('');
    setLastAnalyzedNotes(notes || '');
    dispatch(runAgentChat({ 
      userInput: notes, 
      conversationHistory: agent.conversationHistory 
    }));
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to delete the entire conversation? This cannot be undone.')) {
      dispatch(clearConversationHistory());
      setForm(getInitialFormState());
      setLastAnalyzedNotes('');
      setSaveSuccessMessage('');
    }
  };

  const handleFormChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const resolveHcpId = async (hcpName) => {
    const normalizedName = (hcpName || '').trim();
    if (!normalizedName) {
      return null;
    }

    const existing = hcp.items.find((item) => item.name.toLowerCase() === normalizedName.toLowerCase());
    if (existing) {
      return existing.id;
    }

    const created = await hcpService.create({ name: normalizedName });
    dispatch(fetchHcps());
    return created.id;
  };

  const canSave = useMemo(() => {
    return form.hcp_name.trim() && form.interaction_type && form.date;
  }, [form]);

  const handleSave = async () => {
    setSaveSuccessMessage('');
    if (!canSave) {
      return;
    }

    const hcpId = await resolveHcpId(form.hcp_name);
    if (!hcpId) {
      return;
    }

    const payload = {
      ...form,
      hcp_id: Number(hcpId),
    };
    delete payload.hcp_name;

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
          conversationHistory={agent.conversationHistory}
          onClearHistory={handleClearHistory}
        />

        <InteractionEditor
          form={form}
          onChange={handleFormChange}
          onSave={handleSave}
          saving={interaction.loading}
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
