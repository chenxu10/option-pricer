// Option Pricing Calculator - Client-side pricing logic
// Based on Taleb's tail option pricing under power laws

/**
 * Calculate the price of a call option at strike K2 using the power law formula
 * @param {number} s0 - Current underlying price
 * @param {number} k1 - Anchor strike price (must be > s0 for calls)
 * @param {number} k2 - Target strike price (must be > s0 for calls)
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
 * Calculate the price of a put option at strike K2 using the power law formula (Equation 7)
 * @param {number} s0 - Current underlying price
 * @param {number} k1 - Anchor strike price (must be < s0 for puts)
 * @param {number} k2 - Target strike price (must be < s0 for puts)
 * @param {number} pK1 - Price of put option at K1 (must be > 0)
 * @param {number} alpha - Tail index (must be > 1)
 * @returns {number} - Calculated price P(K2)
 * @throws {Error} - If validation fails
 */
function pricePut(s0, k1, k2, pK1, alpha) {
    // Input validation
    if (alpha <= 1) {
        throw new Error("Alpha must be greater than 1");
    }
    if (k1 >= s0) {
        throw new Error("K1 must be less than S0");
    }
    if (k2 >= s0) {
        throw new Error("K2 must be less than S0");
    }
    if (pK1 <= 0) {
        throw new Error("P(K1) must be positive");
    }
    
    // Calculate numerator: (K2 - S0)^(1-α) - S0^(1-α)*((α-1)K2 + S0)
    const numerator = (k2 - s0) ** (1 - alpha) - (s0 ** (1 - alpha)) * ((alpha - 1) * k2 + s0);
    
    // Calculate denominator: (K1 - S0)^(1-α) - S0^(1-α)*((α-1)K1 + S0)
    const denominator = (k1 - s0) ** (1 - alpha) - (s0 ** (1 - alpha)) * ((alpha - 1) * k1 + s0);
    
    // P(K2) = P(K1) * numerator / denominator
    return pK1 * numerator / denominator;
}

/**
 * Handle form submission and display results
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pricing-form');
    const resultDiv = document.getElementById('result');
    const optionTypeRadios = document.querySelectorAll('input[name="optionType"]');
    const labelK1 = document.getElementById('label-k1');
    const labelK2 = document.getElementById('label-k2');
    const labelPrice = document.getElementById('label-price');
    const calcButton = document.getElementById('calc-button');
    const formulaInfo = document.getElementById('formula-info');
    
    if (!form || !resultDiv) {
        console.error('Required elements not found');
        return;
    }
    
    // Update form labels based on option type selection
    function updateFormLabels() {
        const selectedType = document.querySelector('input[name="optionType"]:checked').value;
        
        if (selectedType === 'call') {
            labelK1.textContent = 'K1 (Anchor Strike > S0):';
            labelK2.textContent = 'K2 (Target Strike > S0):';
            labelPrice.textContent = 'C(K1) (Call Price at K1):';
            calcButton.textContent = 'Calculate C(K2)';
            formulaInfo.innerHTML = `
                <strong>Call Option Formula (Equation 6):</strong><br>
                C(K2) = C(K1) × [(K2 - S0) / (K1 - S0)]^(1-α)<br><br>
                Where K1, K2 > S0 (OTM calls) and α > 1
            `;
        } else {
            labelK1.textContent = 'K1 (Anchor Strike < S0):';
            labelK2.textContent = 'K2 (Target Strike < S0):';
            labelPrice.textContent = 'P(K1) (Put Price at K1):';
            calcButton.textContent = 'Calculate P(K2)';
            formulaInfo.innerHTML = `
                <strong>Put Option Formula (Equation 7):</strong><br>
                P(K2) = P(K1) × [numerator] / [denominator]<br><br>
                Where:<br>
                • numerator = (K2-S0)^(1-α) - S0^(1-α)×[(α-1)K2 + S0]<br>
                • denominator = (K1-S0)^(1-α) - S0^(1-α)×[(α-1)K1 + S0]<br><br>
                K1, K2 < S0 (OTM puts) and α > 1
            `;
        }
    }
    
    // Listen for option type changes
    optionTypeRadios.forEach(radio => {
        radio.addEventListener('change', updateFormLabels);
    });
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        resultDiv.className = 'show';
        resultDiv.textContent = 'Calculating...';
        
        try {
            // Collect input values
            const selectedType = document.querySelector('input[name="optionType"]:checked').value;
            const s0 = parseFloat(document.getElementById('s0').value);
            const k1 = parseFloat(document.getElementById('k1').value);
            const k2 = parseFloat(document.getElementById('k2').value);
            const priceK1 = parseFloat(document.getElementById('price_k1').value);
            const alpha = parseFloat(document.getElementById('alpha').value);
            
            // Validate all fields have valid numbers
            if ([s0, k1, k2, priceK1, alpha].some(isNaN)) {
                throw new Error('Please fill in all fields with valid numbers');
            }
            
            let price;
            let resultLabel;
            
            // Calculate price based on option type
            if (selectedType === 'call') {
                price = priceCall(s0, k1, k2, priceK1, alpha);
                resultLabel = 'C(K2)';
            } else {
                price = pricePut(s0, k1, k2, priceK1, alpha);
                resultLabel = 'P(K2)';
            }
            
            // Display result
            resultDiv.className = 'show';
            resultDiv.innerHTML = `${resultLabel} = ${price.toFixed(6)}`;
        } catch (error) {
            // Display error
            resultDiv.className = 'show error';
            resultDiv.textContent = 'Error: ' + error.message;
            console.error('Calculation error:', error);
        }
    });
});
