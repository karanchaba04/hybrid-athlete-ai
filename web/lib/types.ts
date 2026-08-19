export type SessionType =
  | "strength"
  | "running"
  | "crossfit"
  | "hyrox"
  | "olympic_lifting"
  | "skills"
  | "recovery"
  | "other";

export type RunningWorkoutType =
  | "easy"
  | "zone2"
  | "recovery"
  | "long_run"
  | "tempo"
  | "threshold"
  | "intervals"
  | "race"
  | "other";

export type CrossFitScoreType =
  | "time"
  | "rounds_reps"
  | "reps"
  | "load"
  | "calories"
  | "distance"
  | "points";

export type RxStatus = "rx" | "scaled";

export interface ExerciseSet {
  set_number: number;
  reps: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  distance_meters: number | null;
  rpe: number | null;
  set_type: string;
  successful?: boolean;
}

export interface ExerciseEntry {
  name: string;
  sets: ExerciseSet[];
  notes?: string | null;
}

export interface RunningMetrics {
  id?: number;
  session_id?: number;
  distance_km: number;
  duration_seconds: number;
  average_pace_sec_per_km?: number | null;
  average_hr?: number | null;
  max_hr?: number | null;
  training_load?: number | null;
  elevation_gain_m?: number | null;
  average_cadence?: number | null;
  workout_type: RunningWorkoutType;
}

export interface CrossFitPerformance {
  id?: number;
  session_id?: number;
  workout_definition_id?: number;
  workout_name: string;
  workout_description?: string | null;
  score_type: CrossFitScoreType;
  score_seconds?: number | null;
  score_reps?: number | null;
  score_rounds?: number | null;
  score_load_kg?: number | null;
  score_calories?: number | null;
  score_distance_m?: number | null;
  score_points?: number | null;
  score_display?: string | null;
  rx_status: RxStatus;
  time_cap_seconds?: number | null;
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
  running_metrics?: RunningMetrics | null;
  crossfit_performances?: CrossFitPerformance[];
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

export interface RepRecord {
  movement: string;
  rep_count: number;
  weight_kg: number;
  is_estimated: boolean;
  date: string;
  session_id: number | null;
  session_title: string | null;
  previous_weight_kg: number | null;
  improvement_kg: number | null;
}

export interface RepRecordSummary {
  movement: string;
  records: RepRecord[];
  heaviest_successful_set_kg: number | null;
  estimated_1rm_kg: number | null;
  recent_history: RepRecord[];
}

export interface StrengthHistoryEntry {
  date: string;
  session_id: number;
  session_title: string;
  exercise_name: string;
  best_weight_kg: number;
  reps_at_best: number | null;
}

export interface RunningHistoryEntry {
  date: string;
  session_id: number;
  session_title: string;
  distance_km: number;
  duration_seconds: number;
  average_pace_sec_per_km: number | null;
  average_hr: number | null;
  max_hr: number | null;
  training_load: number | null;
  elevation_gain_m: number | null;
  average_cadence: number | null;
  workout_type: RunningWorkoutType;
}

export interface CrossFitHistoryEntry {
  date: string;
  session_id: number;
  performance_id: number;
  workout_name: string;
  score_type: CrossFitScoreType;
  score_seconds: number | null;
  score_reps: number | null;
  score_rounds: number | null;
  score_load_kg: number | null;
  score_calories: number | null;
  score_distance_m: number | null;
  score_points: number | null;
  score_display: string | null;
  rx_status: RxStatus;
  delta_from_previous: number | null;
  delta_from_first: number | null;
  delta_display: string | null;
}

export interface CrossFitHistorySummary {
  workout_name: string;
  rx_status: RxStatus;
  score_type: CrossFitScoreType;
  entries: CrossFitHistoryEntry[];
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
  plan_id?: number | null;
  from_cache?: boolean;
  context_hash?: string | null;
}

export interface CoachMessage {
  id: number;
  thread_id: string;
  role: string;
  content: string;
  created_at: string | null;
}

export interface TrainingSessionCreate {
  date: string;
  session_type: SessionType;
  title: string;
  duration_minutes?: number | null;
  notes?: string | null;
  exercises?: ExerciseEntry[];
  running_metrics?: RunningMetrics | null;
  crossfit_performances?: CrossFitPerformance[];
}
