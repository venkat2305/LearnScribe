import axiosInstance from "../utils/axisConfig.ts";
import { Quiz, QuizAttemptRequest, QuizResult } from "../types/quiz.types";

export const quizService = {
  // Get all quizzes for current user
  getMyQuizzes: async (): Promise<{ quizzes: Quiz[] }> => {
    const response = await axiosInstance.get<{ quizzes: Quiz[] }>("/quiz/myquizzes");
    return response.data;
  },
  
  // Get a specific quiz by ID
  getQuizById: async (quizId: string): Promise<Quiz> => {
    const response = await axiosInstance.get<Quiz>(`/quiz/${quizId}`);
    return response.data;
  },
  
  // Create a new quiz
  createQuiz: async (quizData: any): Promise<{ message: string; quiz_id: string }> => {
    const response = await axiosInstance.post<{ message: string; quiz_id: string }>(
      "/quiz/",
      quizData
    );
    return response.data;
  },
  
  // Submit quiz attempt
  submitQuizAttempt: async (attemptData: QuizAttemptRequest): Promise<QuizResult> => {
    const response = await axiosInstance.post<QuizResult>("/quiz/attempt", attemptData);
    return response.data;
  },
  
  // Get quiz attempts for a specific quiz
  getQuizAttempts: async (quizId: string): Promise<{ attempts: any[] }> => {
    const response = await axiosInstance.get<{ attempts: any[] }>(
      `/quiz/${quizId}/attempts`
    );
    return response.data;
  },
  
  // Get a specific quiz attempt by ID
  getQuizAttempt: async (attemptId: string): Promise<any> => {
    const response = await axiosInstance.get<any>(`/quiz/attempts/${attemptId}`);
    return response.data;
  },
  
  // Delete a quiz
  deleteQuiz: async (quizId: string): Promise<{ message: string }> => {
    const response = await axiosInstance.delete<{ message: string }>(
      `/quiz/${quizId}`
    );
    return response.data;
  },
};