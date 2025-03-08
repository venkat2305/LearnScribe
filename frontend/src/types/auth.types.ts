// User Types
export interface User {
    user_id: string;
    username: string;
    email: string;
  }
  
  // Auth State Types
  export interface AuthState {
    user: User | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
  }
  
  // Login Types
  export interface LoginRequest {
    username: string;
    password: string;
  }
  
  export interface LoginResponse {
    access_token: string;
    token_type: string;
  }
  
  // Register Types
  export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
  }
  
  export interface RegisterResponse {
    username: string;
    email: string;
  }