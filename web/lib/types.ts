export type SessionType =
  | "strength"
  | "running"
  | "crossfit"
  | "hyrox"
  | "olympic_lifting"
  | "skills"
  | "recovery"
  | "other";

export interface ExerciseSet {
  set_number: number;
  reps: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  distance_meters: number | null;
  rpe: number | null;
  set_type: string;
}

export interface ExerciseEntry {
  name: string;
  sets: ExerciseSet[];
  notes?: string | null;
}

export interface TrainingSession {
  id: number;
  date: string;
  session_type: SessionType;
  title: string;
  duration_minutes: number | null;
  notes: string | null;
  source: string;
  wod_format: string | null;
  wod_description: string | null;
  wod_score: string | null;
  exercises: ExerciseEntry[];
  created_at: string | null;
}

export interface Goal {
  id: number;
  category: string;
  title: string;
  target_value: number | null;
  target_unit: string | null;
  exercise_name: string | null;
  deadline: string | null;
  status: string;
  notes: string | null;
  created_at: string | null;
}

export interface WeeklyVolume {
  week_start: string;
  week_end: string;
  total_volume_kg: number;
  session_count: number;
  sessions_by_type: Record<string, number>;
}

export interface PersonalRecord {
  exercise_name: string;
  weight_kg: number;
  reps: number | null;
  date: string;
  session_id: number;
  session_title: string;
}

export interface StrengthHistoryEntry {
  date: string;
  session_id: number;
  session_title: string;
  exercise_name: string;
  best_weight_kg: number;
  reps_at_best: number | null;
}

export interface CoachChatResponse {
  response: string;
  thread_id: string;
}

export interface AccessoryExercise {
  name: string;
  prescription: string;
  notes?: string | null;
}

export interface AccessorySlotPlan {
  slot: string;
  exercises: AccessoryExercise[];
}

export interface AccessoryRecommendation {
  slots: AccessorySlotPlan[];
  rationale: string;
  warnings: string[];
}

export interface AccessoryPlanResponse {
  recommendation: AccessoryRecommendation;
  context_summary: Record<string, unknown>;
}

export interface TrainingSessionCreate {
  date: string;
  session_type: SessionType;
  title: string;
  duration_minutes?: number | null;
  notes?: string | null;
  exercises: ExerciseEntry[];
}
