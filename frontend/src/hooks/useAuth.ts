import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { 
  login as loginAction,
  register as registerAction,
  logout as logoutAction,
  clearError
} from "../store/slices/authSlice";
import { RootState } from "../store/store";
import { LoginRequest, RegisterRequest } from "../types/auth.types";

export const useAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, accessToken, isAuthenticated, isLoading, error } = useSelector(
    (state: RootState) => state.auth
  );

  const login = useCallback(
    async (credentials: LoginRequest) => {
      try {
        await dispatch(loginAction(credentials)).unwrap();
        navigate("/dashboard");
        return true;
      } catch (error) {
        return false;
      }
    },
    [dispatch, navigate]
  );

  const register = useCallback(
    async (userData: RegisterRequest) => {
      try {
        await dispatch(registerAction(userData)).unwrap();
        navigate("/login");
        return true;
      } catch (error) {
        return false;
      }
    },
    [dispatch, navigate]
  );

  const logout = useCallback(async () => {
    await dispatch(logoutAction());
    navigate("/login");
  }, [dispatch, navigate]);

  const resetAuthError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    resetAuthError,
  };
};