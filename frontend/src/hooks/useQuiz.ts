import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useState } from 'react';
import { 
  fetchMyQuizzes, 
  fetchQuizById,
  fetchQuizAttempts,
  fetchQuizAttempt,
  submitQuizAttempt,
  createQuiz,
  deleteQuiz,
  updateQuizAnswer,
  clearCurrentQuiz,
  clearQuizResult,
  resetError
} from "../store/slices/quizSlice";
import { RootState } from "../store/store";
import { QuizAttemptRequest } from "../types/quiz.types";
import type { FormValues } from '../components/quiz/QuizCreator';
import { quizService } from "../services/quizService";

export const useQuiz = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { 
    quizzes, 
    currentQuiz, 
    quizResult, 
    quizAttempts,
    isLoading: reduxIsLoading, 
    error: reduxError 
  } = useSelector((state: RootState) => state.quiz);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getMyQuizzes = async () => {
    try {
      await dispatch(fetchMyQuizzes()).unwrap();
      return true;
    } catch (error) {
      toast.error("Failed to fetch quizzes", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const getQuizById = async (quizId: string) => {
    try {
      await dispatch(fetchQuizById(quizId)).unwrap();
      return true;
    } catch (error) {
      toast.error("Failed to fetch quiz", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const getQuizAttempts = async (quizId: string) => {
    try {
      await dispatch(fetchQuizAttempts(quizId)).unwrap();
      return true;
    } catch (error) {
      toast.error("Failed to fetch quiz attempts", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const getQuizAttempt = async (attemptId: string) => {
    try {
      await dispatch(fetchQuizAttempt(attemptId)).unwrap();
      return true;
    } catch (error) {
      toast.error("Failed to fetch attempt results", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const attemptQuiz = async (attemptData: QuizAttemptRequest) => {
    try {
      const res = await dispatch(submitQuizAttempt(attemptData)).unwrap();
      return res; 
    } catch (error) {
      toast.error("Failed to submit quiz attempt", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const createNewQuiz = async (originalValues: FormValues, transformedValues: Record<string, any>) => {
    setIsLoading(true);
    setError(null);

    try {
      // Using quizService to send request with tokens via axiosInstance
      const responseData = await quizService.createQuiz(transformedValues);
      toast.success("Quiz created successfully!", {
        description: "Your quiz is now available in My Quizzes.",
      });
      return responseData.quiz_id;
    } catch (err: any) {
      console.error('Error creating quiz:', err);
      setError(err.response?.data?.detail || 'Failed to create quiz');
      toast.error("Failed to create quiz", {
        description: err.response?.data?.detail || "Please try again later.",
      });
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const removeQuiz = async (quizId: string) => {
    try {
      await dispatch(deleteQuiz(quizId)).unwrap();
      toast.success("Quiz deleted successfully!");
      return true;
    } catch (error) {
      toast.error("Failed to delete quiz", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const setAnswer = (questionId: string, choiceId: string) => {
    dispatch(updateQuizAnswer({ questionId, choiceId }));
  };

  const resetQuiz = () => {
    dispatch(clearCurrentQuiz());
  };

  const resetResult = () => {
    dispatch(clearQuizResult());
  };

  const clearError = () => {
    dispatch(resetError());
  };

  return {
    quizzes,
    currentQuiz,
    quizResult,
    quizAttempts,
    isLoading: reduxIsLoading || isLoading,
    error: reduxError || error,
    getMyQuizzes,
    getQuizById,
    getQuizAttempts,
    getQuizAttempt,
    attemptQuiz,
    createNewQuiz,
    removeQuiz,
    setAnswer,
    resetQuiz,
    resetResult,
    clearError,
  };
};