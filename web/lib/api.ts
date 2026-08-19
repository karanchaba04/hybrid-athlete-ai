import type {
  AccessoryPlanResponse,
  CoachChatResponse,
  Goal,
  PersonalRecord,
  StrengthHistoryEntry,
  TrainingSession,
  TrainingSessionCreate,
  WeeklyVolume,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail ?? response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return response.json() as Promise<T>;
}

export const api = {
  listWorkouts: (params?: { session_type?: string; limit?: number }) => {
    const search = new URLSearchParams();
    if (params?.session_type) search.set("session_type", params.session_type);
    if (params?.limit) search.set("limit", String(params.limit));
    const q = search.toString();
    return request<TrainingSession[]>(`/workouts${q ? `?${q}` : ""}`);
  },

  createWorkout: (payload: TrainingSessionCreate) =>
    request<TrainingSession>("/workouts", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listGoals: (status?: string) =>
    request<Goal[]>(`/goals${status ? `?status=${status}` : ""}`),

  getWeeklyVolume: () => request<WeeklyVolume>("/analytics/weekly-volume"),

  getPersonalRecords: () => request<PersonalRecord[]>("/analytics/prs"),

  getStrengthHistory: (exerciseName: string, weeks = 12) =>
    request<StrengthHistoryEntry[]>(
      `/analytics/strength-history?exercise_name=${encodeURIComponent(exerciseName)}&weeks=${weeks}`,
    ),

  coachChat: (message: string, threadId: string) =>
    request<CoachChatResponse>("/coach/chat", {
      method: "POST",
      body: JSON.stringify({ message, thread_id: threadId }),
    }),

  coachAccessories: (availableSlots: string[], notes?: string) =>
    request<AccessoryPlanResponse>("/coach/accessories", {
      method: "POST",
      body: JSON.stringify({ available_slots: availableSlots, notes }),
    }),
};
