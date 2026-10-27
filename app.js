import { createPyodideGateway } from "./gateway.js";

const CONTRACT_VERSION = "v1";

const form = document.getElementById("pricing-form");
const powerLawFields = document.getElementById("power-law-fields");
const bsmFields = document.getElementById("bsm-fields");
const powerLawFormula = document.getElementById("power-law-formula");
const bsmFormula = document.getElementById("bsm-formula");
const formulaCall = document.getElementById("formula-call");
const formulaPut = document.getElementById("formula-put");
const calculateButton = document.getElementById("calculate");
const resultLabel = document.getElementById("result-label");
const resultValue = document.getElementById("result");
const errorMessage = document.getElementById("error");
const runtimeStatus = document.getElementById("runtime-status");
const retryRuntime = document.getElementById("retry-runtime");
const buildVersion = document.getElementById("build-version");
const buildMeta = document.getElementById("build-meta");
const anchorPriceSymbol = document.getElementById("anchor-price-symbol");
const anchorStrikeHint = document.getElementById("anchor-strike-hint");
const targetStrikeHint = document.getElementById("target-strike-hint");

const methodInputs = [...document.querySelectorAll('input[name="method"]')];
const optionTypeInputs = [...document.querySelectorAll('input[name="option_type"]')];
const powerLawInputs = [
  document.getElementById("anchor_strike"),
  document.getElementById("target_strike"),
  document.getElementById("anchor_price"),
  document.getElementById("alpha"),
];
const bsmInputs = [
  document.getElementById("strike"),
  document.getElementById("time_to_expiry"),
  document.getElementById("rate"),
  document.getElementById("volatility"),
];
const allInputs = [document.getElementById("spot"), ...powerLawInputs, ...bsmInputs];

let formVersion = 0;

class FormError extends Error {
  constructor(message, field) {
    super(message);
    this.field = field;
  }
}

const gateway = createPyodideGateway({
  onStatus: (status) => setRuntimeStatus(status),
});

function selectedValue(inputs) {
  return inputs.find((input) => input.checked)?.value ?? "";
}

function isPowerLaw() {
  return selectedValue(methodInputs) === "power_law";
}

function selectedOptionType() {
  return selectedValue(optionTypeInputs) || "call";
}

function syncForm({ resetOutput = true } = {}) {
  const powerLaw = isPowerLaw();
  const optionType = selectedOptionType();
  const call = optionType === "call";

  powerLawFields.hidden = !powerLaw;
  bsmFields.hidden = powerLaw;
  powerLawFormula.hidden = !powerLaw;
  bsmFormula.hidden = powerLaw;
  formulaCall.hidden = !call;
  formulaPut.hidden = call;

  for (const input of powerLawInputs) {
    input.disabled = !powerLaw;
    input.required = powerLaw;
  }
  for (const input of bsmInputs) {
    input.disabled = powerLaw;
    input.required = !powerLaw;
  }

  anchorPriceSymbol.textContent = call ? "C(K1)" : "P(K1)";
  anchorStrikeHint.textContent = call ? "Above spot for calls." : "Below spot for puts.";
  targetStrikeHint.textContent = call ? "Above spot for calls." : "Below spot for puts.";

  calculateButton.textContent = buttonLabel();
  if (resetOutput) {
    clearOutput();
  }
  formVersion += 1;
}

function buttonLabel() {
  const call = selectedOptionType() === "call";
  if (isPowerLaw()) {
    return call ? "Calculate C(K2)" : "Calculate P(K2)";
  }
  return call ? "Calculate BSM call" : "Calculate BSM put";
}

function clearOutput() {
  resultLabel.textContent = "Result";
  resultValue.textContent = "—";
  errorMessage.hidden = true;
  errorMessage.textContent = "";
  delete errorMessage.dataset.code;
  for (const input of allInputs) {
    input.removeAttribute("aria-invalid");
  }
}

function setRuntimeStatus(status) {
  const state = status?.state ?? "idle";
  runtimeStatus.dataset.state = state;
  runtimeStatus.textContent = status?.message ?? "Python runtime not loaded yet.";
  retryRuntime.hidden = state !== "error";
}

function setBusy(busy) {
  form.setAttribute("aria-busy", String(busy));
  calculateButton.disabled = busy;
  calculateButton.textContent = busy ? "Calculating…" : buttonLabel();
}

function numberValue(id) {
  const input = document.getElementById(id);
  const raw = input.value.trim();
  const label = input.labels?.[0]?.textContent?.trim() || id;
  if (!raw) {
    throw new FormError(`${label} is required.`, id);
  }
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new FormError(`${label} must be a finite number.`, id);
  }
  return value;
}

function buildRequest() {
  const method = isPowerLaw() ? "power_law" : "black_scholes";
  const request = {
    version: CONTRACT_VERSION,
    method,
    option_type: selectedOptionType(),
    spot: numberValue("spot"),
  };

  if (method === "power_law") {
    request.anchor_strike = numberValue("anchor_strike");
    request.target_strike = numberValue("target_strike");
    request.anchor_price = numberValue("anchor_price");
    request.alpha = numberValue("alpha");
  } else {
    request.strike = numberValue("strike");
    request.time_to_expiry = numberValue("time_to_expiry");
    request.rate = numberValue("rate");
    request.volatility = numberValue("volatility");
  }

  return request;
}

function showError(message, field) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
  if (field) {
    const input = document.getElementById(field);
    if (input) {
      input.setAttribute("aria-invalid", "true");
      input.focus();
    }
  }
}

function renderResult(response) {
  const call = response.option_type === "call";
  let label;
  if (response.method === "power_law") {
    label = call ? "C(K2)" : "P(K2)";
  } else {
    label = call ? "BSM call" : "BSM put";
  }
  resultLabel.textContent = label;
  resultValue.textContent = formatPrice(response.price);
}

function formatPrice(price) {
  if (price !== 0 && Math.abs(price) < 1e-6) {
    return price.toExponential(6);
  }
  return price.toFixed(6);
}

async function onCalculate(event) {
  event.preventDefault();
  clearOutput();

  let request;
  try {
    request = buildRequest();
  } catch (error) {
    if (error instanceof FormError) {
      showError(error.message, error.field);
      return;
    }
    showError("Could not read the form inputs.");
    console.error(error);
    return;
  }

  const versionAtSubmit = formVersion;
  setBusy(true);

  try {
    const response = await gateway.price(request);
    if (versionAtSubmit !== formVersion) {
      return;
    }
    if (response.ok) {
      renderResult(response);
    } else {
      errorMessage.dataset.code = response.error?.code ?? "UNKNOWN";
      showError(response.error?.message ?? "The model rejected this request.", response.error?.field);
    }
  } catch (error) {
    console.error("Pricing failed", error);
    setRuntimeStatus({
      state: "error",
      message: "Python runtime error. Retry or use the CLI.",
    });
    showError("The Python runtime could not complete the calculation. Retry, or use the CLI.");
  } finally {
    setBusy(false);
  }
}

async function loadBuildInfo() {
  try {
    const response = await fetch("./build-info.json", { cache: "no-store" });
    if (!response.ok) {
      return;
    }
    const info = await response.json();
    const commit = info.commit ? ` (${info.commit})` : "";
    buildVersion.textContent = `${info.version ?? "dev"}${commit}`;
    buildMeta.textContent = `Python ${info.pyodide?.version ?? "?"} · contract ${info.contract ?? "?"}`;
    if (info.contract && info.contract !== CONTRACT_VERSION) {
      console.warn(`Contract mismatch: page ${CONTRACT_VERSION}, build ${info.contract}`);
    }
  } catch (error) {
    console.warn("Could not load build-info.json", error);
  }
}

function warmUp() {
  gateway.warmup().catch(() => {
    // The status callback already reports init failures. A user can retry.
  });
}

methodInputs.forEach((input) => input.addEventListener("change", () => syncForm()));
optionTypeInputs.forEach((input) => input.addEventListener("change", () => syncForm()));
allInputs.forEach((input) =>
  input.addEventListener("input", () => {
    clearOutput();
    formVersion += 1;
  }),
);
form.addEventListener("submit", onCalculate);
retryRuntime.addEventListener("click", () => {
  gateway.restart();
  setRuntimeStatus({ state: "loading", message: "Restarting Python runtime…" });
  warmUp();
});

syncForm({ resetOutput: false });
loadBuildInfo();

if ("requestIdleCallback" in window) {
  window.requestIdleCallback(warmUp, { timeout: 2500 });
} else {
  window.setTimeout(warmUp, 500);
}
