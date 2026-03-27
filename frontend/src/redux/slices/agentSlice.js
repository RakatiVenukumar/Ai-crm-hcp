import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { agentService } from '../../services/agentService';

export const checkAgentHealth = createAsyncThunk('agent/health', async () => {
  return agentService.health();
});

export const runAgentChat = createAsyncThunk('agent/chat', async (userInput) => {
  return agentService.chat(userInput);
});

const agentSlice = createSlice({
  name: 'agent',
  initialState: {
    health: null,
    loading: false,
    error: null,
    lastResponse: null,
  },
  reducers: {
    clearAgentError(state) {
      state.error = null;
    },
    clearAgentResponse(state) {
      state.lastResponse = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(checkAgentHealth.fulfilled, (state, action) => {
        state.health = action.payload;
      })
      .addCase(runAgentChat.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(runAgentChat.fulfilled, (state, action) => {
        state.loading = false;
        state.lastResponse = action.payload;
      })
      .addCase(runAgentChat.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Agent request failed';
      });
  },
});

export const { clearAgentError, clearAgentResponse } = agentSlice.actions;
export default agentSlice.reducer;
