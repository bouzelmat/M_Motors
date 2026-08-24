import { apiClient } from "../../api/apiClient";
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
        const response = await apiClient.post<LoginResponse>(
            `${AuthClient.BASE_URL}/login`,
            request,
        );

        return response.data;
    }
}

export const authClient = new AuthClient();