import type { User } from "@firebase/auth";

export type AccountRole = "farmer" | "buyer";

export interface AccountProfile {
  uid: string;
  role: AccountRole;
  display_name: string | null;
  phone: string | null;
  state: string | null;
  district_name: string | null;
  farm_size_acres: number | null;
  land_ownership: string | null;
  crops: string[];
  buyer_interests: string[];
  lat: number | null;
  lng: number | null;
  onboarding_completed: boolean;
  questionnaire_completed: boolean;
}

export interface QuestionnaireAnswers {
  display_name: string;
  phone: string;
  state: string;
  district_name: string;
  farm_size_acres: number | null;
  land_ownership: string;
  crops: string[];
  buyer_interests: string[];
  lat: number | null;
  lng: number | null;
  clear_location?: boolean;
  skipped?: boolean;
}

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

async function authenticatedRequest(
  user: User,
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${await user.getIdToken()}`);
  return fetch(`${apiBaseUrl}${path}`, { ...init, headers });
}

async function responseError(response: Response): Promise<Error> {
  let message = `Request failed (HTTP ${response.status}).`;
  try {
    const body: unknown = await response.json();
    if (
      typeof body === "object"
      && body !== null
      && "detail" in body
      && typeof body.detail === "string"
    ) {
      message = body.detail;
    }
  } catch {
    // Keep the HTTP status message when the server response is not JSON.
  }
  return new Error(message);
}

function isAccountProfile(value: unknown): value is AccountProfile {
  if (
    typeof value !== "object"
    || value === null
    || !("uid" in value)
    || !("role" in value)
    || !("questionnaire_completed" in value)
  ) {
    return false;
  }
  return typeof value.uid === "string"
    && (value.role === "farmer" || value.role === "buyer")
    && typeof value.questionnaire_completed === "boolean";
}

export async function fetchAccountProfile(user: User): Promise<AccountProfile | null> {
  const response = await authenticatedRequest(user, "/auth/profile");
  if (response.status === 404) return null;
  if (!response.ok) throw await responseError(response);

  const body: unknown = await response.json();
  if (!isAccountProfile(body)) {
    throw new Error("The account service returned an invalid profile.");
  }
  return body;
}

export async function saveAccountProfile(
  user: User,
  role: AccountRole,
): Promise<AccountProfile> {
  const response = await authenticatedRequest(user, "/auth/profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
  if (!response.ok) throw await responseError(response);

  const body: unknown = await response.json();
  if (!isAccountProfile(body)) {
    throw new Error("The account service returned an invalid profile.");
  }
  return body;
}

export async function saveQuestionnaire(
  user: User,
  answers: QuestionnaireAnswers,
): Promise<AccountProfile> {
  const response = await authenticatedRequest(user, "/auth/questionnaire", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(answers),
  });
  if (!response.ok) throw await responseError(response);

  const body: unknown = await response.json();
  if (!isAccountProfile(body)) {
    throw new Error("The account service returned an invalid profile.");
  }
  return body;
}

export function getApiBaseUrl(): string {
  return apiBaseUrl;
}
