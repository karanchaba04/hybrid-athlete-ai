"use client";

import { useState } from "react";
import Link from "next/link";
import { Card } from "@/components/Card";
import { api, parseDurationToSeconds } from "@/lib/api";
import type {
  CrossFitScoreType,
  ExerciseEntry,
  RunningWorkoutType,
  RxStatus,
  SessionType,
} from "@/lib/types";

const SESSION_TYPES: SessionType[] = [
  "strength",
  "running",
  "crossfit",
  "hyrox",
  "olympic_lifting",
  "skills",
  "recovery",
  "other",
];

const RUNNING_TYPES: RunningWorkoutType[] = [
  "easy",
  "zone2",
  "recovery",
  "long_run",
  "tempo",
  "threshold",
  "intervals",
  "race",
  "other",
];

const SCORE_TYPES: CrossFitScoreType[] = [
  "time",
  "rounds_reps",
  "reps",
  "load",
  "calories",
  "distance",
  "points",
];

type SetRow = {
  set_number: number;
  reps: string;
  weight_kg: string;
  successful: boolean;
};

type ExerciseRow = {
  name: string;
  sets: SetRow[];
};

function emptyExercise(): ExerciseRow {
  return {
    name: "",
    sets: [{ set_number: 1, reps: "", weight_kg: "", successful: true }],
  };
}

export default function LogWorkoutPage() {
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(today);
  const [sessionType, setSessionType] = useState<SessionType>("strength");
  const [title, setTitle] = useState("");
  const [duration, setDuration] = useState("");
  const [notes, setNotes] = useState("");
  const [exercises, setExercises] = useState<ExerciseRow[]>([emptyExercise()]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Running fields
  const [runType, setRunType] = useState<RunningWorkoutType>("threshold");
  const [distanceKm, setDistanceKm] = useState("");
  const [runDuration, setRunDuration] = useState("");
  const [avgHr, setAvgHr] = useState("");
  const [maxHr, setMaxHr] = useState("");
  const [trainingLoad, setTrainingLoad] = useState("");
  const [elevation, setElevation] = useState("");
  const [cadence, setCadence] = useState("");

  // CrossFit fields
  const [cfWorkoutName, setCfWorkoutName] = useState("");
  const [cfDescription, setCfDescription] = useState("");
  const [cfScoreType, setCfScoreType] = useState<CrossFitScoreType>("time");
  const [cfScoreSeconds, setCfScoreSeconds] = useState("");
  const [cfScoreRounds, setCfScoreRounds] = useState("");
  const [cfScoreReps, setCfScoreReps] = useState("");
  const [cfScoreLoad, setCfScoreLoad] = useState("");
  const [cfRxStatus, setCfRxStatus] = useState<RxStatus>("rx");

  const isRunning = sessionType === "running";
  const isCrossFit = sessionType === "crossfit";
  const isOlympic = sessionType === "olympic_lifting";
  const showStrengthForm = !isRunning && !isCrossFit;

  function updateExercise(index: number, patch: Partial<ExerciseRow>) {
    setExercises((prev) =>
      prev.map((ex, i) => (i === index ? { ...ex, ...patch } : ex)),
    );
  }

  function addSet(exerciseIndex: number) {
    setExercises((prev) =>
      prev.map((ex, i) => {
        if (i !== exerciseIndex) return ex;
        const next = ex.sets.length + 1;
        return {
          ...ex,
          sets: [
            ...ex.sets,
            { set_number: next, reps: "", weight_kg: "", successful: true },
          ],
        };
      }),
    );
  }

  function buildExercisesPayload(): ExerciseEntry[] {
    return exercises
      .filter((ex) => ex.name.trim())
      .map((ex) => ({
        name: ex.name.trim(),
        sets: ex.sets.map((set, idx) => ({
          set_number: idx + 1,
          reps: set.reps ? Number(set.reps) : null,
          weight_kg: set.weight_kg ? Number(set.weight_kg) : null,
          duration_seconds: null,
          distance_meters: null,
          rpe: null,
          set_type: "normal",
          successful: set.successful,
        })),
      }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const payload: Parameters<typeof api.createWorkout>[0] = {
        date,
        session_type: sessionType,
        title: title || `${sessionType} session`,
        duration_minutes: duration ? Number(duration) : null,
        notes: notes || null,
      };

      if (isRunning) {
        const durationSeconds = parseDurationToSeconds(runDuration);
        if (!distanceKm || !durationSeconds) {
          throw new Error("Distance and duration are required for running");
        }
        payload.running_metrics = {
          distance_km: Number(distanceKm),
          duration_seconds: durationSeconds,
          workout_type: runType,
          average_hr: avgHr ? Number(avgHr) : null,
          max_hr: maxHr ? Number(maxHr) : null,
          training_load: trainingLoad ? Number(trainingLoad) : null,
          elevation_gain_m: elevation ? Number(elevation) : null,
          average_cadence: cadence ? Number(cadence) : null,
        };
        payload.exercises = [];
      } else if (isCrossFit) {
        if (!cfWorkoutName.trim()) {
          throw new Error("Workout name is required for CrossFit");
        }
        const scoreSeconds = cfScoreSeconds
          ? parseDurationToSeconds(cfScoreSeconds)
          : null;
        payload.crossfit_performances = [
          {
            workout_name: cfWorkoutName.trim(),
            workout_description: cfDescription || null,
            score_type: cfScoreType,
            score_seconds: scoreSeconds,
            score_rounds: cfScoreRounds ? Number(cfScoreRounds) : null,
            score_reps: cfScoreReps ? Number(cfScoreReps) : null,
            score_load_kg: cfScoreLoad ? Number(cfScoreLoad) : null,
            rx_status: cfRxStatus,
          },
        ];
        payload.exercises = buildExercisesPayload();
      } else if (showStrengthForm) {
        payload.exercises = buildExercisesPayload();
      }

      await api.createWorkout(payload);
      setSuccess(true);
      setTitle("");
      setNotes("");
      setDuration("");
      setExercises([emptyExercise()]);
      setDistanceKm("");
      setRunDuration("");
      setCfWorkoutName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save workout");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Log workout</h1>
        <p className="mt-1 text-zinc-400">Form adapts to session type.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="text-sm text-zinc-400">Date</span>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
              />
            </label>
            <label className="block">
              <span className="text-sm text-zinc-400">Type</span>
              <select
                value={sessionType}
                onChange={(e) => setSessionType(e.target.value as SessionType)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
              >
                {SESSION_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className="block sm:col-span-2">
              <span className="text-sm text-zinc-400">Title</span>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Lower body strength"
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
              />
            </label>
            <label className="block">
              <span className="text-sm text-zinc-400">Duration (min)</span>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
              />
            </label>
          </div>
        </Card>

        {isRunning && (
          <Card title="Running">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm text-zinc-400">Workout type</span>
                <select
                  value={runType}
                  onChange={(e) => setRunType(e.target.value as RunningWorkoutType)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                >
                  {RUNNING_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Distance (km)</span>
                <input
                  type="number"
                  step="0.01"
                  value={distanceKm}
                  onChange={(e) => setDistanceKm(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Duration (mm:ss)</span>
                <input
                  value={runDuration}
                  onChange={(e) => setRunDuration(e.target.value)}
                  placeholder="41:12"
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Avg HR</span>
                <input
                  type="number"
                  value={avgHr}
                  onChange={(e) => setAvgHr(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Max HR</span>
                <input
                  type="number"
                  value={maxHr}
                  onChange={(e) => setMaxHr(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Training load</span>
                <input
                  type="number"
                  value={trainingLoad}
                  onChange={(e) => setTrainingLoad(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Elevation (m)</span>
                <input
                  type="number"
                  value={elevation}
                  onChange={(e) => setElevation(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Cadence (spm)</span>
                <input
                  type="number"
                  value={cadence}
                  onChange={(e) => setCadence(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
            </div>
          </Card>
        )}

        {isCrossFit && (
          <Card title="CrossFit WOD">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block sm:col-span-2">
                <span className="text-sm text-zinc-400">Workout name</span>
                <input
                  value={cfWorkoutName}
                  onChange={(e) => setCfWorkoutName(e.target.value)}
                  placeholder="Fran"
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block sm:col-span-2">
                <span className="text-sm text-zinc-400">Description</span>
                <textarea
                  value={cfDescription}
                  onChange={(e) => setCfDescription(e.target.value)}
                  rows={2}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                />
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Score type</span>
                <select
                  value={cfScoreType}
                  onChange={(e) => setCfScoreType(e.target.value as CrossFitScoreType)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                >
                  {SCORE_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="text-sm text-zinc-400">Rx / Scaled</span>
                <select
                  value={cfRxStatus}
                  onChange={(e) => setCfRxStatus(e.target.value as RxStatus)}
                  className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                >
                  <option value="rx">Rx</option>
                  <option value="scaled">Scaled</option>
                </select>
              </label>
              {cfScoreType === "time" && (
                <label className="block">
                  <span className="text-sm text-zinc-400">Time (mm:ss)</span>
                  <input
                    value={cfScoreSeconds}
                    onChange={(e) => setCfScoreSeconds(e.target.value)}
                    placeholder="4:48"
                    className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                  />
                </label>
              )}
              {cfScoreType === "rounds_reps" && (
                <>
                  <label className="block">
                    <span className="text-sm text-zinc-400">Rounds</span>
                    <input
                      type="number"
                      value={cfScoreRounds}
                      onChange={(e) => setCfScoreRounds(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                    />
                  </label>
                  <label className="block">
                    <span className="text-sm text-zinc-400">Reps</span>
                    <input
                      type="number"
                      value={cfScoreReps}
                      onChange={(e) => setCfScoreReps(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                    />
                  </label>
                </>
              )}
              {cfScoreType === "reps" && (
                <label className="block">
                  <span className="text-sm text-zinc-400">Reps</span>
                  <input
                    type="number"
                    value={cfScoreReps}
                    onChange={(e) => setCfScoreReps(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                  />
                </label>
              )}
              {cfScoreType === "load" && (
                <label className="block">
                  <span className="text-sm text-zinc-400">Load (kg)</span>
                  <input
                    type="number"
                    value={cfScoreLoad}
                    onChange={(e) => setCfScoreLoad(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                  />
                </label>
              )}
            </div>
          </Card>
        )}

        {showStrengthForm &&
          exercises.map((exercise, exIdx) => (
            <Card key={exIdx} title={`Exercise ${exIdx + 1}`}>
              <input
                value={exercise.name}
                onChange={(e) => updateExercise(exIdx, { name: e.target.value })}
                placeholder="Back Squat"
                className="mb-4 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
              />
              <div className="space-y-2">
                <div className="grid grid-cols-5 gap-2 text-xs text-zinc-500 px-1">
                  <span>Set</span>
                  <span>Weight (kg)</span>
                  <span>Reps</span>
                  {isOlympic && <span>OK</span>}
                  <span />
                </div>
                {exercise.sets.map((set, setIdx) => (
                  <div key={setIdx} className="grid grid-cols-5 gap-2 items-center">
                    <span className="py-2 text-zinc-400">{setIdx + 1}</span>
                    <input
                      type="number"
                      value={set.weight_kg}
                      onChange={(e) => {
                        const sets = [...exercise.sets];
                        sets[setIdx] = { ...sets[setIdx], weight_kg: e.target.value };
                        updateExercise(exIdx, { sets });
                      }}
                      className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                    />
                    <input
                      type="number"
                      value={set.reps}
                      onChange={(e) => {
                        const sets = [...exercise.sets];
                        sets[setIdx] = { ...sets[setIdx], reps: e.target.value };
                        updateExercise(exIdx, { sets });
                      }}
                      className="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
                    />
                    {isOlympic && (
                      <input
                        type="checkbox"
                        checked={set.successful}
                        onChange={(e) => {
                          const sets = [...exercise.sets];
                          sets[setIdx] = { ...sets[setIdx], successful: e.target.checked };
                          updateExercise(exIdx, { sets });
                        }}
                        className="h-4 w-4"
                        title="Successful attempt"
                      />
                    )}
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={() => addSet(exIdx)}
                className="mt-3 text-sm text-emerald-400 hover:text-emerald-300"
              >
                + Add set
              </button>
            </Card>
          ))}

        {showStrengthForm && (
          <button
            type="button"
            onClick={() => setExercises((prev) => [...prev, emptyExercise()])}
            className="text-sm text-zinc-400 hover:text-white"
          >
            + Add exercise
          </button>
        )}

        <label className="block">
          <span className="text-sm text-zinc-400">Notes</span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
          />
        </label>

        {error && <p className="text-red-400">{error}</p>}
        {success && (
          <p className="text-emerald-400">
            Workout saved!{" "}
            <Link href="/" className="underline">Back to dashboard</Link>
          </p>
        )}

        <button
          type="submit"
          disabled={saving}
          className="w-full rounded-lg bg-emerald-600 py-3 font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save workout"}
        </button>
      </form>
    </div>
  );
}
