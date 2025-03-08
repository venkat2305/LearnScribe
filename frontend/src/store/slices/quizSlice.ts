import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { quizService } from "../../services/quizService";
import { Quiz, QuizAttemptRequest, QuizResult } from "../../types/quiz.types";

interface QuizState {
  quizzes: Quiz[];
  currentQuiz: Quiz | null;
  quizResult: QuizResult | null;
  quizAttempts: any[]; // using any[] for attempts; update type as needed.
  isLoading: boolean;
  error: string | null;
}

const initialState: QuizState = {
  quizzes: [],
  currentQuiz: null,
  quizResult: null,
  quizAttempts: [],
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchMyQuizzes = createAsyncThunk(
  "quiz/fetchMyQuizzes",
  async (_, { rejectWithValue }) => {
    try {
      const response = await quizService.getMyQuizzes();
      return response.quizzes;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to fetch quizzes");
    }
  }
);

export const fetchQuizById = createAsyncThunk(
  "quiz/fetchQuizById",
  async (quizId: string, { rejectWithValue }) => {
    try {
      const response = await quizService.getQuizById(quizId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to fetch quiz");
    }
  }
);

export const submitQuizAttempt = createAsyncThunk(
  "quiz/submitQuizAttempt",
  async (attemptData: QuizAttemptRequest, { rejectWithValue }) => {
    try {
      const response = await quizService.submitQuizAttempt(attemptData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to submit quiz attempt");
    }
  }
);

export const createQuiz = createAsyncThunk(
  "quiz/createQuiz",
  async (quizData: any, { rejectWithValue }) => {
    try {
      const response = await quizService.createQuiz(quizData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to create quiz");
    }
  }
);

export const deleteQuiz = createAsyncThunk(
  "quiz/deleteQuiz",
  async (quizId: string, { rejectWithValue }) => {
    try {
      await quizService.deleteQuiz(quizId);
      return quizId;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Failed to delete quiz");
    }
  }
);

// NEW: fetchQuizAttempts by quizId
export const fetchQuizAttempts = createAsyncThunk(
  "quiz/fetchQuizAttempts",
  async (quizId: string, { rejectWithValue }) => {
    try {
      const response = await quizService.getQuizAttempts(quizId);
      return response.attempts;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || "Failed to fetch quiz attempts"
      );
    }
  }
);

// NEW: fetchQuizAttempt by attemptId
export const fetchQuizAttempt = createAsyncThunk(
  "quiz/fetchQuizAttempt",
  async (attemptId: string, { rejectWithValue }) => {
    try {
      const response = await quizService.getQuizAttempt(attemptId);
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || "Failed to fetch quiz attempt"
      );
    }
  }
);

const quizSlice = createSlice({
  name: "quiz",
  initialState,
  reducers: {
    setCurrentQuiz: (state, action: PayloadAction<Quiz>) => {
      state.currentQuiz = action.payload;
    },
    clearCurrentQuiz: (state) => {
      state.currentQuiz = null;
    },
    clearQuizResult: (state) => {
      state.quizResult = null;
    },
    updateQuizAnswer: (state, action: PayloadAction<{ questionId: string; choiceId: string }>) => {
      if (state.currentQuiz) {
        const { questionId, choiceId } = action.payload;
        state.currentQuiz.questions = state.currentQuiz.questions.map(question => 
          question.question_id === questionId  // changed from question.questionId
            ? { ...question, selected_choice_id: choiceId }
            : question
        );
      }
    },
    resetError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch My Quizzes
    builder.addCase(fetchMyQuizzes.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchMyQuizzes.fulfilled, (state, action) => {
      state.isLoading = false;
      state.quizzes = action.payload;
    });
    builder.addCase(fetchMyQuizzes.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Fetch Quiz By Id
    builder.addCase(fetchQuizById.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchQuizById.fulfilled, (state, action) => {
      state.isLoading = false;
      state.currentQuiz = action.payload;
    });
    builder.addCase(fetchQuizById.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Submit Quiz Attempt
    builder.addCase(submitQuizAttempt.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(submitQuizAttempt.fulfilled, (state, action) => {
      state.isLoading = false;
      state.quizResult = action.payload;
    });
    builder.addCase(submitQuizAttempt.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Create Quiz
    builder.addCase(createQuiz.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(createQuiz.fulfilled, (state) => {
      state.isLoading = false;
    });
    builder.addCase(createQuiz.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    // Delete Quiz
    builder.addCase(deleteQuiz.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(deleteQuiz.fulfilled, (state, action) => {
      state.isLoading = false;
      state.quizzes = state.quizzes.filter(quiz => quiz.quiz_id !== action.payload);
    });
    builder.addCase(deleteQuiz.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });

    // NEW extra reducers for quiz attempts
    builder.addCase(fetchQuizAttempts.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchQuizAttempts.fulfilled, (state, action) => {
      state.isLoading = false;
      state.quizAttempts = action.payload;
    });
    builder.addCase(fetchQuizAttempts.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
    
    builder.addCase(fetchQuizAttempt.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchQuizAttempt.fulfilled, (state, action) => {
      state.isLoading = false;
      state.quizResult = action.payload;
    });
    builder.addCase(fetchQuizAttempt.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string;
    });
  },
});

export const { 
  setCurrentQuiz, 
  clearCurrentQuiz,
  clearQuizResult,
  updateQuizAnswer,
  resetError,
} = quizSlice.actions;

export default quizSlice.reducer;