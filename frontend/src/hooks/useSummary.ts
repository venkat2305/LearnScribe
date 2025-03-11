import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { 
  fetchMySummaries, 
  fetchSummaryById,
  createSummary as createSummaryAction,
  deleteSummary,
  setCurrentSummary,
  clearCurrentSummary,
  resetError
} from "../store/slices/summarySlice";
import { RootState } from "../store/store";
import { SummaryRequest } from "../types/summary.types";

export const useSummary = () => {
  const dispatch = useDispatch();
  const { summaries, currentSummary, isLoading, error } = useSelector(
    (state: RootState) => state.summary
  );

  const getMySummaries = async () => {
    try {
      await dispatch(fetchMySummaries()).unwrap();
      return true;
    } catch (error) {
      toast.error("Failed to fetch summaries", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const getSummaryById = async (summaryId: string) => {
    try {
      await dispatch(fetchSummaryById(summaryId)).unwrap();
      return true;
    } catch (error) {
      toast.error("Failed to fetch summary", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const createSummary = async (summaryData: SummaryRequest) => {
    try {
      const result = await dispatch(createSummaryAction(summaryData)).unwrap();
      toast.success("Summary created successfully!", {
        description: "Your summary is now available in My Summaries.",
      });
      return result.summary_id;
    } catch (error) {
      toast.error("Failed to create summary", {
        description: error as string || "Please try again later.",
      });
      return null;
    }
  };

  const removeSummary = async (summaryId: string) => {
    try {
      await dispatch(deleteSummary(summaryId)).unwrap();
      toast.success("Summary deleted successfully!");
      return true;
    } catch (error) {
      toast.error("Failed to delete summary", {
        description: error as string || "Please try again later.",
      });
      return false;
    }
  };

  const setSummary = (summary: any) => {
    dispatch(setCurrentSummary(summary));
  };

  const resetSummary = () => {
    dispatch(clearCurrentSummary());
  };

  const clearError = () => {
    dispatch(resetError());
  };

  return {
    summaries,
    currentSummary,
    isLoading,
    error,
    getMySummaries,
    getSummaryById,
    createSummary,
    removeSummary,
    setSummary,
    resetSummary,
    clearError,
  };
};