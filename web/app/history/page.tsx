"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { api, formatDuration, formatPace } from "@/lib/api";
import type {
  CrossFitHistorySummary,
  PersonalRecord,
  RepRecordSummary,
  RunningHistoryEntry,
  SessionType,
  StrengthHistoryEntry,
  TrainingSession,
} from "@/lib/types";

const FILTERS: { label: string; value: SessionType | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Strength", value: "strength" },
  { label: "Running", value: "running" },
  { label: "CrossFit", value: "crossfit" },
  { label: "Olympic", value: "olympic_lifting" },
  { label: "HYROX", value: "hyrox" },
];

export default function HistoryPage() {
  const [filter, setFilter] = useState<SessionType | "all">("all");
  const [workouts, setWorkouts] = useState<TrainingSession[]>([]);
  const [prs, setPrs] = useState<PersonalRecord[]>([]);
  const [history, setHistory] = useState<StrengthHistoryEntry[]>([]);
  const [runningHistory, setRunningHistory] = useState<RunningHistoryEntry[]>([]);
  const [repSummary, setRepSummary] = useState<RepRecordSummary | null>(null);
  const [barbellLogbook, setBarbellLogbook] = useState<RepRecordSummary[]>([]);
  const [cfHistory, setCfHistory] = useState<CrossFitHistorySummary | null>(null);
  const [chartExercise, setChartExercise] = useState("Back Squat");
  const [cfWorkoutName, setCfWorkoutName] = useState("Fran");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [workoutList, prList, runs, logbook] = await Promise.all([
          api.listWorkouts({ limit: 100 }),
          api.getPersonalRecords(),
          api.getRunningHistory(12),
          api.getBarbellLogbook(),
        ]);
        setWorkouts(workoutList);
        setPrs(prList);
        setRunningHistory(runs);
        setBarbellLogbook(logbook);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load history");
      }
    }
    load();
  }, []);

  useEffect(() => {
    async function loadStrength() {
      if (!chartExercise.trim()) return;
      try {
        const [entries, summary] = await Promise.all([
          api.getStrengthHistory(chartExercise.trim(), 12),
          api.getRepRecords(chartExercise.trim(), "strength"),
        ]);
        setHistory(entries);
        setRepSummary(summary);
      } catch {
        setHistory([]);
        setRepSummary(null);
      }
    }
    loadStrength();
  }, [chartExercise]);

  useEffect(() => {
    async function loadCf() {
      if (!cfWorkoutName.trim()) return;
      try {
        const summary = await api.getCrossFitHistory(cfWorkoutName.trim(), "rx");
        setCfHistory(summary);
      } catch {
        setCfHistory(null);
      }
    }
    loadCf();
  }, [cfWorkoutName]);

  const filtered =
    filter === "all"
      ? workouts
      : workouts.filter((w) => w.session_type === filter);

  const maxWeight = Math.max(...history.map((h) => h.best_weight_kg), 1);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Training history</h1>
        <p className="mt-1 text-zinc-400">Sport-specific trends and comparisons</p>
      </div>

      {error && <p className="text-red-400">{error}</p>}

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            type="button"
            onClick={() => setFilter(f.value)}
            className={`rounded-lg px-3 py-1.5 text-sm ${
              filter === f.value
                ? "bg-emerald-600 text-white"
                : "bg-zinc-800 text-zinc-400 hover:text-white"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Strength — rep PRs">
          <label className="block text-sm text-zinc-400 mb-3">
            Exercise
            <input
              value={chartExercise}
              onChange={(e) => setChartExercise(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm"
            />
          </label>
          {repSummary ? (
            <ul className="space-y-2 text-sm">
              {repSummary.records.map((record) => (
                <li key={`${record.rep_count}-${record.is_estimated}`} className="flex justify-between">
                  <span>
                    {record.rep_count}RM
                    {record.is_estimated ? " (est.)" : ""}
                  </span>
                  <span className="font-mono text-emerald-400">
                    {record.weight_kg} kg
                    {record.improvement_kg != null && record.improvement_kg > 0
                      ? ` (+${record.improvement_kg})`
                      : ""}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-zinc-500 text-sm">No rep records yet.</p>
          )}
          {history.length > 0 && (
            <div className="mt-4 space-y-2">
              {history.map((entry) => (
                <div key={`${entry.session_id}-${entry.date}`} className="flex items-center gap-3">
                  <span className="w-24 text-xs text-zinc-500 shrink-0">
                    {new Date(entry.date).toLocaleDateString()}
                  </span>
                  <div className="flex-1 h-6 rounded bg-zinc-800 overflow-hidden">
                    <div
                      className="h-full bg-emerald-600/80 rounded"
                      style={{
                        width: `${(entry.best_weight_kg / maxWeight) * 100}%`,
                        minWidth: "4px",
                      }}
                    />
                  </div>
                  <span className="text-sm font-mono text-emerald-400 w-20 text-right">
                    {entry.best_weight_kg} kg
                    {entry.reps_at_best ? ` × ${entry.reps_at_best}` : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Running — recent">
          {runningHistory.length === 0 ? (
            <p className="text-zinc-500 text-sm">No runs logged yet.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {runningHistory.slice(0, 8).map((run) => (
                <li
                  key={run.session_id}
                  className="flex flex-wrap justify-between gap-2 rounded-lg bg-zinc-800/50 px-3 py-2"
                >
                  <span>
                    {new Date(run.date).toLocaleDateString()} — {run.distance_km} km
                  </span>
                  <span className="font-mono text-emerald-400">
                    {formatDuration(run.duration_seconds)}
                    {run.average_pace_sec_per_km
                      ? ` · ${formatPace(run.average_pace_sec_per_km)}`
                      : ""}
                    {run.average_hr ? ` · ${run.average_hr} bpm` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Olympic — barbell logbook">
          {barbellLogbook.length === 0 ? (
            <p className="text-zinc-500 text-sm">No barbell performances yet.</p>
          ) : (
            <ul className="space-y-3 text-sm">
              {barbellLogbook.map((entry) => (
                <li key={entry.movement}>
                  <p className="font-medium">{entry.movement}</p>
                  <ul className="mt-1 space-y-1 text-zinc-400">
                    {entry.records.slice(0, 3).map((r) => (
                      <li key={r.rep_count}>
                        {r.rep_count}RM: {r.weight_kg} kg
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="CrossFit — workout history">
          <label className="block text-sm text-zinc-400 mb-3">
            Workout
            <input
              value={cfWorkoutName}
              onChange={(e) => setCfWorkoutName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm"
            />
          </label>
          {cfHistory && cfHistory.entries.length > 0 ? (
            <ul className="space-y-2 text-sm">
              {cfHistory.entries.map((entry) => (
                <li
                  key={entry.performance_id}
                  className="flex justify-between rounded-lg bg-zinc-800/50 px-3 py-2"
                >
                  <span>{new Date(entry.date).toLocaleDateString()}</span>
                  <span className="font-mono text-emerald-400">
                    {entry.score_type === "time" && entry.score_seconds
                      ? formatDuration(entry.score_seconds)
                      : entry.score_display ??
                        `${entry.score_rounds ?? 0}+${entry.score_reps ?? 0}`}
                    {entry.delta_display ? ` (${entry.delta_display})` : ""}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-zinc-500 text-sm">No scored performances for this workout.</p>
          )}
        </Card>

        <Card title="Legacy PRs (heaviest set)">
          {prs.length === 0 ? (
            <p className="text-zinc-500 text-sm">No PRs yet.</p>
          ) : (
            <ul className="space-y-2">
              {prs.slice(0, 12).map((pr) => (
                <li
                  key={pr.exercise_name}
                  className="flex justify-between rounded-lg bg-zinc-800/50 px-3 py-2 text-sm"
                >
                  <span>{pr.exercise_name}</span>
                  <span className="font-mono text-emerald-400">
                    {pr.weight_kg} kg
                    {pr.reps ? ` × ${pr.reps}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Sessions">
        {filtered.length === 0 ? (
          <p className="text-zinc-500">No sessions for this filter.</p>
        ) : (
          <ul className="divide-y divide-zinc-800">
            {filtered.map((workout) => (
              <li key={workout.id} className="py-3 first:pt-0">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <span className="font-medium">{workout.title}</span>
                    <span className="mx-2 text-zinc-600">·</span>
                    <span className="text-sm text-zinc-400">
                      {new Date(workout.date).toLocaleDateString()}
                    </span>
                  </div>
                  <span className="text-xs uppercase text-zinc-500">{workout.session_type}</span>
                </div>
                {workout.running_metrics && (
                  <p className="mt-1 text-sm text-zinc-500">
                    {workout.running_metrics.distance_km} km ·{" "}
                    {formatDuration(workout.running_metrics.duration_seconds)}
                  </p>
                )}
                {workout.crossfit_performances && workout.crossfit_performances.length > 0 && (
                  <p className="mt-1 text-sm text-zinc-500">
                    {workout.crossfit_performances.map((p) => p.workout_name).join(", ")}
                  </p>
                )}
                {workout.exercises.length > 0 && (
                  <p className="mt-1 text-sm text-zinc-500">
                    {workout.exercises.map((e) => e.name).join(", ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
