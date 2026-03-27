import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { interactionService } from '../../services/interactionService';

export const saveInteraction = createAsyncThunk('interaction/save', async (payload) => {
  return interactionService.log(payload);
});

export const fetchTimeline = createAsyncThunk('interaction/timeline', async () => {
  return interactionService.timeline();
});

const interactionSlice = createSlice({
  name: 'interaction',
  initialState: {
    loading: false,
    error: null,
    savedInteraction: null,
    timeline: [],
  },
  reducers: {
    clearSavedInteraction(state) {
      state.savedInteraction = null;
    },
    clearInteractionError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(saveInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(saveInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.savedInteraction = action.payload;
      })
      .addCase(saveInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to save interaction';
      })
      .addCase(fetchTimeline.fulfilled, (state, action) => {
        state.timeline = action.payload;
      });
  },
});

export const { clearSavedInteraction, clearInteractionError } = interactionSlice.actions;
export default interactionSlice.reducer;
