/**
 * Pricing Engine — the "backend" math module.
 *
 * This module exposes a single function that takes pricing inputs and returns
 * the computed to-solve put option price.
 *
 * Currently returns a hardcoded placeholder value.
 * Replace the body of `computePutPrice` with the real formula when ready.
 *
 * CONTRACT:
 *   Input  — { alpha, anchoredPutPrice, anchoredPutStrike, underlyingPrice, toSolveStrike }
 *   Output — { price: number }  (or throws an Error on invalid input)
 */

/**
 * Validate that all required fields are present and are finite positive numbers.
 * @param {Object} inputs
 */
function validateInputs(inputs) {
    const fields = [
        ["alpha", inputs.alpha],
        ["anchoredPutPrice", inputs.anchoredPutPrice],
        ["anchoredPutStrike", inputs.anchoredPutStrike],
        ["underlyingPrice", inputs.underlyingPrice],
        ["toSolveStrike", inputs.toSolveStrike],
    ];

    for (const [name, value] of fields) {
        if (value === undefined || value === null || !Number.isFinite(value)) {
            throw new Error(`Invalid input: "${name}" must be a finite number.`);
        }
        if (value <= 0) {
            throw new Error(`Invalid input: "${name}" must be positive.`);
        }
    }
}

/**
 * Compute the to-solve put option price.
 *
 * @param {Object} inputs
 * @param {number} inputs.alpha             - Tail exponent
 * @param {number} inputs.anchoredPutPrice  - Known (anchored) put option price
 * @param {number} inputs.anchoredPutStrike - Strike of the anchored put
 * @param {number} inputs.underlyingPrice   - Current underlying price
 * @param {number} inputs.toSolveStrike     - Strike of the put to price
 * @returns {{ price: number }}
 */
export function computePutPrice(inputs) {
    validateInputs(inputs);

    // ---------------------------------------------------------------
    // TODO: Replace the hardcoded value below with the real formula.
    // The function signature and return shape should stay the same so
    // the frontend does not need to change.
    // ---------------------------------------------------------------
    const placeholderPrice = 7.42;

    return { price: placeholderPrice };
}
