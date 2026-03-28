import { apiClient } from './apiClient';

export const agentService = {
  async health() {
    const { data } = await apiClient.get('/agent/health');
    return data;
  },

  async chat(userInput, conversationHistory = []) {
    const { data } = await apiClient.post('/agent/chat', { 
      user_input: userInput,
      conversation_history: conversationHistory,
    });
    return data;
  },
};
