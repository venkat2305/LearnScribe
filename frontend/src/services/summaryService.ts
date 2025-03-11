import axiosInstance from "../utils/axisConfig";
import { Summary, SummaryRequest, SummaryResponse } from "../types/summary.types";

export const summaryService = {
  // Get all summaries for current user
  getMySummaries: async (): Promise<{ summaries: Summary[] }> => {
    const response = await axiosInstance.get<{ summaries: Summary[] }>("/summary/mysummaries");
    return response.data;
  },
  
  // Get a specific summary by ID
  getSummaryById: async (summaryId: string): Promise<Summary> => {
    const response = await axiosInstance.get<Summary>(`/summary/${summaryId}`);
    return response.data;
  },
  
  // Create a new summary
  createSummary: async (summaryData: SummaryRequest): Promise<SummaryResponse> => {
    const response = await axiosInstance.post<SummaryResponse>(
      "/summary/",
      summaryData
    );
    return response.data;
  },
  
  // Delete a summary
  deleteSummary: async (summaryId: string): Promise<{ message: string }> => {
    const response = await axiosInstance.delete<{ message: string }>(
      `/summary/${summaryId}`
    );
    return response.data;
  },
};