"use client";

import { useRef, useState } from "react";
import { Card } from "@/components/Card";
import { api } from "@/lib/api";
import type { AccessoryPlanResponse } from "@/lib/types";

type ChatMessage = {
  role: "user" | "coach";
  text: string;
};

export default function CoachPage() {
  const threadId = useRef(`web-${Date.now()}`);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [slotsInput, setSlotsInput] = useState("Tue 30 min\nThu 45 min\nSat 30 min");
  const [accessoryNotes, setAccessoryNotes] = useState("");
  const [accessoryResult, setAccessoryResult] = useState<AccessoryPlanResponse | null>(null);
  const [accessoryLoading, setAccessoryLoading] = useState(false);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);
    setError(null);

    try {
      const { response } = await api.coachChat(userText, threadId.current);
      setMessages((prev) => [...prev, { role: "coach", text: response }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Coach request failed");
    } finally {
      setLoading(false);
    }
  }

  async function generateAccessoryPlan() {
    setAccessoryLoading(true);
    setError(null);
    const slots = slotsInput
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);

    if (slots.length === 0) {
      setError("Add at least one time slot");
      setAccessoryLoading(false);
      return;
    }

    try {
      const result = await api.coachAccessories(slots, accessoryNotes || undefined);
      setAccessoryResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Accessory plan failed");
    } finally {
      setAccessoryLoading(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">AI Coach</h1>
          <p className="mt-1 text-zinc-400">
            V3.0 — conversational coach with tool access to your training data
          </p>
        </div>

        <Card className="min-h-[420px] flex flex-col">
          <div className="flex-1 space-y-4 overflow-y-auto max-h-[360px] pr-2">
            {messages.length === 0 && (
              <p className="text-zinc-500 text-sm">
                Try: &quot;What are my active goals?&quot; or &quot;How has my squat progressed?&quot;
              </p>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`rounded-lg px-3 py-2 text-sm ${
                  msg.role === "user"
                    ? "bg-emerald-900/30 text-emerald-100 ml-4"
                    : "bg-zinc-800 text-zinc-200 mr-4"
                }`}
              >
                <span className="text-xs uppercase text-zinc-500 block mb-1">
                  {msg.role === "user" ? "You" : "Coach"}
                </span>
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>
            ))}
            {loading && (
              <p className="text-sm text-zinc-500 animate-pulse">Coach is thinking…</p>
            )}
          </div>

          <form onSubmit={sendMessage} className="mt-4 flex gap-2 border-t border-zinc-800 pt-4">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your coach…"
              className="flex-1 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium hover:bg-emerald-500 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </Card>
      </div>

      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold text-white">Accessory planner</h2>
          <p className="mt-1 text-zinc-400">
            V3.1 — structured workflow: gather context → recommend per slot
          </p>
        </div>

        <Card>
          <label className="block text-sm text-zinc-400">
            Available slots (one per line)
            <textarea
              value={slotsInput}
              onChange={(e) => setSlotsInput(e.target.value)}
              rows={4}
              className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm"
            />
          </label>
          <label className="mt-3 block text-sm text-zinc-400">
            Notes (optional)
            <textarea
              value={accessoryNotes}
              onChange={(e) => setAccessoryNotes(e.target.value)}
              placeholder="Shoulder tight, CF has squats twice this week…"
              rows={2}
              className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm"
            />
          </label>
          <button
            type="button"
            onClick={generateAccessoryPlan}
            disabled={accessoryLoading}
            className="mt-4 w-full rounded-lg bg-zinc-700 py-2 text-sm font-medium hover:bg-zinc-600 disabled:opacity-50"
          >
            {accessoryLoading ? "Generating…" : "Generate accessory plan"}
          </button>
        </Card>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        {accessoryResult && (
          <Card title="Recommendation">
            <p className="mb-4 text-sm text-zinc-300 whitespace-pre-wrap">
              {accessoryResult.recommendation.rationale}
            </p>
            {accessoryResult.recommendation.warnings.length > 0 && (
              <ul className="mb-4 text-sm text-amber-400/90 space-y-1">
                {accessoryResult.recommendation.warnings.map((w, i) => (
                  <li key={i}>⚠ {w}</li>
                ))}
              </ul>
            )}
            {accessoryResult.recommendation.slots.map((slot) => (
              <div key={slot.slot} className="mb-4 last:mb-0">
                <h3 className="font-medium text-emerald-400">{slot.slot}</h3>
                <ul className="mt-2 space-y-2 text-sm">
                  {slot.exercises.map((ex) => (
                    <li key={ex.name} className="rounded bg-zinc-800/60 px-3 py-2">
                      <span className="font-medium">{ex.name}</span>
                      <span className="text-zinc-400"> — {ex.prescription}</span>
                      {ex.notes && (
                        <p className="mt-1 text-xs text-zinc-500">{ex.notes}</p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </Card>
        )}
      </div>
    </div>
  );
}
