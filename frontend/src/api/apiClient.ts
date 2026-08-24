/** Configuration du client HTTP partagé de l'application. */
import axios, { InternalAxiosRequestConfig, AxiosResponse } from "axios";
import { useAuthStore } from "../auth/ui/hooks/useAuth";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Ajout automatique du jeton Bearer.
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().token;

        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error: unknown) => Promise.reject(error),
);

// Gestion centralisée des réponses HTTP.
apiClient.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: any) => { // 'any' ici est nécessaire car la structure de l'erreur axios dépend de la réponse réseau
        if (error.response?.status === 401) {
            useAuthStore.getState().logout();
            window.location.href = "/login";
        }

        return Promise.reject(error);
    },
);
