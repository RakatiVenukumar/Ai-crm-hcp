import { apiClient } from './apiClient';

export const hcpService = {
  async list() {
    const { data } = await apiClient.get('/hcp');
    return data;
  },
};
