"""
Streamlit Web Application for Engineering Calculations Suite.
Includes Pipe Flow Analysis, Heat Transfer Calculations, and Rock/Fluid Data Dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from engineering import Fluid, Pipe, HeatTransferEngine

# Page Config
st.set_page_config(page_title="Engineering Suite", page_icon="⚙️", layout="wide")

st.title("⚙️ Fluid Flow & Heat Transfer Engineering Suite")

# Predefined Fluid Library
FLUIDS = {
    "Water (20°C)": Fluid("Water", 998.2, 0.001002, 4184),
    "Air (20°C, 1 atm)": Fluid("Air", 1.204, 0.00001825, 1005),
    "Crude Oil (Light, 15°C)": Fluid("Crude Oil", 855.0, 0.0072, 1900),
}

# Navigation Sidebar
module = st.sidebar.radio(
    "Select Module",
    ["Module A: Pipe Flow Analyser", "Module B: Heat Transfer Calculator", "Module C: Data Dashboard"]
)

# ---------------------------------------------------------
# MODULE A: PIPE FLOW ANALYSER
# ---------------------------------------------------------
if module == "Module A: Pipe Flow Analyser":
    st.header("🌊 Module A: Pipe Flow Analyser")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("1. Fluid Properties")
        fluid_option = st.selectbox("Select Fluid Presets", list(FLUIDS.keys()) + ["Custom Fluid"])
        
        if fluid_option == "Custom Fluid":
            rho = st.number_input("Density ρ (kg/m³)", value=1000.0, min_value=0.1)
            mu = st.number_input("Dynamic Viscosity μ (Pa·s)", value=0.001, min_value=0.000001, format="%.6f")
            selected_fluid = Fluid("Custom", rho, mu)
        else:
            selected_fluid = FLUIDS[fluid_option]
            st.caption(f"Density: **{selected_fluid.density} kg/m³** | Viscosity: **{selected_fluid.viscosity} Pa·s**")

        st.subheader("2. Pipe Geometry & Operations")
        d_m = st.number_input("Inner Diameter D (m)", value=0.1, min_value=0.001, format="%.3f")
        l_m = st.number_input("Pipe Length L (m)", value=100.0, min_value=0.1)
        rough_m = st.number_input("Roughness ε (m)", value=0.000045, min_value=0.0, format="%.6f", help="0.000045m for Commercial Steel")
        q_m3h = st.number_input("Volumetric Flow Rate Q (m³/h)", value=50.0, min_value=0.1)

    with col2:
        try:
            pipe = Pipe(diameter=d_m, length=l_m, roughness=rough_m)
            v = pipe.calculate_velocity(q_m3h)
            re = pipe.calculate_reynolds(v, selected_fluid)
            f = pipe.calculate_friction_factor(re)
            dp = pipe.calculate_pressure_drop(v, f, selected_fluid)

            st.subheader("Analysis Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Velocity (v)", f"{v:.2f} m/s")
            m2.metric("Reynolds No. (Re)", f"{re:,.0f}")
            m3.metric("Friction Factor (f)", f"{f:.4f}")
            m4.metric("Pressure Drop (ΔP)", f"{dp/1e5:.3f} bar")

            # Sensitivity Plot: Flow Rate vs ΔP
            q_range = np.linspace(max(0.1, q_m3h * 0.1), q_m3h * 2.0, 50)
            dp_list = []
            for q in q_range:
                v_temp = pipe.calculate_velocity(q)
                re_temp = pipe.calculate_reynolds(v_temp, selected_fluid)
                f_temp = pipe.calculate_friction_factor(re_temp)
                dp_list.append(pipe.calculate_pressure_drop(v_temp, f_temp, selected_fluid) / 1000.0) # kPa

            plot_df = pd.DataFrame({"Flow Rate (m³/h)": q_range, "Pressure Drop (kPa)": dp_list})
            fig = px.line(plot_df, x="Flow Rate (m³/h)", y="Pressure Drop (kPa)", title="Flow Rate vs. Pressure Drop")
            st.plotly_chart(fig, use_container_width=True)

            # Export Results
            results_df = pd.DataFrame([{
                "Fluid": selected_fluid.name, "Density_kg_m3": selected_fluid.density,
                "Viscosity_Pa_s": selected_fluid.viscosity, "Diameter_m": d_m,
                "Length_m": l_m, "Roughness_m": rough_m, "FlowRate_m3_h": q_m3h,
                "Velocity_m_s": v, "Reynolds_Number": re, "Friction_Factor": f, "PressureDrop_Pa": dp
            }])
            
            st.download_button("📥 Export Analysis Results (CSV)", results_df.to_csv(index=False), "pipe_flow_results.csv", "text/csv")

        except Exception as err:
            st.error(f"Calculation Error: {err}")

# ---------------------------------------------------------
# MODULE B: HEAT TRANSFER CALCULATOR
# ---------------------------------------------------------
elif module == "Module B: Heat Transfer Calculator":
    st.header("🔥 Module B: Heat Transfer Calculator")
    
    tab1, tab2 = st.tabs(["1. Steady-State Conduction", "2. Newton's Law of Cooling"])

    with tab1:
        st.subheader("Steady-State Flat Wall Conduction (Fourier's Law)")
        c1, c2 = st.columns(2)
        with c1:
            k_val = st.number_input("Thermal Conductivity k (W/m·K)", value=45.0, help="Structural Steel ~ 45, Brick ~ 0.7")
            area_val = st.number_input("Wall Surface Area A (m²)", value=10.0, min_value=0.1)
            thick_val = st.number_input("Wall Thickness L (m)", value=0.15, min_value=0.001)
        with c2:
            t_in = st.number_input("Inside Surface Temp T1 (°C)", value=120.0)
            t_out = st.number_input("Outside Surface Temp T2 (°C)", value=25.0)

        q_watts = HeatTransferEngine.wall_conduction(k_val, area_val, thick_val, t_in, t_out)
        st.success(f"**Calculated Heat Loss (Q):** {q_watts:,.2f} Watts ({q_watts/1000:.2f} kW)")

    with tab2:
        st.subheader("Newton's Law of Cooling (Transient)")
        col_a, col_b = st.columns([1, 2])

        with col_a:
            t0 = st.slider("Initial Object Temp T₀ (°C)", 50.0, 300.0, 150.0)
            t_inf = st.slider("Ambient Temp T_inf (°C)", 0.0, 40.0, 25.0)
            t_target = st.slider("Target Temp T_target (°C)", t_inf + 1.0, t0 - 1.0, 50.0)
            k_cool = st.slider("Cooling Rate Constant k (1/s)", 0.001, 0.05, 0.005, step=0.001, format="%.3f")
            t_max = st.number_input("Simulation Duration (s)", value=1000, min_value=10)

        with col_b:
            times, temps = HeatTransferEngine.transient_cooling(t0, t_inf, k_cool, t_max)
            fig_cool = px.line(x=times, y=temps, labels={'x': 'Time (s)', 'y': 'Temperature (°C)'}, title="Cooling Curve over Time")
            
            try:
                t_reach = HeatTransferEngine.time_to_target_temp(t0, t_inf, t_target, k_cool)
                fig_cool.add_vline(x=t_reach, line_dash="dash", line_color="red", annotation_text=f"Target: {t_reach:.1f}s")
                st.info(f"⏱ Time required to reach **{t_target}°C**: **{t_reach:.2f} seconds**")
            except ValueError as e:
                st.warning(str(e))

            st.plotly_chart(fig_cool, use_container_width=True)

# ---------------------------------------------------------
# MODULE C: ROCK & FLUID DATA DASHBOARD
# ---------------------------------------------------------
elif module == "Module C: Data Dashboard":
    st.header("📊 Module C: Rock & Fluid Data Dashboard")
    
    uploaded_file = st.file_uploader("Upload CSV Dataset (e.g., Core Sample Porosity/Permeability Data)", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) >= 2:
            st.subheader("Data Filtering & Statistics")
            filter_col = st.selectbox("Select Column to Filter By", numeric_cols)
            min_val, max_val = float(df[filter_col].min()), float(df[filter_col].max())
            selected_range = st.slider(f"Filter range for {filter_col}", min_val, max_val, (min_val, max_val))

            filtered_df = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]
            
            st.write(f"Displaying **{len(filtered_df)}** of **{len(df)}** rows")
            st.write(filtered_df.describe())

            col_x, col_y = st.columns(2)
            with col_x:
                x_axis = st.selectbox("Select Histogram Column", numeric_cols, index=0)
                fig_hist = px.histogram(filtered_df, x=x_axis, title=f"Distribution of {x_axis}")
                st.plotly_chart(fig_hist, use_container_width=True)

            with col_y:
                y_axis = st.selectbox("Select Crossplot Y-Axis", numeric_cols, index=min(1, len(numeric_cols)-1))
                fig_scatter = px.scatter(filtered_df, x=x_axis, y=y_axis, title=f"{x_axis} vs {y_axis}")
                st.plotly_chart(fig_scatter, use_container_width=True)

            st.download_button("📥 Download Filtered Data CSV", filtered_df.to_csv(index=False), "filtered_rock_data.csv", "text/csv")
        else:
            st.error("Uploaded CSV must contain at least two numeric columns.")
    else:
        st.info("💡 Upload a CSV file or download this sample dataset to test:")
        sample_data = pd.DataFrame({
            "Sample_ID": [f"CORE-{i:03d}" for i in range(1, 51)],
            "Porosity_%": np.random.uniform(5, 28, 50).round(2),
            "Permeability_mD": np.random.exponential(50, 50).round(2),
            "Grain_Density_g_cc": np.random.normal(2.65, 0.03, 50).round(2)
        })
        st.download_button("📥 Download Sample Core CSV", sample_data.to_csv(index=False), "sample_core_data.csv", "text/csv")
