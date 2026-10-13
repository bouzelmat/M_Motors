import axios from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthService } from "../AuthService";
import { authService } from "../AuthService";
import { useAuthStore } from "../../ui/hooks/useAuth";

vi.mock("axios", async () => {
  const actual = await vi.importActual<typeof import("axios")>("axios");
  return {
    ...actual,
    default: {
      ...actual.default,
      create: vi.fn(),
      isAxiosError: actual.default.isAxiosError,
    },
  };
});

describe("AuthService", () => {
  const post = vi.fn();
  const get = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(axios.create).mockReturnValue({ post, get } as never);
  });

  it("envoie une requête d'inscription JSON", async () => {
    post.mockResolvedValue({ data: { id: "user-1", email: "jane@example.com" } });
    const service = new AuthService();
    const result = await service.register({
      email: "jane@example.com",
      password: "Secret123!",
      first_name: "Jane",
      last_name: "Doe",
    });
    expect(post).toHaveBeenCalledWith("/api/v1/auth/register", {
      email: "jane@example.com",
      password: "Secret123!",
      first_name: "Jane",
      last_name: "Doe",
    });
    expect(result.email).toBe("jane@example.com");
  });

  it("envoie la connexion en formulaire urlencoded", async () => {
    post.mockResolvedValue({ data: { access_token: "token", token_type: "bearer" } });
    const result = await new AuthService().login({ username: "jane@example.com", password: "Secret123!" });
    expect(post).toHaveBeenCalledWith(
      "/api/v1/auth/login",
      expect.any(URLSearchParams),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } },
    );
    const form = post.mock.calls[0][1] as URLSearchParams;
    expect(form.get("username")).toBe("jane@example.com");
    expect(form.get("password")).toBe("Secret123!");
    expect(result.access_token).toBe("token");
  });

  it("récupère l'utilisateur courant avec le bearer token", async () => {
    get.mockResolvedValue({ data: { id: "user-1", email: "jane@example.com", role: "CLIENT" } });
    const result = await new AuthService().getCurrentUser("token");
    expect(get).toHaveBeenCalledWith("/api/v1/auth/me", {
      headers: { Authorization: "Bearer token" },
    });
    expect(result.role).toBe("CLIENT");
  });
});

describe("useAuthStore", () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
    useAuthStore.getState().clearError();
    vi.restoreAllMocks();
  });

  it("gère le token, le profil et la déconnexion", () => {
    useAuthStore.getState().setToken("token");
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    useAuthStore.getState().setUser({ id: "user-1", email: "jane@example.com", role: "CLIENT" } as never);
    expect(useAuthStore.getState().user?.email).toBe("jane@example.com");
    useAuthStore.getState().logout();
    expect(useAuthStore.getState()).toMatchObject({ token: null, user: null, isAuthenticated: false, error: null });
  });

  it("enregistre un utilisateur avec les bons paramètres", async () => {
    vi.spyOn(authService, "register").mockResolvedValue({ id: "user-1", email: "jane@example.com" });
    await useAuthStore.getState().register("jane@example.com", "Secret123!", "Jane", "Doe");
    expect(authService.register).toHaveBeenCalledWith({
      email: "jane@example.com",
      password: "Secret123!",
      first_name: "Jane",
      last_name: "Doe",
    });
    expect(useAuthStore.getState().isLoading).toBe(false);
  });

  it("traduit une erreur d'inscription en message d'état", async () => {
    vi.spyOn(authService, "register").mockRejectedValue(new Error("Email déjà utilisé"));
    await expect(useAuthStore.getState().register("jane@example.com", "Secret123!", "Jane", "Doe")).rejects.toThrow();
    expect(useAuthStore.getState().error).toBe("Email déjà utilisé");
    expect(useAuthStore.getState().isLoading).toBe(false);
  });
});
