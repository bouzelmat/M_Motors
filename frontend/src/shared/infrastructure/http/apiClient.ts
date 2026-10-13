/** Configuration du client HTTP partagé de l'application. */
import axios, { InternalAxiosRequestConfig, AxiosResponse } from "axios";
import { useAuthStore } from "../../../auth/ui/hooks/useAuth";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
        "Content-Type": "application/json",
    },
});

const csrfClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

let csrfToken: string | null = null;
let csrfTokenRequest: Promise<string> | null = null;

async function getCsrfToken(): Promise<string> {
    if (csrfToken) return csrfToken;
    if (!csrfTokenRequest) {
        csrfTokenRequest = csrfClient
            .get<{ csrf_token: string }>("/api/v1/auth/csrf")
            .then(({ data }) => {
                csrfToken = data.csrf_token;
                return data.csrf_token;
            })
            .finally(() => {
                csrfTokenRequest = null;
            });
    }
    return csrfTokenRequest;
}

// Ajout automatique du jeton Bearer.
apiClient.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().token;

        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        const method = config.method?.toUpperCase();
        const path = config.url ?? "";
        const mutatesState = ["POST", "PUT", "PATCH", "DELETE"].includes(method ?? "");
        const csrfExempt = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/csrf",
        ].some((exemptPath) => path.startsWith(exemptPath));

        if (mutatesState && !csrfExempt) {
            config.headers["X-CSRF-Token"] = await getCsrfToken();
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
