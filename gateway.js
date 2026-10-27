// The only JavaScript that knows how to reach Python.
//
// The gateway owns the worker lifecycle, the startup timeout, and the tiny
// request/response protocol. It knows nothing about option pricing.

const CONTRACT_VERSION = "v1";
const BUILD_INFO_URL = new URL("./build-info.json", import.meta.url);
const INIT_TIMEOUT_MS = 90_000;
const REQUEST_TIMEOUT_MS = 20_000;

export function createPyodideGateway({ onStatus = () => {} } = {}) {
  let worker = null;
  let initPromise = null;
  let nextId = 1;
  let disposed = false;
  const pending = new Map();

  function emit(status) {
    onStatus(status);
  }

  function ensureWorker() {
    if (disposed) {
      throw new Error("The pricing gateway has been disposed.");
    }
    if (worker) {
      return worker;
    }
    if (typeof Worker === "undefined") {
      throw new Error("This browser does not support Web Workers.");
    }

    worker = new Worker(new URL("./pyodide-worker.js", import.meta.url), {
      type: "module",
    });
    worker.addEventListener("message", onWorkerMessage);
    worker.addEventListener("error", onWorkerError);
    worker.addEventListener("messageerror", onWorkerError);
    return worker;
  }

  function onWorkerMessage(event) {
    const message = event.data;
    if (!message || typeof message !== "object") {
      return;
    }
    if (message.type === "status") {
      emit({
        state: message.state ?? "loading",
        message: message.message ?? "Loading Python runtime…",
      });
      return;
    }

    const entry = pending.get(message.id);
    if (!entry) {
      return;
    }
    pending.delete(message.id);
    window.clearTimeout(entry.timer);

    if (message.type === "error") {
      entry.reject(new Error(message.error?.message ?? "Python runtime error."));
      return;
    }
    entry.resolve(message);
  }

  function onWorkerError(event) {
    const message = event?.message || "The Python worker failed to start.";
    emit({ state: "error", message });
    for (const entry of pending.values()) {
      window.clearTimeout(entry.timer);
      entry.reject(new Error(message));
    }
    pending.clear();
    worker?.terminate();
    worker = null;
    initPromise = null;
  }

  function send(message, timeoutMs) {
    const activeWorker = ensureWorker();
    const id = nextId++;
    return new Promise((resolve, reject) => {
      const timer = window.setTimeout(() => {
        pending.delete(id);
        reject(new Error("The Python runtime did not respond in time."));
      }, timeoutMs);

      pending.set(id, { resolve, reject, timer });
      try {
        activeWorker.postMessage({ ...message, id });
      } catch (error) {
        window.clearTimeout(timer);
        pending.delete(id);
        reject(error);
      }
    });
  }

  async function loadBuildInfo() {
    const response = await fetch(BUILD_INFO_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(
        `build-info.json is missing (${response.status}). Run scripts/build_site.py first.`,
      );
    }
    const info = await response.json();
    if (!info.pyodide?.url || !info.wheel) {
      throw new Error("build-info.json is missing the pyodide URL or wheel path.");
    }
    if (info.contract !== CONTRACT_VERSION) {
      throw new Error(
        `Contract mismatch: page ${CONTRACT_VERSION}, build ${info.contract ?? "unknown"}.`,
      );
    }
    return info;
  }

  function init() {
    if (initPromise) {
      return initPromise;
    }

    initPromise = (async () => {
      emit({ state: "loading", message: "Loading build configuration…" });
      const info = await loadBuildInfo();
      ensureWorker();
      emit({ state: "loading", message: "Starting Python runtime…" });
      const ready = await send(
        {
          type: "init",
          pyodideUrl: info.pyodide.url,
          wheelUrl: new URL(info.wheel, BUILD_INFO_URL).href,
        },
        INIT_TIMEOUT_MS,
      );
      emit({ state: "ready", message: "Python runtime ready." });
      return ready;
    })().catch((error) => {
      worker?.terminate();
      worker = null;
      initPromise = null;
      emit({
        state: "error",
        message: error?.message || "Python runtime failed to load.",
      });
      throw error;
    });

    return initPromise;
  }

  async function price(request) {
    await init();
    const response = await send({ type: "price", request }, REQUEST_TIMEOUT_MS);
    return response.payload;
  }

  function restart() {
    if (worker) {
      worker.terminate();
      worker = null;
    }
    for (const entry of pending.values()) {
      window.clearTimeout(entry.timer);
      entry.reject(new Error("The Python runtime was restarted."));
    }
    pending.clear();
    initPromise = null;
    emit({ state: "idle", message: "Python runtime restarted." });
  }

  function warmup() {
    return init();
  }

  function dispose() {
    disposed = true;
    restart();
  }

  return { init, warmup, price, restart, dispose };
}
