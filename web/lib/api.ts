import type {
  AccessoryPlanResponse,
  CoachChatResponse,
  CoachMessage,
  CrossFitHistorySummary,
  Goal,
  PersonalRecord,
  RepRecord,
  RepRecordSummary,
  RunningHistoryEntry,
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

  getRepRecords: (movement: string, source: "strength" | "olympic" = "strength") =>
    request<RepRecordSummary>(
      `/analytics/rep-records?movement=${encodeURIComponent(movement)}&source=${source}`,
    ),

  getMovementHistory: (movement: string) =>
    request<RepRecord[]>(
      `/analytics/movement-history?movement=${encodeURIComponent(movement)}`,
    ),

  getBarbellLogbook: () => request<RepRecordSummary[]>("/analytics/barbell-logbook"),

  getRunningHistory: (weeks = 12) =>
    request<RunningHistoryEntry[]>(`/analytics/running-history?weeks=${weeks}`),

  getCrossFitHistory: (workoutName: string, rxStatus?: string) => {
    const params = new URLSearchParams({ workout_name: workoutName });
    if (rxStatus) params.set("rx_status", rxStatus);
    return request<CrossFitHistorySummary>(`/analytics/crossfit/history?${params}`);
  },

  getStrengthHistory: (exerciseName: string, weeks = 12) =>
    request<StrengthHistoryEntry[]>(
      `/analytics/strength-history?exercise_name=${encodeURIComponent(exerciseName)}&weeks=${weeks}`,
    ),

  coachChat: (message: string, threadId: string) =>
    request<CoachChatResponse>("/coach/chat", {
      method: "POST",
      body: JSON.stringify({ message, thread_id: threadId }),
    }),

  coachAccessories: (availableSlots: string[], notes?: string, forceRegenerate = false) =>
    request<AccessoryPlanResponse>("/coach/accessories", {
      method: "POST",
      body: JSON.stringify({
        available_slots: availableSlots,
        notes,
        force_regenerate: forceRegenerate,
      }),
    }),

  getCoachThreadMessages: (threadId: string) =>
    request<CoachMessage[]>(`/coach/threads/${encodeURIComponent(threadId)}/messages`),
};

export function parseDurationToSeconds(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  if (trimmed.includes(":")) {
    const parts = trimmed.split(":").map(Number);
    if (parts.some((p) => Number.isNaN(p))) return null;
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    return null;
  }
  const minutes = Number(trimmed);
  if (Number.isNaN(minutes)) return null;
  return Math.round(minutes * 60);
}

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export function formatPace(paceSecPerKm: number): string {
  const total = Math.round(paceSecPerKm);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}/km`;
}
