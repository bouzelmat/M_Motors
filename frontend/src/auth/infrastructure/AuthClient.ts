import { apiClient } from "../../shared/infrastructure/http/apiClient";
import { RegisterRequest, RegisterResponse, LoginRequest, LoginResponse } from "./auth.types";

export class AuthClient {
    private static readonly BASE_URL = "/api/v1/auth";

    async register(
        request: RegisterRequest,
    ): Promise<RegisterResponse> {
        const response = await apiClient.post<RegisterResponse>(
            `${AuthClient.BASE_URL}/register`,
            request,
        );

        return response.data;
    }

    async login(
        request: LoginRequest,
    ): Promise<LoginResponse> {
        const formData = new URLSearchParams();
        formData.append('username', request.username);
        formData.append('password', request.password);

        const response = await apiClient.post<LoginResponse>(
            `${AuthClient.BASE_URL}/login`,
            formData,
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            },
        );

        return response.data;
    }
}

export const authClient = new AuthClient();