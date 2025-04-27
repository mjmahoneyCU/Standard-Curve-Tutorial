import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

st.set_page_config(page_title="DNS Assay: Standard Curve Tool", layout="wide")

st.title("🧪 DNS Assay: Build and Use a Standard Curve")

with st.expander("📘 Background Briefing: What Are We Doing and Why?", expanded=True):
    st.markdown("""
### Welcome to the Lab!
You're part of a biotech team helping a nutrition research group analyze sugar content in beverages using a color-based chemical test called the **DNS assay**. Today, you're going to:

1. Make a **standard curve** using glucose solutions with known concentrations.
2. Use the **DNS assay** to measure how much sugar is in an unknown drink (like a soda or juice).
3. Use the absorbance (color intensity) readings from your samples to **estimate glucose concentration** using your standard curve.

### What is the DNS Assay?
The **DNS assay** (3,5-dinitrosalicylic acid) is a colorimetric test that detects **reducing sugars** like glucose. When DNS reacts with glucose under heat, it turns orange or red — the more glucose, the darker the color.

- You measure this color using a **spectrophotometer** at 540 nm.
- The result is called **absorbance** (AU = absorbance units).

### What is a Standard Curve?
A **standard curve** is a graph that shows the relationship between:
- **Known concentrations** of a substance (x-axis)
- Their corresponding **absorbance readings** (y-axis)

Once you graph this data, a **line of best fit** is drawn. This line has an equation in the form:

\[ \text{Absorbance} = m \times \text{Concentration} + b \]

Where:
- \( m \) is the slope (how steep the line is)
- \( b \) is the y-intercept (where the line crosses the y-axis)

You will use this equation to calculate the glucose concentration of an unknown beverage sample based on its absorbance.

### Why Do We Use Dilutions?
Beverages like soda often contain a lot of sugar. If you test them directly, the absorbance might be **too high** and fall **outside the linear region** of your standard curve.

To fix that, we **dilute** the drink with water — for example:
- A **1:10 dilution** means 1 part soda and 9 parts water.

Then you test the diluted sample and use your standard curve to calculate the sugar content in the original drink.

### What is the Linear Region?
The **linear region** is the part of your standard curve where the absorbance increases in direct proportion to concentration.

- This is the most **accurate range** to estimate unknowns.
- If your sample's absorbance is too high or low (outside this range), it may give **inaccurate results**.
""")

st.markdown("---")

st.header("📊 Step 1: Enter Your Standard Curve Data")

with st.expander("Enter absorbance values for your glucose standards"):
    concs = [0.0, 0.1, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0]  # mg/mL
    default_abs = [0.00, 0.05, 0.15, 0.30, 0.55, 0.80, 1.00, 1.20]
    df_std = pd.DataFrame({"Glucose (mg/mL)": concs, "Absorbance (AU)": default_abs})
    edited_std = st.data_editor(df_std, key="std_editor")

# Fit linear regression to determine linear region
x = edited_std["Glucose (mg/mL)"].values
y = edited_std["Absorbance (AU)"].values

slope, intercept, r_value, p_value, std_err = linregress(x, y)

st.write(f"**Linear Fit Equation:** Absorbance = {slope:.3f} * Concentration + {intercept:.3f}")

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

st.markdown("""
Try different dilutions to make sure the absorbance of your beverage sample falls within the **linear region** of your curve.
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
            est_conc = (abs_val - intercept) / slope
            return round(est_conc, 3)
        except:
            return ""

    edited_unknown["Estimated Glucose (mg/mL)"] = edited_unknown["Absorbance (AU)"].apply(estimate_concentration)
    st.dataframe(edited_unknown)

st.markdown("---")

st.header("🧠 Reflection")

st.text_area("1. What did you learn about using a standard curve to determine unknown concentrations?")
st.text_area("2. How did the sugar content in your chosen beverage compare to the diet soda?")
st.text_area("3. Why is it important to dilute your sample to fit within the linear range of your curve?")
st.text_area("4. What would happen if your sample’s absorbance was too high?")

st.success("Great job applying real-world biotech tools to everyday products!")


