// Auth store using Zustand

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';
import { authService } from '../../application/AuthService';
import { UserResponse } from '../../application/dtos';

interface AuthState {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setToken: (token: string) => void;
  setUser: (user: UserResponse) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName: string, lastName: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setToken: (token) => {
        set({ token, isAuthenticated: !!token });
      },

      setUser: (user) => {
        set({ user });
      },

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login({ username: email, password });
          set({ token: response.access_token, isAuthenticated: true });
          
          // Fetch user info
          const user = await authService.getCurrentUser(response.access_token);
          set({ user, isLoading: false });
        } catch (error) {
          set({
            error: axios.isAxiosError(error) && error.response?.status === 401
              ? 'Adresse e-mail ou mot de passe incorrect.'
              : 'La connexion a échoué. Réessayez dans un instant.',
            isLoading: false,
            isAuthenticated: false,
            token: null,
            user: null,
          });
          throw error;
        }
      },

      register: async (email: string, password: string, firstName: string, lastName: string) => {
        set({ isLoading: true, error: null });
        try {
          await authService.register({
            email,
            password,
            first_name: firstName,
            last_name: lastName,
          });
          set({ isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Registration failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        set({
          token: null,
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);

