import { apiClient } from './apiClient';

export const interactionService = {
  async log(payload) {
    const { data } = await apiClient.post('/interaction/log', payload);
    return data;
  },

  async timeline() {
    const { data } = await apiClient.get('/interaction/timeline');
    return data;
  },
};
