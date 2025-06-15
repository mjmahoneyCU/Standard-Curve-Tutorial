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
    # This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
    st.markdown(r"""
Let's use that absorbance data that you collected with the spectrophotometer and create a Standard Curve.
Then, we can use it to determine the amount of sugar in your beverage.

### What is a Standard Curve?
A **standard curve** is a graph that shows the relationship between:
- **Known concentrations** of a substance (x-axis)
- Their corresponding **absorbance readings** (y-axis)

Once you graph this data, a **line of best fit** is drawn. This line has an equation in the form:
""")

    st.latex(r"A = m \times C + b") # st.latex implicitly handles raw strings for LaTeX

    # This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
    st.markdown(r"""
Where:
- \( A \) is Absorbance (AU)
- \( C \) is Concentration (mg/mL)
- \( m \) is the slope (how steep the line is)
- \( b \) is the y-intercept (where the line crosses the y-axis)
""")


st.markdown("---") # Simple string, no backslashes, doesn't strictly need 'r' but no harm

st.header("📊 Step 1: Build Your Standard Curve")

with st.expander("Enter absorbance values for your glucose standards"):
    concs = [0.0, 0.1, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0]  # mg/mL
    default_abs = [0.00, 0.05, 0.15, 0.30, 0.55, 0.80, 1.00, 1.20]
    df_std = pd.DataFrame({"Glucose (mg/mL)": concs, "Absorbance (AU)": default_abs})
    edited_std = st.data_editor(df_std, key="std_editor")

    # Removed: Download button for standard curve data


# Fit linear regression to determine linear region
x = edited_std["Glucose (mg/mL)"].values
y = edited_std["Absorbance (AU)"].values

slope, intercept, r_value, p_value, std_err = linregress(x, y)

# This is an f-string, usually doesn't need 'r' for '\times' in this specific context in Streamlit
st.write(f"**Linear Fit Equation:** Absorbance = {slope:.3f} × Concentration + {intercept:.3f}")

# Plot the standard curve
fig, ax = plt.subplots()
ax.plot(x, y, 'o', label='Data')
ax.plot(x, slope * x + intercept, '-', label='Best Fit')
ax.set_xlabel("Glucose (mg/mL)")
ax.set_ylabel("Absorbance (AU)")
ax.set_title("Standard Curve")
ax.legend()
st.pyplot(fig)

st.markdown("---")

st.header("🥤 Step 2: Analyze an Unknown Beverage")

# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""
#### **Using the Standard Curve Equation to Find Unknown Concentration (Step-by-Step):**

You've learned that your standard curve gives you an equation:
**Absorbance (A) = slope (m) × Concentration (C) + y-intercept (b)**

But what if you know the **Absorbance (A)** of an unknown sample and want to find its **Concentration (C)**? You need to rearrange the equation!

Let's do the algebra together:

1.  **Start with your equation:**
    $A = m \times C + b$

2.  **Move 'b' (y-intercept) to the other side:**
    *Since 'b' is added on the right, subtract 'b' from both sides to move it:*
    $A - b = m \times C$

3.  **Isolate 'C' (Concentration):**
    *Since 'm' is multiplied by 'C' on the right, divide both sides by 'm':*
    """)
st.latex(r" \frac{A - b}{m} = C ") # st.latex implicitly handles raw strings well

# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""
    So, the final equation to find your unknown concentration is:
    """)
st.latex(r" \textbf{Concentration (C) = } \frac{\textbf{Absorbance (A) - y-intercept (b)}}{\textbf{slope (m)}} ") # st.latex implicitly handles raw strings well

# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""
**Here's how you'll use it in practice (the table below will help):**

1.  Measure your unknown beverage sample's Absorbance (A) using the spectrophotometer.
2.  Your script has already calculated the slope (m) and y-intercept (b) from your standard curve data (look at "Linear Fit Equation" above).
3.  The table below will then take your measured Absorbance (A) and automatically plug these numbers into the rearranged equation to calculate the Estimated Glucose Concentration for your unknown sample.
""")

# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""
Try different dilutions to make sure the absorbance of your beverage sample falls within the linear region of your curve.
""")

beverage = st.text_input("Name of beverage you're testing:", "Orange Soda")

with st.expander("Enter absorbance values for different dilutions"):
    df_unknown = pd.DataFrame({
        "Dilution Factor": ["1:1", "1:5", "1:10", "Other"],
        "Absorbance (AU)": ["", "", "", ""]
    })
    edited_unknown = st.data_editor(df_unknown, key="unknown_editor")

    def estimate_concentration(abs_val):
        try:
            abs_val = float(abs_val)
            # Ensure slope is not zero to prevent division by zero
            if slope == 0:
                return "Error: Slope is zero"
            est_conc = (abs_val - intercept) / slope
            return round(est_conc, 3)
        except ValueError: # Catch if abs_val cannot be converted to float
            return ""
        except TypeError: # Catch if abs_val is None or other non-numeric type
            return ""

    edited_unknown["Estimated Glucose (mg/mL)"] = edited_unknown["Absorbance (AU)"].apply(estimate_concentration)
    st.dataframe(edited_unknown)

# --- NEW SECTION: Correcting for Dilution ---
st.markdown("---")
st.subheader("📈 Step 3: Correct for Dilution to Find Original Beverage Concentration")
# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""
The "Estimated Glucose (mg/mL)" value you just calculated is the concentration in your diluted sample.
To find the actual glucose concentration in your original beverage, you need to reverse the dilution!
""")

# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""**Formula for Correcting Dilution:**""")

st.latex(r" \text{Original Concentration} = \text{Estimated Concentration (from diluted sample)} \times \text{Dilution Factor}") # st.latex implicitly handles raw strings well

# This block explicitly uses r"""...""" to prevent invalid escape sequence warnings
st.markdown(r"""
* **What is the Dilution Factor?**
    * If you did a **1:1 dilution**, the Dilution Factor is **1** (no dilution).
    * If you did a **1:5 dilution**, the Dilution Factor is **5**.
    * If you did a **1:10 dilution**, the Dilution Factor is **10**.
    * If you did a **1:20 dilution**, the Dilution Factor is **20**, and so on.
""")

# Interactive calculation for students
estimated_conc_input = st.number_input(
    "Enter the 'Estimated Glucose (mg/mL)' from your table for the best dilution:",
    min_value=0.0, format="%.3f", key="estimated_conc_input"
)
dilution_factor_input = st.number_input(
    "Enter the Dilution Factor you used (e.g., enter 10 for a 1:10 dilution):",
    min_value=1.0, step=1.0, format="%f", key="dilution_factor_input"
)

# Initialize original_conc_final outside the if block to ensure it's always defined
original_conc_final = 0.0 # Default value

if estimated_conc_input > 0 and dilution_factor_input >= 1:
    original_conc_final = estimated_conc_input * dilution_factor_input
    st.success(f"**Calculated Original Glucose Concentration in {beverage}:** {original_conc_final:.3f} mg/mL")
    st.info(f"This means your original {beverage} contains {original_conc_final:.3f} mg of glucose per milliliter.")
elif estimated_conc_input == 0 and dilution_factor_input == 1:
    st.info("Enter your estimated concentration and dilution factor above to calculate the original concentration.")
else:
    st.info("Enter your estimated concentration and dilution factor above to calculate the original concentration.")

st.markdown("---")

st.header("🧠 Reflection")

st.text_area("1. What did you learn about using a standard curve to determine unknown concentrations?")
st.text_area("2. How did the sugar content in your chosen beverage compare to the diet soda?")
st.text_area("3. Why is it important to dilute your sample to fit within the linear range of your curve?")
st.text_area("4. What would happen if your sample’s absorbance was too high?")

st.success("Great job applying real-world biotech tools to everyday products!")

# --- NEW: SINGLE DOWNLOAD BUTTON FOR ALL RESULTS ---
st.markdown("---")
st.subheader("⬇️ Download All Your Results")

# Prepare the data for a single CSV file
# It will include standard curve data, unknown analysis data, and the final calculated original concentration.
def generate_combined_csv(std_df, unknown_df, final_conc, beverage_name, slope_val, intercept_val):
    combined_content = f"Standard Curve Data:\n"
    combined_content += std_df.to_csv(index=False)
    combined_content += "\n\n--- Linear Fit Equation ---\n"
    combined_content += f"Absorbance = {slope_val:.3f} * Concentration + {intercept_val:.3f}\n\n"
    combined_content += f"Beverage Analysis Data for {beverage_name}:\n"
    combined_content += unknown_df.to_csv(index=False)
    
    if not np.isnan(final_conc): # Check if final_conc was successfully calculated
        combined_content += f"\n\n--- Final Original Concentration for {beverage_name} ---\n"
        combined_content += f"Original Glucose Concentration: {final_conc:.3f} mg/mL\n"
    else:
        combined_content += "\n\n--- Final Original Concentration ---\n"
        combined_content += "Not calculated or invalid input.\n"
        
    return combined_content.encode('utf-8')

# Ensure variables are defined for the download function, even if inputs haven't been made yet
# Use default values or check if inputs have been interacted with
final_original_conc_for_download = original_conc_final if 'original_conc_final' in locals() else np.nan
current_beverage_name_for_download = beverage if beverage else "Unknown_Beverage"

st.download_button(
    label="Download All DNS Assay Results (.csv)",
    data=generate_combined_csv(edited_std, edited_unknown, final_original_conc_for_download, 
                               current_beverage_name_for_download, slope, intercept),
    file_name=f"{current_beverage_name_for_download.replace(' ', '_')}_DNS_Assay_Results.csv",
    mime="text/csv",
    key="download_all_results"
)
