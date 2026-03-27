import { apiClient } from './apiClient';

export const agentService = {
  async health() {
    const { data } = await apiClient.get('/agent/health');
    return data;
  },

  async chat(userInput) {
    const { data } = await apiClient.post('/agent/chat', { user_input: userInput });
    return data;
  },
};
