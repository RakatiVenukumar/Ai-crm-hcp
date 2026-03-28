import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { agentService } from '../../services/agentService';

export const checkAgentHealth = createAsyncThunk('agent/health', async () => {
  return agentService.health();
});

export const runAgentChat = createAsyncThunk('agent/chat', async ({ userInput, conversationHistory }) => {
  return agentService.chat(userInput, conversationHistory);
});

const agentSlice = createSlice({
  name: 'agent',
  initialState: {
    health: null,
    loading: false,
    error: null,
    conversationHistory: [],
    lastResponse: null,
  },
  reducers: {
    clearAgentError(state) {
      state.error = null;
    },
    clearConversationHistory(state) {
      state.conversationHistory = [];
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
        const userInput = action.meta.arg.userInput;
        const response = action.payload;
        
        // Add user message to history
        state.conversationHistory.push({
          role: 'user',
          content: userInput,
          timestamp: new Date().toISOString(),
        });
        
        // Add assistant message to history (use response_message if available, otherwise show summary)
        const assistantContent = response?.response_message || 
                                 `Recorded: ${response?.extracted_data?.hcp_name || 'HCP'} - ${response?.extracted_data?.sentiment || 'neutral'}`;
        
        state.conversationHistory.push({
          role: 'assistant',
          content: assistantContent,
          timestamp: new Date().toISOString(),
        });
        
        state.lastResponse = response;
        if (response?.success === false) {
          state.error = response.error || 'Agent could not process the request';
        } else {
          state.error = null;
        }
      })
      .addCase(runAgentChat.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Agent request failed';
      });
  },
});

export const { clearAgentError, clearConversationHistory } = agentSlice.actions;
export default agentSlice.reducer;
