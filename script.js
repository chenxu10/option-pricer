// Option Pricing Calculator - Client-side pricing logic
// Based on Taleb's tail option pricing under power laws

/**
 * Calculate the price of a call option at strike K2 using the power law formula
 * @param {number} s0 - Current underlying price
 * @param {number} k1 - Anchor strike price (must be > s0)
 * @param {number} k2 - Target strike price (must be > s0)
 * @param {number} cK1 - Price of call option at K1 (must be > 0)
 * @param {number} alpha - Tail index (must be > 1)
 * @returns {number} - Calculated price C(K2)
 * @throws {Error} - If validation fails
 */
function priceCall(s0, k1, k2, cK1, alpha) {
    // Input validation
    if (alpha <= 1) {
        throw new Error("Alpha must be greater than 1");
    }
    if (k1 <= s0) {
        throw new Error("K1 must be greater than S0");
    }
    if (k2 <= s0) {
        throw new Error("K2 must be greater than S0");
    }
    if (cK1 <= 0) {
        throw new Error("C(K1) must be positive");
    }
    
    // Power law pricing formula: C(K2) = ((K2 - S0) / (K1 - S0))^(1 - alpha) * C(K1)
    return ((k2 - s0) / (k1 - s0)) ** (1 - alpha) * cK1;
}

/**
 * Handle form submission and display results
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pricing-form');
    const resultDiv = document.getElementById('result');
    
    if (!form || !resultDiv) {
        console.error('Required elements not found');
        return;
    }
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        resultDiv.className = 'show';
        resultDiv.textContent = 'Calculating...';
        
        try {
            // Collect input values
            const data = {
                s0: parseFloat(document.getElementById('s0').value),
                k1: parseFloat(document.getElementById('k1').value),
                k2: parseFloat(document.getElementById('k2').value),
                cK1: parseFloat(document.getElementById('c_k1').value),
                alpha: parseFloat(document.getElementById('alpha').value)
            };
            
            // Validate all fields have valid numbers
            if (Object.values(data).some(isNaN)) {
                throw new Error('Please fill in all fields with valid numbers');
            }
            
            // Calculate price
            const price = priceCall(data.s0, data.k1, data.k2, data.cK1, data.alpha);
            
            // Display result
            resultDiv.className = 'show';
            resultDiv.innerHTML = `C(K2) = ${price.toFixed(6)}`;
        } catch (error) {
            // Display error
            resultDiv.className = 'show error';
            resultDiv.textContent = 'Error: ' + error.message;
            console.error('Calculation error:', error);
        }
    });
});
