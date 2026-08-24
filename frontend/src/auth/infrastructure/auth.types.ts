/** Requête d'inscription. */
export type RegisterRequest = {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
};

/** Réponse d'inscription. */
export type RegisterResponse = {
    id: string;
    email: string;
};

/** Requête de connexion. */
export type LoginRequest = {
    email: string;
    password: string;
};

/** Réponse de connexion. */
export type LoginResponse = {
    access_token: string;
    token_type: string;
};