import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# --- CONFIG ---
st.set_page_config(page_title="Standard Curve Tutorial", layout="wide")

# --- STYLING ---
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
h2, h3 {
    color: #1a1a1a;
    border-bottom: 2px solid #CFB87C;
    padding-bottom: 0.25rem;
}
.stButton > button {
    background-color: #CFB87C;
    color: #000000;
    border: none;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #b8a269;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

# --- DEPARTMENT BANNER ---
import base64
with open("CBEN.png", "rb") as _banner_file:
    _banner_b64 = base64.b64encode(_banner_file.read()).decode()
st.markdown(
    f"""
    <div style="background-color: #000000; padding: 0.5rem 1.5rem; margin-bottom: 1rem; border-radius: 4px;">
        <img src="data:image/png;base64,{_banner_b64}" style="height: 80px; display: block;" />
    </div>
    """,
    unsafe_allow_html=True,
)

# --- PAGE TITLE ---
st.title("Standard Curve Tutorial")


# --- INTRO (collapsible) ---
with st.expander("What is a standard curve? (Click to expand)", expanded=False):
    st.markdown("""
A **standard curve** connects a known **concentration** to a measured **absorbance**. Once you've built one, you can measure the absorbance of an unknown sample and use your curve to back-calculate its concentration.

The line equation looks like this:
""")
    st.latex(r"A = m \times C + b")
    st.markdown(r"""
- $A$ = **Absorbance** (from your spectrophotometer)
- $C$ = **Concentration** (what you're trying to find)
- $m$ = **slope** (how steeply absorbance rises with concentration)
- $b$ = **y-intercept** (absorbance when concentration is zero)

To find an unknown concentration from an absorbance reading, rearrange the equation:
""")
    st.latex(r"C = \frac{A - b}{m}")


# --- STEP 1: STANDARDS DATA ---
st.header("Step 1: Enter your standard absorbance data")

st.markdown("""
Enter the absorbance you measured for each Red 40 standard at **510 nm**. The standard concentrations are pre-filled based on the Day 1 dilution series.
""")

default_concs = [1700.0, 850.0, 425.0, 212.5, 106.25, 53.13, 26.56, 13.28, 0.0]
labels = ["ST1", "ST2", "ST3", "ST4", "ST5", "ST6", "ST7", "ST8", "Blank"]
default_abs = [2.000, 1.450, 0.850, 0.440, 0.220, 0.110, 0.055, 0.028, 0.000]

df_std = pd.DataFrame({
    "Standard": labels,
    "Red 40 (µg/mL)": default_concs,
    "Absorbance (510 nm)": default_abs
})

edited_std = st.data_editor(
    df_std,
    key="std_editor",
    disabled=["Standard", "Red 40 (µg/mL)"],
    width="stretch"
)

x_all = edited_std["Red 40 (µg/mL)"].values.astype(float)
y_all = edited_std["Absorbance (510 nm)"].values.astype(float)


# --- STEP 2: LINEAR RANGE ---
st.header("Step 2: Identify the linear range")

st.markdown("""
Not every standard will fall on a straight line. At **very high concentrations**, the spectrophotometer saturates and absorbance readings flatten. At **very low concentrations**, readings get noisy.

Adjust the sliders below to select the concentration range where your data forms the cleanest straight line.
""")

col_start, col_end = st.columns(2)
unique_concs_sorted = sorted(np.unique(x_all))
default_start_idx = min(2, len(unique_concs_sorted) - 1)
default_end_idx = max(0, len(unique_concs_sorted) - 2)

start_conc = col_start.selectbox(
    "Start concentration for linear fit (µg/mL):",
    options=unique_concs_sorted,
    index=default_start_idx,
    key="start_conc_select"
)
end_conc = col_end.selectbox(
    "End concentration for linear fit (µg/mL):",
    options=unique_concs_sorted,
    index=len(unique_concs_sorted) - 1,
    key="end_conc_select"
)

if end_conc <= start_conc:
    st.error("End concentration must be greater than start concentration.")
    st.stop()

linear_mask = (x_all >= start_conc) & (x_all <= end_conc)
x_linear = x_all[linear_mask]
y_linear = y_all[linear_mask]


# --- STEP 3: CURVE EQUATION ---
if len(x_linear) >= 2:
    slope, intercept, r_value, _, _ = linregress(x_linear, y_linear)
    r_squared = r_value ** 2

    st.header("Step 3: Your standard curve")

    metric_cols = st.columns(3)
    metric_cols[0].metric("Slope (m)", f"{slope:.5f}")
    metric_cols[1].metric("Y-intercept (b)", f"{intercept:.4f}")
    metric_cols[2].metric("R²", f"{r_squared:.4f}")

    if r_squared < 0.95:
        st.warning(f"R² = {r_squared:.3f} is below 0.95. Your selected range isn't very linear — try adjusting the start or end concentration.")
    else:
        st.success(f"R² = {r_squared:.3f} — strong linear fit. You can trust this equation.")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_all, y_all, 'o', color='#888888', alpha=0.5, markersize=9, label='Excluded standards')
    ax.plot(x_linear, y_linear, 'o', color='#4A90E2', markersize=10, label='Standards used for fit')
    x_fit = np.linspace(x_linear.min(), x_linear.max(), 100)
    ax.plot(x_fit, slope * x_fit + intercept, '-', color='#D62728', linewidth=2,
            label=f'y = {slope:.5f}x + {intercept:.4f}')
    ax.set_xlabel("Red 40 concentration (µg/mL)", fontsize=11)
    ax.set_ylabel("Absorbance at 510 nm", fontsize=11)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95)
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)
    plt.close(fig)

    # Save the linear range boundaries for later use
    absorbance_min = slope * start_conc + intercept if slope > 0 else slope * end_conc + intercept
    absorbance_max = slope * end_conc + intercept if slope > 0 else slope * start_conc + intercept

    st.info(f"**Your usable absorbance range is approximately {absorbance_min:.3f} to {absorbance_max:.3f}.** Any beverage dilution with absorbance outside this range should not be used for back-calculation.")

    # --- STEP 4: BEVERAGE DATA ---
    st.header("Step 4: Measure your beverage dilutions")

    beverage = st.text_input("Name of beverage you're testing:", value="Gatorade Fruit Punch")

    st.markdown("""
    Enter the absorbance you measured for each of your three beverage dilutions. The app will calculate the Red 40 concentration in each **diluted** sample.
    """)

    dilution_factors = {"1:10": 10, "1:50": 50, "1:100": 100}
    df_unknown = pd.DataFrame({
        "Dilution": list(dilution_factors.keys()),
        "Dilution Factor": list(dilution_factors.values()),
        "Absorbance (510 nm)": [np.nan, np.nan, np.nan]
    })

    edited_unknown = st.data_editor(
        df_unknown,
        key="unknown_editor",
        disabled=["Dilution", "Dilution Factor"],
        width="stretch"
    )
    edited_unknown["Absorbance (510 nm)"] = pd.to_numeric(edited_unknown["Absorbance (510 nm)"], errors='coerce')

    def concentration_in_diluted_sample(abs_val):
        if pd.isna(abs_val):
            return np.nan
        return round((abs_val - intercept) / slope, 2)

    edited_unknown["Diluted sample (µg/mL)"] = edited_unknown["Absorbance (510 nm)"].apply(concentration_in_diluted_sample)

    def usability_status(abs_val):
        if pd.isna(abs_val):
            return "—"
        if abs_val < absorbance_min:
            return "Too dilute — below linear range"
        if abs_val > absorbance_max:
            return "Too concentrated — above linear range"
        return "In linear range — usable"

    edited_unknown["Status"] = edited_unknown["Absorbance (510 nm)"].apply(usability_status)

    st.dataframe(edited_unknown, width="stretch")


    # --- STEP 5: BACK-CALCULATE ---
    st.header("Step 5: Back-calculate the beverage concentration")

    usable_rows = edited_unknown[edited_unknown["Status"] == "In linear range — usable"]

    if len(usable_rows) == 0:
        if edited_unknown["Absorbance (510 nm)"].notna().any():
            st.warning("None of your dilutions fall within the linear range of your standard curve. You may need to re-dilute your samples.")
        else:
            st.info("Enter your beverage absorbances above to see the back-calculation.")
    else:
        st.markdown("""
Select which usable dilution you want to use for the final back-calculation. If multiple dilutions are usable, they should give you similar answers — differences between them tell you something about your technique.
""")

        usable_options = usable_rows["Dilution"].tolist()
        chosen_dilution = st.radio("Use this dilution:", usable_options, key="chosen_dilution")

        chosen_row = usable_rows[usable_rows["Dilution"] == chosen_dilution].iloc[0]
        diluted_conc = chosen_row["Diluted sample (µg/mL)"]
        dilution_factor = chosen_row["Dilution Factor"]
        original_conc = diluted_conc * dilution_factor

        st.latex(
            rf"\text{{Beverage concentration}} = {diluted_conc:.2f} \; \mu g/mL \times {int(dilution_factor)} = {original_conc:.1f} \; \mu g/mL"
        )

        result_cols = st.columns(3)
        result_cols[0].metric("Diluted sample", f"{diluted_conc:.2f} µg/mL")
        result_cols[1].metric("Dilution factor", f"×{int(dilution_factor)}")
        result_cols[2].metric(f"{beverage}", f"{original_conc:.1f} µg/mL")

        st.success(f"**{beverage} contains approximately {original_conc:.1f} µg/mL ({original_conc/1000:.2f} mg/mL) of Red 40.**")

        # --- CROSS-CHECK ---
        if len(usable_rows) > 1:
            st.markdown("### Cross-check with your other dilutions")
            check_rows = usable_rows.copy()
            check_rows["Back-calculated beverage (µg/mL)"] = (
                check_rows["Diluted sample (µg/mL)"] * check_rows["Dilution Factor"]
            ).round(1)
            st.dataframe(
                check_rows[["Dilution", "Absorbance (510 nm)", "Diluted sample (µg/mL)", "Back-calculated beverage (µg/mL)"]],
                width="stretch"
            )

            max_val = check_rows["Back-calculated beverage (µg/mL)"].max()
            min_val = check_rows["Back-calculated beverage (µg/mL)"].min()
            spread_pct = (max_val - min_val) / ((max_val + min_val) / 2) * 100 if (max_val + min_val) > 0 else 0

            if spread_pct < 10:
                st.success(f"Your dilutions agree to within {spread_pct:.1f}% — that's strong evidence your technique was consistent.")
            else:
                st.info(f"Your dilutions differ by {spread_pct:.1f}%. Differences larger than 10% suggest pipetting variability or reading errors.")

    # --- DOWNLOAD ---
    st.markdown("---")
    st.subheader("Download your results")

    def generate_combined_csv():
        content = f"Standard Curve Data\n"
        content += edited_std.to_csv(index=False)
        content += f"\n\nLinear Fit\n"
        content += f"Range used: {start_conc} to {end_conc} µg/mL\n"
        content += f"Absorbance = {slope:.5f} * Concentration + {intercept:.4f}\n"
        content += f"R-squared: {r_squared:.4f}\n\n"
        content += f"Beverage: {beverage}\n"
        content += edited_unknown.to_csv(index=False)

        if len(usable_rows) > 0:
            content += f"\n\nFinal beverage concentration (based on {chosen_dilution} dilution): {original_conc:.1f} µg/mL\n"
        else:
            content += "\n\nNo usable dilution was identified for back-calculation.\n"

        return content.encode('utf-8')

    st.download_button(
        label="Download CSV of all results",
        data=generate_combined_csv(),
        file_name=f"{beverage.replace(' ', '_')}_standard_curve_results.csv",
        mime="text/csv",
        key="download_all_results"
    )

else:
    st.error("Select a range with at least two data points to perform the linear fit.")
