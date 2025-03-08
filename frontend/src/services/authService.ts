import axiosInstance from "../utils/axisConfig.ts"
import { LoginRequest, LoginResponse, RegisterRequest, RegisterResponse } from "../types/auth.types";

export const authService = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    // Convert to FormData as the API expects form data for login
    const formData = new FormData();
    formData.append("username", data.username);
    formData.append("password", data.password);
    
    const response = await axiosInstance.post<LoginResponse>(
      "/auth/login",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },
  
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await axiosInstance.post<RegisterResponse>(
      "/auth/register", 
      data
    );
    return response.data;
  },
  
  logout: async (): Promise<{ message: string }> => {
    const response = await axiosInstance.post<{ message: string }>(
      "/auth/logout"
    );
    return response.data;
  },
  
  refreshToken: async (): Promise<LoginResponse> => {
    const response = await axiosInstance.post<LoginResponse>(
      "/auth/refresh-token"
    );
    return response.data;
  },
};