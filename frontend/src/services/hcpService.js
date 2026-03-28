import { apiClient } from './apiClient';

export const hcpService = {
  async list() {
    const { data } = await apiClient.get('/hcp');
    return data;
  },

  async create(payload) {
    const { data } = await apiClient.post('/hcp', payload);
    return data;
  },
};
