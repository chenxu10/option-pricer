// Option Pricing Calculator - Client-side pricing logic
// Based on Taleb's tail option pricing under power laws and BSM model

/**
 * Calculate the price of a call option at strike K2 using the power law formula
 */
function priceCall(s0, k1, k2, cK1, alpha) {
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
    
    return ((k2 - s0) / (k1 - s0)) ** (1 - alpha) * cK1;
}

/**
 * Calculate the price of a put option at strike K2 using the power law formula
 * Based on Equation 7, properly transformed to return space
 * r = (S0 - K) / S0, where returns are positive for OTM puts (K < S0)
 */
function pricePut(s0, k1, k2, pK1, alpha) {
    if (alpha <= 1) {
        throw new Error("Alpha must be greater than 1");
    }
    if (k1 >= s0) {
        throw new Error("K1 must be less than S0 for puts (OTM puts)");
    }
    if (k2 >= s0) {
        throw new Error("K2 must be less than S0 for puts (OTM puts)");
    }
    if (pK1 <= 0) {
        throw new Error("P(K1) must be positive");
    }
    
    // Transform strikes to returns: r = (S0 - K) / S0
    // This gives positive returns for OTM puts (K < S0)
    const r1 = (s0 - k1) / s0;  // return at K1
    const r2 = (s0 - k2) / s0;  // return at K2
    
    // Apply the power law formula in return space
    // Derived from Equation 7 by substituting K = S0(1-r)
    // P(K2) = P(K1) * [α - r2^(1-α) - (α-1)*r2] / [α - r1^(1-α) - (α-1)*r1]
    const numerator = alpha - Math.pow(r2, 1 - alpha) - (alpha - 1) * r2;
    const denominator = alpha - Math.pow(r1, 1 - alpha) - (alpha - 1) * r1;
    
    if (Math.abs(denominator) < 1e-15) {
        throw new Error("Invalid parameters: denominator is too close to zero");
    }
    
    return pK1 * numerator / denominator;
}

/**
 * Standard normal cumulative distribution function
 */
function normalCDF(x) {
    return 0.5 * (1 + erf(x / Math.sqrt(2)));
}

/**
 * Error function approximation
 */
function erf(x) {
    const sign = x >= 0 ? 1 : -1;
    x = Math.abs(x);
    
    const a1 =  0.254829592;
    const a2 = -0.284496736;
    const a3 =  1.421413741;
    const a4 = -1.453152027;
    const a5 =  1.061405429;
    const p  =  0.3275911;
    
    const t = 1 / (1 + p * x);
    const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
    
    return sign * y;
}

/**
 * Calculate BSM call option price
 */
function bsmCallPrice(S, K, T, r, sigma) {
    if (S <= 0) {
        throw new Error("S (underlying price) must be positive");
    }
    if (K <= 0) {
        throw new Error("K (strike price) must be positive");
    }
    if (T <= 0) {
        throw new Error("T (time to expiration) must be positive");
    }
    if (sigma <= 0) {
        throw new Error("Sigma (volatility) must be positive");
    }
    
    const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);
    
    return S * normalCDF(d1) - K * Math.exp(-r * T) * normalCDF(d2);
}

/**
 * Calculate BSM put option price
 */
function bsmPutPrice(S, K, T, r, sigma) {
    if (S <= 0) {
        throw new Error("S (underlying price) must be positive");
    }
    if (K <= 0) {
        throw new Error("K (strike price) must be positive");
    }
    if (T <= 0) {
        throw new Error("T (time to expiration) must be positive");
    }
    if (sigma <= 0) {
        throw new Error("Sigma (volatility) must be positive");
    }
    
    const d1 = (Math.log(S / K) + (r + sigma * sigma / 2) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);
    
    return K * Math.exp(-r * T) * normalCDF(-d2) - S * normalCDF(-d1);
}

/**
 * Handle form submission and display results
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pricing-form');
    const resultDiv = document.getElementById('result');
    const optionTypeRadios = document.querySelectorAll('input[name="optionType"]');
    const pricingMethodRadios = document.querySelectorAll('input[name="pricingMethod"]');
    const labelK1 = document.getElementById('label-k1');
    const labelK2 = document.getElementById('label-k2');
    const labelPrice = document.getElementById('label-price');
    const calcButton = document.getElementById('calc-button');
    const formulaInfo = document.getElementById('formula-info');
    const bsmFormulaInfo = document.getElementById('bsm-formula-info');
    const alphaInput = document.getElementById('alpha');
    const powerlawFields = document.getElementById('powerlaw-fields');
    const bsmFields = document.getElementById('bsm-fields');
    const descPowerlaw = document.getElementById('description-powerlaw');
    const descBSM = document.getElementById('description-bsm');
    
    if (!form || !resultDiv) {
        console.error('Required elements not found');
        return;
    }
    
    function updateFormVisibility() {
        const method = document.querySelector('input[name="pricingMethod"]:checked').value;
        const selectedType = document.querySelector('input[name="optionType"]:checked').value;
        
        if (method === 'powerlaw') {
            powerlawFields.style.display = 'block';
            bsmFields.style.display = 'none';
            formulaInfo.style.display = 'block';
            bsmFormulaInfo.style.display = 'none';
            descPowerlaw.style.display = 'block';
            descBSM.style.display = 'none';
            
            document.getElementById('k1').required = true;
            document.getElementById('k2').required = true;
            document.getElementById('price_k1').required = true;
            document.getElementById('alpha').required = true;
            document.getElementById('bsm-k').required = false;
            document.getElementById('bsm-t').required = false;
            document.getElementById('bsm-r').required = false;
            document.getElementById('bsm-sigma').required = false;
            
            if (selectedType === 'call') {
                labelK1.textContent = 'K1 (Anchor Strike > S0):';
                labelK2.textContent = 'K2 (Target Strike > S0):';
                labelPrice.textContent = 'C(K1) (Call Price at K1):';
                calcButton.textContent = 'Calculate C(K2)';
                alphaInput.step = '0.1';
                alphaInput.placeholder = 'e.g., 2.6';
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
                alphaInput.step = '0.1';
                alphaInput.placeholder = 'e.g., 2.6';
                formulaInfo.innerHTML = `
                    <strong>Put Option Formula (Equation 7 in return space):</strong><br>
                    P(K2) = P(K1) × [α - r2^(1-α) - (α-1)r2] / [α - r1^(1-α) - (α-1)r1]<br><br>
                    Where r = (S0 - K) / S0 (positive returns for OTM puts)<br>
                    and α > 1 (any real number)
                `;
            }
        } else {
            powerlawFields.style.display = 'none';
            bsmFields.style.display = 'block';
            formulaInfo.style.display = 'none';
            bsmFormulaInfo.style.display = 'block';
            descPowerlaw.style.display = 'none';
            descBSM.style.display = 'block';
            
            document.getElementById('k1').required = false;
            document.getElementById('k2').required = false;
            document.getElementById('price_k1').required = false;
            document.getElementById('alpha').required = false;
            document.getElementById('bsm-k').required = true;
            document.getElementById('bsm-t').required = true;
            document.getElementById('bsm-r').required = true;
            document.getElementById('bsm-sigma').required = true;
            
            if (selectedType === 'call') {
                calcButton.textContent = 'Calculate BSM Call Price';
            } else {
                calcButton.textContent = 'Calculate BSM Put Price';
            }
        }
    }
    
    // Listen for changes
    optionTypeRadios.forEach(radio => {
        radio.addEventListener('change', updateFormVisibility);
    });
    
    pricingMethodRadios.forEach(radio => {
        radio.addEventListener('change', updateFormVisibility);
    });
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        resultDiv.className = 'show';
        resultDiv.textContent = 'Calculating...';
        
        try {
            const method = document.querySelector('input[name="pricingMethod"]:checked').value;
            const selectedType = document.querySelector('input[name="optionType"]:checked').value;
            const s0 = parseFloat(document.getElementById('s0').value);
            
            if (isNaN(s0)) {
                throw new Error('Please fill in S0 with a valid number');
            }
            
            let price;
            let resultLabel;
            
            if (method === 'powerlaw') {
                const k1 = parseFloat(document.getElementById('k1').value);
                const k2 = parseFloat(document.getElementById('k2').value);
                const priceK1 = parseFloat(document.getElementById('price_k1').value);
                const alpha = parseFloat(document.getElementById('alpha').value);
                
                if ([k1, k2, priceK1, alpha].some(isNaN)) {
                    throw new Error('Please fill in all fields with valid numbers');
                }
                
                if (selectedType === 'call') {
                    price = priceCall(s0, k1, k2, priceK1, alpha);
                    resultLabel = 'C(K2)';
                } else {
                    price = pricePut(s0, k1, k2, priceK1, alpha);
                    resultLabel = 'P(K2)';
                }
            } else {
                const K = parseFloat(document.getElementById('bsm-k').value);
                const T = parseFloat(document.getElementById('bsm-t').value);
                const r = parseFloat(document.getElementById('bsm-r').value);
                const sigma = parseFloat(document.getElementById('bsm-sigma').value);
                
                if ([K, T, r, sigma].some(isNaN)) {
                    throw new Error('Please fill in all BSM fields with valid numbers');
                }
                
                if (selectedType === 'call') {
                    price = bsmCallPrice(s0, K, T, r, sigma);
                    resultLabel = 'BSM Call Price';
                } else {
                    price = bsmPutPrice(s0, K, T, r, sigma);
                    resultLabel = 'BSM Put Price';
                }
            }
            
            resultDiv.className = 'show';
            resultDiv.innerHTML = `${resultLabel} = ${price.toFixed(6)}`;
        } catch (error) {
            resultDiv.className = 'show error';
            resultDiv.textContent = 'Error: ' + error.message;
            console.error('Calculation error:', error);
        }
    });
});
