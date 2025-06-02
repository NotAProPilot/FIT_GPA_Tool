# Imports: Streamlit for UI, pandas/numpy for data handling,
# Plotly for interactive plotting, and scipy for statistical functions.
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import percentileofscore, gaussian_kde

# Set Streamlit page configuration
st.set_page_config(page_title="GPA Analyzer", layout="centered")
st.title("📊 GPA Analyzer & Visualizer")

# Step 1: Upload an Excel file (.xlsx) through file uploader
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Parse uploaded Excel file and let the user choose a sheet
    xls = pd.ExcelFile(uploaded_file)
    sheet = st.selectbox("Choose a sheet:", xls.sheet_names)
    df = xls.parse(sheet)

    # Extract numeric columns to identify valid GPA candidates
    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    if not numeric_columns:
        st.warning("No numeric columns found!")
    else:
        # Let user select the GPA column
        gpa_column = st.selectbox("Choose the GPA column:", numeric_columns)

        # Coerce GPA values to numeric, drop NaNs, and filter to [0, 4] range
        gpas = pd.to_numeric(df[gpa_column], errors='coerce').dropna()
        gpas = gpas[(gpas >= 0) & (gpas <= 4)]

        # --- Histogram Section ---

        st.subheader("📈 GPA Distribution Histogram (0.1 bins)")

        # Define histogram bins and labels
        bins = np.arange(0, 4.1, 0.1)
        bin_labels = [f"{bins[i]:.2f}-{bins[i+1]-0.01:.2f}" for i in range(len(bins) - 1)]
        counts, _ = np.histogram(gpas, bins=bins)

        # Plot histogram using Plotly
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Bar(x=bin_labels, y=counts, marker_color="mediumslateblue"))
        fig_hist.update_layout(
            xaxis_title="GPA Range",
            yaxis_title="Number of Students",
            title="Histogram of GPAs",
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # --- Percentile Estimation from Input GPA ---

        st.subheader("🔍 See Your Percentile")

        # Allow user to input their GPA to see percentile ranking
        user_gpa = st.number_input("Enter your GPA", min_value=0.0, max_value=4.0, step=0.01)
        if user_gpa:
            percentile = percentileofscore(gpas, user_gpa)
            st.success(f"Your GPA of {user_gpa:.2f} is in the {percentile:.2f}th percentile.")

        # --- Bell Curve Visualization ---

        st.subheader("🔔 GPA Percentile Bell Curve")

        # Estimate GPA distribution using kernel density estimation (KDE)
        kde = gaussian_kde(gpas)
        x_vals = np.linspace(0, 4.0, 500)
        y_vals = kde(x_vals)

        # Let user select GPA using a slider to see their percentile on the curve
        slider_gpa = st.slider("📍 Drag your GPA", min_value=0.0, max_value=4.0, value=3.0, step=0.01)
        slider_percentile = percentileofscore(gpas, slider_gpa)
        y_slider = kde(slider_gpa)

        fig_bell = go.Figure()

        # Add KDE bell curve line and area fill
        fig_bell.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='lines',
            line=dict(color='royalblue', width=3),
            fill='tozeroy',
            name='GPA Distribution'
        ))

        # Add user's GPA marker on the bell curve
        fig_bell.add_trace(go.Scatter(
            x=[slider_gpa], y=[y_slider],
            mode='markers+text',
            marker=dict(color='crimson', size=10),
            text=[f"{slider_percentile:.1f}th %"],
            textposition="top center",
            name="Your GPA"
        ))

        # Optional: Add standard percentile markers (like IQ curve)
        for p in [16, 50, 84]:
            gpa_at_p = np.percentile(gpas, p)
            y_at_p = kde(gpa_at_p)
            fig_bell.add_trace(go.Scatter(
                x=[gpa_at_p], y=[y_at_p],
                mode='markers+text',
                marker=dict(color='orange', size=8),
                text=[f"{p}th"],
                textposition="bottom center",
                name=f"{p}th Percentile"
            ))

        # Finalize bell curve layout
        fig_bell.update_layout(
            title="GPA Percentile Bell Curve",
            xaxis_title="GPA",
            yaxis_title="Density (not frequency)",
            showlegend=False,
            height=500
        )

        st.plotly_chart(fig_bell, use_container_width=True)

        # --- Inverse Query: Percentile to Required GPA ---

        st.subheader("🎯 Target Percentile to GPA")

        # Let user choose a target percentile and see required GPA to reach it
        target_percentile = st.slider("Choose your desired percentile", min_value=0.0, max_value=100.0, value=90.0, step=0.1)
        gpa_needed = np.percentile(gpas, target_percentile)

        st.info(f"To be in the **{target_percentile:.1f}th** percentile, you'd need a GPA of at least **{gpa_needed:.2f}**.")
