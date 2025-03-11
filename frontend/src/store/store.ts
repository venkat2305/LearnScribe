import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import quizReducer from "./slices/quizSlice";
import summaryReducer from "./slices/summarySlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    quiz: quizReducer,
    summary: summaryReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;