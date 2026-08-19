"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { api } from "@/lib/api";
import type {
  PersonalRecord,
  SessionType,
  StrengthHistoryEntry,
  TrainingSession,
} from "@/lib/types";

const FILTERS: { label: string; value: SessionType | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Strength", value: "strength" },
  { label: "Running", value: "running" },
  { label: "CrossFit", value: "crossfit" },
  { label: "HYROX", value: "hyrox" },
];

export default function HistoryPage() {
  const [filter, setFilter] = useState<SessionType | "all">("all");
  const [workouts, setWorkouts] = useState<TrainingSession[]>([]);
  const [prs, setPrs] = useState<PersonalRecord[]>([]);
  const [history, setHistory] = useState<StrengthHistoryEntry[]>([]);
  const [chartExercise, setChartExercise] = useState("Back Squat");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [workoutList, prList] = await Promise.all([
          api.listWorkouts({ limit: 100 }),
          api.getPersonalRecords(),
        ]);
        setWorkouts(workoutList);
        setPrs(prList);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load history");
      }
    }
    load();
  }, []);

  useEffect(() => {
    async function loadHistory() {
      if (!chartExercise.trim()) return;
      try {
        const entries = await api.getStrengthHistory(chartExercise.trim(), 12);
        setHistory(entries);
      } catch {
        setHistory([]);
      }
    }
    loadHistory();
  }, [chartExercise]);

  const filtered =
    filter === "all"
      ? workouts
      : workouts.filter((w) => w.session_type === filter);

  const maxWeight = Math.max(...history.map((h) => h.best_weight_kg), 1);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Training history</h1>
        <p className="mt-1 text-zinc-400">Sessions, PRs, and strength trends</p>
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
        <Card title="Strength progress">
          <label className="block text-sm text-zinc-400 mb-3">
            Exercise
            <input
              value={chartExercise}
              onChange={(e) => setChartExercise(e.target.value)}
              className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm"
            />
          </label>
          {history.length === 0 ? (
            <p className="text-zinc-500 text-sm">No data for this exercise yet.</p>
          ) : (
            <div className="space-y-2">
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

        <Card title="Recent PRs">
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
