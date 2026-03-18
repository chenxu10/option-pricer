/**
 * App — frontend logic.
 *
 * Reads user inputs from the DOM, passes them to the pricing engine,
 * and renders the result (or error) back to the DOM.
 *
 * This module knows nothing about the math. It only depends on the
 * pricing engine's public API:
 *   computePutPrice(inputs) => { price: number }
 */

import { computePutPrice } from "./pricing-engine.js";

// --- DOM references ---
const form = document.getElementById("pricer-form");
const resultSection = document.getElementById("result-section");
const resultValue = document.getElementById("result-value");
const errorSection = document.getElementById("error-section");
const errorMessage = document.getElementById("error-message");

/**
 * Read numeric values from the form inputs.
 * @returns {Object} inputs expected by the pricing engine
 */
function readInputs() {
    return {
        alpha: parseFloat(document.getElementById("alpha").value),
        anchoredPutPrice: parseFloat(document.getElementById("anchored-put-price").value),
        anchoredPutStrike: parseFloat(document.getElementById("anchored-put-strike").value),
        underlyingPrice: parseFloat(document.getElementById("underlying-price").value),
        toSolveStrike: parseFloat(document.getElementById("to-solve-strike").value),
    };
}

/**
 * Show the result section and hide the error section.
 */
function showResult(price) {
    resultValue.textContent = price.toFixed(4);
    resultSection.classList.remove("hidden");
    errorSection.classList.add("hidden");
}

/**
 * Show the error section and hide the result section.
 */
function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove("hidden");
    resultSection.classList.add("hidden");
}

/**
 * Hide both result and error sections.
 */
function clearOutput() {
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
}

// --- Event handling ---
form.addEventListener("submit", (e) => {
    e.preventDefault();
    clearOutput();

    try {
        const inputs = readInputs();
        const { price } = computePutPrice(inputs);
        showResult(price);
    } catch (err) {
        showError(err.message);
    }
});
