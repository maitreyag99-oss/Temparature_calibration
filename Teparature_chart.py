import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import chebyshev as C

# ---- your data ----
T = np.array([4.2, 10, 20, 40, 77, 150, 300])          # true temperatures (K)
R = np.array([2025.8, 978.1, 574.3, 363.5, 233.0, 159.0, 111.7])  # measured resistances (ohm)

# ---- fit log10(T) as a function of log10(R), so it's usable as R -> T ----
x = np.log10(R)      # independent: what you measure
y = np.log10(T)      # dependent: what you want

xmin, xmax = x.min(), x.max()
def rescale(v):                       # map log10(R) into [-1, 1] for Chebyshev
    return (2*v - (xmax + xmin)) / (xmax - xmin)

order = 4
coeffs = C.chebfit(rescale(x), y, deg=order)   # <-- THE FIT: these coeffs are your calibration
print("Calibration coefficients:", np.round(coeffs, 6))

# ---- the calibration function: give it R, it returns T ----
def R_to_T(R_meas):
    u = rescale(np.log10(R_meas))
    return 10**C.chebval(u, coeffs)

# ---- residuals + RMS (how good is the fit?) ----
T_pred = R_to_T(R)
resid_mK = (T_pred - T) * 1000
rms = np.sqrt(np.mean(resid_mK**2))
print(f"RMS residual = {rms:.1f} mK")

# ---- plot 1: the fit against your points ----
R_smooth = np.logspace(np.log10(R.min()), np.log10(R.max()), 300)  # smooth R range
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.loglog(R, T, 'o', markersize=9, label='calibration points')
ax1.loglog(R_smooth, R_to_T(R_smooth), '-', label=f'Chebyshev fit (order {order})')
ax1.set_xlabel('Resistance R (ohm)')
ax1.set_ylabel('Temperature T (K)')
ax1.set_title('Cernox calibration curve: R -> T')
ax1.grid(True, which='both', alpha=0.3)
ax1.legend()

# ---- plot 2: the residuals (where and how much it misses) ----
ax2.axhline(0, color='green', linestyle='--', alpha=0.6)
ax2.plot(T, resid_mK, 'o-', color='crimson')
ax2.set_xscale('log')
ax2.set_xlabel('Temperature T (K)')
ax2.set_ylabel('Residual (mK)')
ax2.set_title(f'Residuals  (RMS = {rms:.0f} mK)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ---- use the calibration ----
print("\nUsing the calibration:")
for R_test in [2025.8, 500, 159.0]:
    print(f"  R = {R_test:7.1f} ohm  ->  T = {R_to_T(R_test):7.2f} K")