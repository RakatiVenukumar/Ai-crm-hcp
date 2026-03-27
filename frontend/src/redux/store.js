import { configureStore } from '@reduxjs/toolkit';
import agentReducer from './slices/agentSlice';
import interactionReducer from './slices/interactionSlice';
import hcpReducer from './slices/hcpSlice';

export const store = configureStore({
  reducer: {
    agent: agentReducer,
    interaction: interactionReducer,
    hcp: hcpReducer,
  },
});
