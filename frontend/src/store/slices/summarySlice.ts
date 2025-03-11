import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { summaryService } from "../../services/summaryService";
import { Summary, SummaryRequest, SummaryResponse } from "../../types/summary.types";

interface SummaryState {
  summaries: Summary[];
  currentSummary: Summary | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: SummaryState = {
  summaries: [],
  currentSummary: null,
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchMySummaries = createAsyncThunk(
  "summary/fetchMySummaries",
  async (_, { rejectWithValue }) => {
    try {
      const response = await summaryService.getMySummaries();
      return response.summaries;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to fetch summaries");
    }
  }
);

export const fetchSummaryById = createAsyncThunk(
  "summary/fetchSummaryById",
  async (summaryId: string, { rejectWithValue }) => {
    try {
      const response = await summaryService.getSummaryById(summaryId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to fetch summary");
    }
  }
);

export const createSummary = createAsyncThunk(
  "summary/createSummary",
  async (summaryData: SummaryRequest, { rejectWithValue }) => {
    try {
      const response = await summaryService.createSummary(summaryData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to create summary");
    }
  }
);

export const deleteSummary = createAsyncThunk(
  "summary/deleteSummary",
  async (summaryId: string, { rejectWithValue }) => {
    try {
      await summaryService.deleteSummary(summaryId);
      return summaryId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to delete summary");
    }
  }
);

const summarySlice = createSlice({
  name: "summary",
  initialState,
  reducers: {
    setCurrentSummary: (state, action: PayloadAction<Summary>) => {
      state.currentSummary = action.payload;
    },
    clearCurrentSummary: (state) => {
      state.currentSummary = null;
    },
    resetError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch My Summaries
    builder.addCase(fetchMySummaries.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchMySummaries.fulfilled, (state, action) => {
      state.isLoading = false;
      state.summaries = action.payload;
    });
    builder.addCase(fetchMySummaries.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Fetch Summary By Id
    builder.addCase(fetchSummaryById.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchSummaryById.fulfilled, (state, action) => {
      state.isLoading = false;
      state.currentSummary = action.payload;
    });
    builder.addCase(fetchSummaryById.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Create Summary
    builder.addCase(createSummary.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(createSummary.fulfilled, (state) => {
      state.isLoading = false;
    });
    builder.addCase(createSummary.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Delete Summary
    builder.addCase(deleteSummary.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(deleteSummary.fulfilled, (state, action) => {
      state.isLoading = false;
      state.summaries = state.summaries.filter(summary => summary.summary_id !== action.payload);
    });
    builder.addCase(deleteSummary.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
  },
});

export const { 
  setCurrentSummary, 
  clearCurrentSummary,
  resetError,
} = summarySlice.actions;

export default summarySlice.reducer;