// CPython in a module worker.
//
// This file is a transport adapter. It loads Pyodide, installs the pure-Python
// wheel, imports the web bridge, and forwards JSON strings. It contains no
// pricing logic.

let pyodide = null;
let bridge = null;
let initPromise = null;

function postStatus(state, message) {
  self.postMessage({ type: "status", state, message });
}

function errorMessage(error) {
  return error?.message || String(error) || "Unknown Python runtime error.";
}

async function initialize(config) {
  if (initPromise) {
    return initPromise;
  }

  initPromise = (async () => {
    postStatus("loading", "Downloading the Python runtime…");

    const { loadPyodide } = await import(config.pyodideUrl);
    const indexURL = new URL(".", config.pyodideUrl).href;
    pyodide = await loadPyodide({ indexURL });
    const pythonVersion = String(pyodide.runPython("import sys; sys.version.split()[0]"));

    postStatus("loading", "Installing the pricing model…");
    await pyodide.loadPackage("micropip");
    const wheelUrl = JSON.stringify(config.wheelUrl);
    await pyodide.runPythonAsync(`import micropip\nawait micropip.install(${wheelUrl})`);

    bridge = pyodide.pyimport("option_pricer.adapters.web_bridge");
    const contractVersion = String(bridge.contract_version());
    if (contractVersion !== "v1") {
      throw new Error(`Contract mismatch: worker expected v1, wheel has ${contractVersion}.`);
    }

    postStatus("ready", `Python ${pythonVersion} ready.`);
    return { contractVersion, pythonVersion };
  })().catch((error) => {
    initPromise = null;
    throw error;
  });

  return initPromise;
}

async function handlePrice(message) {
  if (!initPromise || !bridge) {
    throw new Error("The Python runtime is not initialized.");
  }
  await initPromise;
  const raw = bridge.handle_request(JSON.stringify(message.request));
  return JSON.parse(raw);
}

self.addEventListener("message", (event) => {
  const message = event.data;
  if (!message || typeof message !== "object") {
    return;
  }

  if (message.type === "init") {
    initialize(message)
      .then((info) => {
        self.postMessage({ type: "ready", id: message.id, ...info });
      })
      .catch((error) => {
        console.error("Pyodide initialization failed", error);
        self.postMessage({
          type: "error",
          id: message.id,
          error: { code: "RUNTIME_ERROR", message: errorMessage(error) },
        });
      });
    return;
  }

  if (message.type === "price") {
    handlePrice(message)
      .then((payload) => {
        self.postMessage({ type: "result", id: message.id, payload });
      })
      .catch((error) => {
        console.error("Pricing bridge failed", error);
        self.postMessage({
          type: "error",
          id: message.id,
          error: { code: "RUNTIME_ERROR", message: errorMessage(error) },
        });
      });
  }
});
