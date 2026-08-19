"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { api } from "@/lib/api";
import type { Goal, TrainingSession, WeeklyVolume } from "@/lib/types";

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function computeRunningKm(workouts: TrainingSession[]): number {
  let meters = 0;
  for (const workout of workouts) {
    for (const exercise of workout.exercises) {
      if (exercise.name.toLowerCase() === "run" || workout.session_type === "running") {
        for (const set of exercise.sets) {
          if (set.distance_meters) meters += set.distance_meters;
        }
      }
    }
  }
  return meters / 1000;
}

export default function DashboardPage() {
  const [volume, setVolume] = useState<WeeklyVolume | null>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [workouts, setWorkouts] = useState<TrainingSession[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [vol, goalList, recent] = await Promise.all([
          api.getWeeklyVolume(),
          api.listGoals("active"),
          api.listWorkouts({ limit: 10 }),
        ]);
        setVolume(vol);
        setGoals(goalList);
        setWorkouts(recent);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load dashboard");
      }
    }
    load();
  }, []);

  const runningKm = computeRunningKm(workouts);
  const strengthSessions = volume?.sessions_by_type?.strength ?? 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
        <p className="mt-1 text-zinc-400">This week at a glance</p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-900 bg-red-950/50 p-4 text-red-200">
          {error}
          <p className="mt-2 text-sm text-red-300/80">
            Is FastAPI running? <code className="text-red-100">uv run hybrid-athlete-ai</code>
          </p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <p className="text-3xl font-semibold text-emerald-400">
            {volume?.session_count ?? "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">Sessions this week</p>
        </Card>
        <Card>
          <p className="text-3xl font-semibold text-emerald-400">
            {runningKm > 0 ? `${runningKm.toFixed(1)} km` : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">Running (recent logged)</p>
        </Card>
        <Card>
          <p className="text-3xl font-semibold text-emerald-400">
            {volume ? `${Math.round(volume.total_volume_kg).toLocaleString()} kg` : "—"}
          </p>
          <p className="mt-1 text-sm text-zinc-400">
            Strength volume · {strengthSessions} strength sessions
          </p>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Current goals">
          {goals.length === 0 ? (
            <p className="text-zinc-500">No active goals yet.</p>
          ) : (
            <ul className="space-y-3">
              {goals.map((goal) => (
                <li
                  key={goal.id}
                  className="flex items-center justify-between rounded-lg bg-zinc-800/50 px-3 py-2"
                >
                  <span className="font-medium">{goal.title}</span>
                  {goal.target_value != null && (
                    <span className="text-sm text-emerald-400">
                      {goal.target_value} {goal.target_unit ?? ""}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Recent training">
          {workouts.length === 0 ? (
            <p className="text-zinc-500">No workouts logged yet.</p>
          ) : (
            <ul className="space-y-2">
              {workouts.slice(0, 6).map((workout) => (
                <li
                  key={workout.id}
                  className="flex items-center justify-between rounded-lg bg-zinc-800/40 px-3 py-2 text-sm"
                >
                  <div>
                    <span className="text-zinc-400">{formatDate(workout.date)}</span>
                    <span className="mx-2 text-zinc-600">·</span>
                    <span>{workout.title}</span>
                  </div>
                  <span className="rounded bg-zinc-700 px-2 py-0.5 text-xs uppercase text-zinc-300">
                    {workout.session_type}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
