import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress, t
import streamlit.components.v1 as components

# --- CONFIG ---
st.set_page_config(page_title="DNS Assay: Standard Curve Tool", layout="wide")

st.title("🧪 DNS Assay: Build and Use a Standard Curve")

with st.expander("📘 Background Briefing: What Are We Doing and Why?", expanded=True):
    st.markdown("""
Welcome to the DNS Assay tool! Today, you'll take your experimental absorbance data, create a **standard curve**,
and then use it to figure out how much sugar is in your everyday beverage.

### What is a Standard Curve?
A **standard curve** is like a secret decoder ring for your experiments. It's a graph that shows the relationship between:
* **Known amounts** (or **concentrations**) of a substance (that's your X-axis!)
* Their corresponding **absorbance readings** (that's your Y-axis!)

When you graph this data, we draw a **line of best fit** through your points. This line has a special equation:
""")

    st.latex(r"A = m \times C + b") # st.latex implicitly handles raw strings for LaTeX

    st.markdown(r"""
Where:
* $A$ is **Absorbance** (measured by the spectrophotometer in Absorbance Units, AU)
* $C$ is **Concentration** (how much sugar is present, in mg/mL)
* $m$ is the **slope** (how steep your line is – a bigger '$m$' means more absorbance per unit of sugar!)
* $b$ is the **y-intercept** (where your line crosses the Y-axis when there's zero sugar)

Once you have this equation, it's a powerful tool! If you measure the absorbance of an unknown sample, you can use the equation to calculate its concentration.
""")


st.markdown("---")

st.header("📊 Step 1: Build Your Standard Curve")

st.info("""
**Important Tip:** Your spectrophotometer is best at reading absorbance values in a **linear range**.
This means the relationship between concentration and absorbance should look like a straight line.
If some of your absorbance values are too high (or too low), they might not fit the straight line,
and your standard curve won't be as accurate!
""")

with st.expander("Enter absorbance values for your glucose standards (Click to expand)"):
    concs = [0.0, 0.1, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0]  # mg/mL
    # Updated default_abs to explicitly use 3 decimal places
    default_abs = [0.000, 0.050, 0.150, 0.300, 0.550, 0.800, 1.000, 1.200]
    df_std = pd.DataFrame({"Glucose (mg/mL)": concs, "Absorbance (AU)": default_abs})
    edited_std = st.data_editor(df_std, key="std_editor")

# Extract original data for reference
x_all = edited_std["Glucose (mg/mL)"].values
y_all = edited_std["Absorbance (AU)"].values

st.markdown("---")
st.subheader("1.1: Identify the Linear Region of Your Standard Curve")
st.markdown("""
Look at the graph below. Sometimes, not all your standard points will fall perfectly on a straight line, especially at very high or very low concentrations.
**Your task is to select the range of glucose concentrations that look the most linear (form the straightest line).**
This is the "linear region" we want to use for our calculations.
""")

# Input for selecting linear range
col_start, col_end = st.columns(2)
min_conc_option = float(x_all.min())
max_conc_option = float(x_all.max())

# Determine sensible step for number_input based on available concentrations
if len(np.unique(x_all)) > 1:
    step_val = np.min(np.diff(np.sort(np.unique(x_all))))
else:
    step_val = 1.0 # Default step if only one unique concentration

# Set default values for start/end, avoiding direct use of min/max of edited_std if it has issues
initial_start_conc = float(0.0)
initial_end_conc = float(x_all.max())

# Ensure min/max values for number_input are within the actual data range
start_conc = col_start.number_input(
    "Start Concentration (mg/mL) for Linear Fit:",
    min_value=min_conc_option,
    max_value=max_conc_option,
    value=initial_start_conc,
    step=step_val,
    format="%.1f",
    key="start_conc_input"
)
end_conc = col_end.number_input(
    "End Concentration (mg/mL) for Linear Fit:",
    min_value=min_conc_option,
    max_value=max_conc_option,
    value=initial_end_conc,
    step=step_val,
    format="%.1f",
    key="end_conc_input"
)

# Filter data based on selected range
linear_mask = (x_all >= start_conc) & (x_all <= end_conc)
x_linear = x_all[linear_mask]
y_linear = y_all[linear_mask]

# Perform linear regression ONLY on the selected linear data
if len(x_linear) >= 2: # Need at least 2 points for a linear fit
    slope, intercept, r_value, p_value, std_err = linregress(x_linear, y_linear)

    st.markdown("---")
    st.subheader("1.2: Your Selected Linear Fit Equation and Plot")
    st.write("Your **Linear Fit Equation** is:")
    st.latex(f"A = {slope:.3f} \\times C + {intercept:.3f}")
    st.markdown(f"*(The R-squared value for your **selected linear range** is: {r_value**2:.3f}. A value closer to 1.0 indicates a very strong linear fit.)*")

    # Plot the standard curve with highlighted linear region
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_all, y_all, 'o', label='All Data Points', color='grey', alpha=0.6) # Show all data points
    ax.plot(x_linear, y_linear, 'o', label='Selected Linear Region', color='blue') # Highlight selected points
    ax.plot(x_linear, slope * x_linear + intercept, '-', label=f'Best Fit Line (y={slope:.3f}x + {intercept:.3f})', color='red') # Fit line only on linear region

    ax.set_xlabel("Glucose Concentration (mg/mL)")
    ax.set_ylabel("Absorbance (AU)")
    ax.set_title("Glucose Standard Curve with Selected Linear Fit")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)
    plt.close(fig)

    if r_value**2 < 0.95: # Simple heuristic for a "good" R-squared
        st.warning(f"⚠️ **Warning:** The R-squared value for your selected range ({r_value**2:.3f}) is a bit low. This means the points in your selected range don't form a very strong straight line. Consider adjusting your 'Start Concentration' and 'End Concentration' to find a more linear section of your data.")

else:
    st.error("Please select a range with at least two data points to perform the linear fit.")
    slope = np.nan # Ensure slope and intercept are nan if no fit can be made
    intercept = np.nan


st.markdown("---")

st.header("🥤 Step 2: Analyze an Unknown Beverage")

st.markdown("""
#### **Using the Standard Curve Equation to Find Unknown Concentration (Step-by-Step):**

You've just created your standard curve, which gave you this equation:
**Absorbance (A) = slope (m) × Concentration (C) + y-intercept (b)**

But what if you know the **Absorbance (A)** of an unknown sample and want to find its **Concentration (C)**? You need to rearrange the equation! Let's do the algebra:

1.  **Start with your equation:**
""")
st.latex(r"A = m \times C + b") # Use st.latex for the equation
st.markdown("""
2.  **Move 'b' (y-intercept) to the other side:**
    *Since 'b' is added on the right, subtract 'b' from both sides to move it:*
""")
st.latex(r"A - b = m \times C") # Use st.latex for the equation
st.markdown("""
3.  **Isolate 'C' (Concentration):**
    *Since 'm' is multiplied by 'C' on the right, divide both sides by 'm':*
""")
st.latex(r" C = \frac{A - b}{m} ") # st.latex implicitly handles raw strings well

st.markdown("""
So, the final equation to find your unknown concentration is:
""")
st.latex(r" \textbf{Concentration (C) = } \frac{\textbf{Absorbance (A) - y-intercept (b)}}{\textbf{slope (m)}} ") # st.latex implicitly handles raw strings well

st.markdown("""
**Here's how you'll use it in practice:**

1.  Measure your unknown beverage sample's **Absorbance (A)** using the spectrophotometer.
2.  Your script has already calculated the **slope (m)** and **y-intercept (b)** from your standard curve data (look at "Your Selected Linear Fit Equation" above).
3.  Enter your measured absorbance values in the table below. The "Estimated Glucose (mg/mL)" column will then **automatically calculate the concentration** for each dilution based on your standard curve equation.

**Pro Tip:** Remember, you tried 20x, 100x, and one other dilution. When analyzing your results in the table below, focus on the sample whose absorbance (AU) falls within the **linear region** of your standard curve (the straight-line part of your graph!). Absorbance values that are too high can lead to inaccurate concentration readings because they are outside this reliable linear range.
""")

beverage = st.text_input("Name of beverage you're testing:", "Orange Soda")

with st.expander("Enter absorbance values for different dilutions of your beverage (Click to expand)"):
    # Updated Dilution Factors to reflect the instructions given to students
    df_unknown = pd.DataFrame({
        "Dilution Factor": ["1:20", "1:100", "Other (e.g., 1:5, 1:10)"],
        "Absorbance (AU)": [np.nan, np.nan, np.nan] # Initialize with np.nan for numerical input
    })
    # Explicitly cast to float to ensure data_editor treats it as a numeric column
    df_unknown["Absorbance (AU)"] = df_unknown["Absorbance (AU)"].astype(float)

    edited_unknown = st.data_editor(df_unknown, key="unknown_editor")

    # CRUCIAL FIX: Ensure 'Absorbance (AU)' column is numeric after user edits
    # This converts any non-numeric input (like empty strings) to np.nan
    edited_unknown["Absorbance (AU)"] = pd.to_numeric(edited_unknown["Absorbance (AU)"], errors='coerce')


    def estimate_concentration(abs_val, slope, intercept):
        # Handle non-numeric or NaN inputs for absorbance first
        if pd.isna(abs_val): # Check for np.nan values that might come from pd.to_numeric(errors='coerce')
            return np.nan # Return NaN for truly empty/missing data

        # Ensure slope and intercept are valid numbers from the linear fit
        if np.isnan(slope) or np.isnan(intercept):
            return "N/A (no valid linear fit)"

        try:
            # abs_val is already float due to pd.to_numeric earlier, so direct use is safe
            est_conc = (abs_val - intercept) / slope
            if est_conc < 0:
                return 0.0 # Return 0.0 for negative concentrations (or np.nan if you prefer)
            return round(est_conc, 3)
        except ZeroDivisionError: # Catch if slope is precisely 0
            return "Error: Slope is zero"
        except Exception as e: # Catch any other unexpected errors during calculation
            # st.error(f"An unexpected calculation error occurred for {abs_val}: {e}") # Too verbose in apply
            return np.nan


    # Apply the function to create the new column
    edited_unknown["Estimated Glucose (mg/mL)"] = edited_unknown["Absorbance (AU)"].apply(lambda x: estimate_concentration(x, slope, intercept))
    st.dataframe(edited_unknown)


# --- NEW SECTION: Correcting for Dilution ---
st.markdown("---")
st.header("📈 Step 3: Calculate Original Concentration (Correct for Dilution!)")
st.markdown("""
The "Estimated Glucose (mg/mL)" value you just calculated is the concentration in your **diluted sample**.
To find the actual glucose concentration in your **original beverage**, you need to reverse the dilution!
""")

st.markdown("""**Formula for Correcting Dilution:**""")

st.latex(r" \text{Original Concentration} = \text{Estimated Concentration (from diluted sample)} \times \text{Dilution Factor}") # st.latex implicitly handles raw strings well

st.markdown("""
* **What is the Dilution Factor?**
    * If you did a **1:1 dilution**, the Dilution Factor is **1** (no dilution).
    * If you did a **1:5 dilution**, the Dilution Factor is **5**.
    * If you did a **1:10 dilution**, the Dilution Factor is **10**.
    * If you did a **1:20 dilution**, the Dilution Factor is **20**, and so on.
""")

# Interactive calculation for students
estimated_conc_input = st.number_input(
    "Enter the 'Estimated Glucose (mg/mL)' from your table for the best dilution (e.g., 0.500):",
    min_value=0.0, format="%.3f", key="estimated_conc_input"
)
dilution_factor_input = st.number_input(
    "Enter the Dilution Factor you used (e.g., enter 10 for a 1:10 dilution):",
    min_value=1.0, step=1.0, format="%f", key="dilution_factor_input"
)

# Initialize original_conc_final to NaN for clear representation if not calculated
original_conc_final = np.nan

# Only perform calculation if both inputs are valid and non-zero (for concentration)
# Also check if slope and intercept are valid (not NaN from a failed linear fit)
if estimated_conc_input > 0 and dilution_factor_input >= 1 and not np.isnan(slope) and not np.isnan(intercept):
    original_conc_final = estimated_conc_input * dilution_factor_input
    st.success(f"**Calculated Original Glucose Concentration in {beverage}:** **{original_conc_final:.3f} mg/mL**")
    st.info(f"This means your original **{beverage}** contains approximately **{original_conc_final:.3f} milligrams of glucose per milliliter** of liquid.")
elif np.isnan(slope) or np.isnan(intercept):
    st.warning("Cannot calculate original concentration. Please ensure your standard curve has at least two points and a valid linear fit.")
elif estimated_conc_input == 0 and dilution_factor_input == 1: # This means the user hasn't input anything meaningful yet (default state)
    st.info("Enter your estimated concentration and dilution factor above to calculate the original concentration.")
else: # This handles cases where inputs might be invalid or lead to zero results that aren't the default state
    st.info("Enter your estimated concentration and dilution factor above to calculate the original concentration.")

st.markdown("---")

st.header("🧠 Reflection")

st.text_area("1. What did you learn about using a standard curve to determine unknown concentrations?", height=100)
st.text_area("2. How did the sugar content in your chosen beverage compare to printed label (go check the label on the bottle)?", height=100)
st.text_area("3. Why is it important to dilute your sample to fit within the linear range of your curve? What might happen if you don't?", height=100)
st.text_area("4. What would happen if your sample’s absorbance was too high for your standard curve?", height=100)

st.success("🎉 Great job applying real-world biotech tools to everyday products! 🎉")

# --- NEW: SINGLE DOWNLOAD BUTTON FOR ALL RESULTS ---
st.markdown("---")
st.subheader("⬇️ Download All Your Results")

def generate_combined_csv(std_df, unknown_df, final_conc, beverage_name, slope_val, intercept_val, r_squared_val, start_conc_fit, end_conc_fit):
    combined_content = f"Standard Curve Data:\n"
    combined_content += std_df.to_csv(index=False)
    combined_content += "\n\n--- Linear Fit Equation (from selected range) ---\n"
    combined_content += f"Range used for fit: {start_conc_fit} mg/mL to {end_conc_fit} mg/mL\n"
    combined_content += f"Absorbance = {slope_val:.3f} * Concentration + {intercept_val:.3f}\n"
    combined_content += f"R-squared: {r_squared_val:.3f}\n\n" # Added R-squared to CSV
    combined_content += f"Beverage Analysis Data for {beverage_name}:\n"
    combined_content += unknown_df.to_csv(index=False)

    if not np.isnan(final_conc): # Check if final_conc was successfully calculated
        combined_content += f"\n\n--- Final Original Concentration for {beverage_name} ---\n"
        combined_content += f"Original Glucose Concentration: {final_conc:.3f} mg/mL\n"
    else:
        combined_content += "\n\n--- Final Original Concentration ---\n"
        combined_content += "Not calculated or invalid input (check estimated concentration and dilution factor, and if a valid linear fit was made).\n"

    return combined_content.encode('utf-8')

# Ensure variables are defined for the download function, even if inputs haven't been made yet
final_original_conc_for_download = original_conc_final if 'original_conc_final' in locals() and not np.isnan(original_conc_final) else np.nan
current_beverage_name_for_download = beverage if beverage else "Unknown_Beverage"

# Get the selected range for download info
selected_start_conc_for_download = start_conc if 'start_conc' in locals() else 'N/A'
selected_end_conc_for_download = end_conc if 'end_conc' in locals() else 'N/A'
r_squared_for_download = r_value**2 if 'r_value' in locals() and not np.isnan(r_value) else np.nan

st.download_button(
    label="Download All DNS Assay Results (.csv)",
    data=generate_combined_csv(edited_std, edited_unknown, final_original_conc_for_download,
                               current_beverage_name_for_download, slope, intercept,
                               r_squared_for_download, selected_start_conc_for_download, selected_end_conc_for_download),
    file_name=f"{current_beverage_name_for_download.replace(' ', '_')}_DNS_Assay_Results.csv",
    mime="text/csv",
    key="download_all_results"
)
