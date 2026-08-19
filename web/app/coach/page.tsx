"use client";

import { useCallback, useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { api } from "@/lib/api";
import {
  getOrCreateCoachThreadId,
  resetCoachThreadId,
  storeCoachThreadId,
} from "@/lib/coach-thread";
import type { AccessoryPlanResponse } from "@/lib/types";

type ChatMessage = {
  role: "user" | "coach";
  text: string;
};

type ChatPersistStatus =
  | "loading"
  | "restored"
  | "new"
  | "saved"
  | "idle";

function formatSavedTime(iso: string | null): string | null {
  if (!iso) return null;
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return null;
  }
}

export default function CoachPage() {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatStatus, setChatStatus] = useState<ChatPersistStatus>("loading");
  const [restoredCount, setRestoredCount] = useState(0);
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);

  const [slotsInput, setSlotsInput] = useState("Tue 30 min\nThu 45 min\nSat 30 min");
  const [accessoryNotes, setAccessoryNotes] = useState("");
  const [accessoryResult, setAccessoryResult] = useState<AccessoryPlanResponse | null>(null);
  const [accessoryLoading, setAccessoryLoading] = useState(false);

  const loadHistory = useCallback(async (id: string) => {
    setChatStatus("loading");
    try {
      const history = await api.getCoachThreadMessages(id);
      if (history.length > 0) {
        setMessages(
          history.map((msg) => ({
            role: msg.role === "user" ? "user" : "coach",
            text: msg.content,
          })),
        );
        setRestoredCount(history.length);
        const last = history[history.length - 1];
        setLastSavedAt(last.created_at ?? null);
        setChatStatus("restored");
      } else {
        setMessages([]);
        setRestoredCount(0);
        setLastSavedAt(null);
        setChatStatus("new");
      }
    } catch {
      setChatStatus("new");
    }
  }, []);

  useEffect(() => {
    const id = getOrCreateCoachThreadId();
    setThreadId(id);
    loadHistory(id);
  }, [loadHistory]);

  useEffect(() => {
    if (chatStatus !== "saved") return;
    const timer = window.setTimeout(() => setChatStatus("idle"), 3000);
    return () => window.clearTimeout(timer);
  }, [chatStatus]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading || !threadId) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);
    setError(null);

    try {
      const { response, thread_id } = await api.coachChat(userText, threadId);
      if (thread_id !== threadId) {
        storeCoachThreadId(thread_id);
        setThreadId(thread_id);
      }
      setMessages((prev) => [...prev, { role: "coach", text: response }]);
      setLastSavedAt(new Date().toISOString());
      setChatStatus("saved");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Coach request failed");
    } finally {
      setLoading(false);
    }
  }

  function startNewConversation() {
    const id = resetCoachThreadId();
    setThreadId(id);
    setMessages([]);
    setRestoredCount(0);
    setLastSavedAt(null);
    setAccessoryResult(null);
    setError(null);
    setChatStatus("new");
  }

  async function generateAccessoryPlan(force = false) {
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
      const result = await api.coachAccessories(slots, accessoryNotes || undefined, force);
      setAccessoryResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Accessory plan failed");
    } finally {
      setAccessoryLoading(false);
    }
  }

  const savedTimeLabel = formatSavedTime(lastSavedAt);

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div className="space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-white">AI Coach</h1>
            <p className="mt-1 text-zinc-400">
              Conversations are saved automatically and restored when you return.
            </p>
          </div>
          <button
            type="button"
            onClick={startNewConversation}
            className="rounded-lg border border-zinc-600 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800"
          >
            New conversation
          </button>
        </div>

        <div
          className={`rounded-lg border px-3 py-2 text-sm ${
            chatStatus === "saved"
              ? "border-emerald-600/50 bg-emerald-900/20 text-emerald-300"
              : chatStatus === "restored"
                ? "border-zinc-700 bg-zinc-800/50 text-zinc-300"
                : chatStatus === "loading"
                  ? "border-zinc-700 bg-zinc-800/30 text-zinc-500"
                  : "border-zinc-700/80 bg-zinc-900/40 text-zinc-400"
          }`}
        >
          {chatStatus === "loading" && "Loading saved conversation…"}
          {chatStatus === "restored" && (
            <>
              <span className="text-emerald-400">● Restored</span>
              {" "}
              {restoredCount} saved message{restoredCount === 1 ? "" : "s"}
              {savedTimeLabel ? ` · last saved ${savedTimeLabel}` : ""}
            </>
          )}
          {chatStatus === "new" && (
            <>New conversation — your messages will be saved after each reply.</>
          )}
          {chatStatus === "saved" && (
            <>
              <span className="text-emerald-400">● Saved</span>
              {" "}
              Conversation updated
              {savedTimeLabel ? ` · ${savedTimeLabel}` : ""}
            </>
          )}
          {chatStatus === "idle" && restoredCount > 0 && savedTimeLabel && (
            <>
              Conversation saved · last updated {savedTimeLabel}
            </>
          )}
          {chatStatus === "idle" && restoredCount === 0 && (
            <>Messages save automatically when the coach replies.</>
          )}
        </div>

        <Card className="min-h-[420px] flex flex-col">
          <div className="flex-1 space-y-4 overflow-y-auto max-h-[360px] pr-2">
            {messages.length === 0 && chatStatus !== "loading" && (
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
              disabled={loading || !threadId}
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
            Plans are saved for this week — regenerate only when your training changes.
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
            onClick={() => generateAccessoryPlan(false)}
            disabled={accessoryLoading}
            className="mt-4 w-full rounded-lg bg-zinc-700 py-2 text-sm font-medium hover:bg-zinc-600 disabled:opacity-50"
          >
            {accessoryLoading ? "Generating…" : "Generate accessory plan"}
          </button>
          <button
            type="button"
            onClick={() => generateAccessoryPlan(true)}
            disabled={accessoryLoading}
            className="mt-2 w-full rounded-lg border border-zinc-600 py-2 text-sm text-zinc-300 hover:bg-zinc-800 disabled:opacity-50"
          >
            Force regenerate
          </button>
        </Card>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        {accessoryResult && (
          <Card
            title={
              accessoryResult.from_cache
                ? "Recommendation (saved)"
                : "Recommendation (new)"
            }
          >
            <p className="mb-3 text-xs text-zinc-500">
              {accessoryResult.from_cache
                ? "● Loaded from saved plan — no new AI call"
                : "● New plan generated and saved for this week"}
              {accessoryResult.plan_id != null && (
                <span className="ml-2 text-zinc-600">plan #{accessoryResult.plan_id}</span>
              )}
            </p>
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
