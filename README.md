# Fluid Flow & Heat Transfer Engineering Suite

A multi-page Streamlit web application providing engineering models for fluid mechanics, thermal conduction/cooling, and core rock data analysis.

## Live Application
🔗 **[Launch Engineering Suite Web App](https://engineering-suite-tcnettey4074424.streamlit.app/)**

## Features
- **Module A: Pipe Flow Analyser**: Computes velocity, Reynolds number, Swamee-Jain friction factor, and Darcy-Weisbach pressure drop with interactive plotting.
- **Module B: Heat Transfer Calculator**: Computes flat-wall Fourier heat loss and interactive Newton's Law of Cooling dynamics over time.
- **Module C: Rock & Fluid Data Dashboard**: Dynamic CSV processor for reservoir/core sample datasets, including interactive filtering, histograms, and crossplots.

## Architecture
- `engineering.py`: Core Object-Oriented Python logic (`Fluid`, `Pipe`, `HeatTransferEngine`).
- `app.py`: Streamlit frontend layout and interactive visualizations.

## AI Usage Documentation
1. **Prompt 1:** "Generate explicit Python formula for Swamee-Jain friction factor approximation."
   - *Verified:* Cross-checked against manual calculation ($Re = 50,000$, $\epsilon/D = 0.00045$, $f \approx 0.021$).
   - *Corrected:* Fixed logarithmic base from $e$ (`math.log`) to $10$ (`math.log10`).
2. **Prompt 2:** "Write vectorised Newton's Law of Cooling dynamic NumPy function."
   - *Verified:* Checked boundary value at $t=0$ ($T = T_0$) and $t \to \infty$ ($T \to T_\infty$).
   - *Corrected:* Added error handling to prevent logarithm domain errors when $T_{target} \le T_\infty$.
3. **Prompt 3:** "Draft Streamlit metric display and download layout for Module A."
   - *Verified:* Streamlit rendered without layout overflow.
   - *Corrected:* Replaced static tables with Plotly `st.plotly_chart` for dynamic hover inspection.
