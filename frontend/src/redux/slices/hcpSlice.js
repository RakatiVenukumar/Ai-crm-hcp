import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { hcpService } from '../../services/hcpService';

export const fetchHcps = createAsyncThunk('hcp/list', async () => {
  return hcpService.list();
});

const hcpSlice = createSlice({
  name: 'hcp',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHcps.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHcps.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchHcps.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to load HCP list';
      });
  },
});

export default hcpSlice.reducer;
