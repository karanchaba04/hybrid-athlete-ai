const COACH_THREAD_KEY = "hybrid-athlete-coach-thread-id";

export function createCoachThreadId(): string {
  return `web-${Date.now()}`;
}

export function getStoredCoachThreadId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(COACH_THREAD_KEY);
}

export function storeCoachThreadId(threadId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(COACH_THREAD_KEY, threadId);
}

export function getOrCreateCoachThreadId(): string {
  const stored = getStoredCoachThreadId();
  if (stored) return stored;
  const id = createCoachThreadId();
  storeCoachThreadId(id);
  return id;
}

export function resetCoachThreadId(): string {
  const id = createCoachThreadId();
  storeCoachThreadId(id);
  return id;
}
