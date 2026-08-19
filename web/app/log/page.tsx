"use client";

import { useState } from "react";
import Link from "next/link";
import { Card } from "@/components/Card";
import { api } from "@/lib/api";
import type { ExerciseEntry, SessionType } from "@/lib/types";

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

type SetRow = {
  set_number: number;
  reps: string;
  weight_kg: string;
};

type ExerciseRow = {
  name: string;
  sets: SetRow[];
};

function emptyExercise(): ExerciseRow {
  return {
    name: "",
    sets: [{ set_number: 1, reps: "", weight_kg: "" }],
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
          sets: [...ex.sets, { set_number: next, reps: "", weight_kg: "" }],
        };
      }),
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    const payloadExercises: ExerciseEntry[] = exercises
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
        })),
      }));

    try {
      await api.createWorkout({
        date,
        session_type: sessionType,
        title: title || `${sessionType} session`,
        duration_minutes: duration ? Number(duration) : null,
        notes: notes || null,
        exercises: payloadExercises,
      });
      setSuccess(true);
      setTitle("");
      setNotes("");
      setDuration("");
      setExercises([emptyExercise()]);
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
        <p className="mt-1 text-zinc-400">Add exercises and sets — no JSON required.</p>
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

        {exercises.map((exercise, exIdx) => (
          <Card key={exIdx} title={`Exercise ${exIdx + 1}`}>
            <input
              value={exercise.name}
              onChange={(e) => updateExercise(exIdx, { name: e.target.value })}
              placeholder="Back Squat"
              className="mb-4 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2"
            />
            <div className="space-y-2">
              <div className="grid grid-cols-4 gap-2 text-xs text-zinc-500 px-1">
                <span>Set</span>
                <span>Weight (kg)</span>
                <span>Reps</span>
                <span />
              </div>
              {exercise.sets.map((set, setIdx) => (
                <div key={setIdx} className="grid grid-cols-4 gap-2">
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

        <button
          type="button"
          onClick={() => setExercises((prev) => [...prev, emptyExercise()])}
          className="text-sm text-zinc-400 hover:text-white"
        >
          + Add exercise
        </button>

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
