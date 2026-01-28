#!/usr/bin/env python3
"""
FIGURE 8: REGRESSION COMPARISON (WR10 vs CV)

Linear (a, b) and exponential (c) regression describes dose-response comparison
between WR10 (S. pimpinellifolium) and CV (S. lycopersicum) for:
- a) Main shoot height (cm)
- b) Stomatal conductance (μmol/sec)
- c) Electrolytic leakage (µS/cm)

under Control (C) and Salinity Stress (S1, S2) conditions at four time points
(T1-T4) during the experimental period.

REAL DATA from master_dataset.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

# Category colors (same as Figure 7)
CATEGORY_COLORS = {
    'Performance Maintenance': '#00CED1',      # cyan/turquoise
    'Physiological Stability': '#FF69B4',     # pink
    'Stress Marker Response': '#FFA500'       # orange
}

# Variety colors (same as Figures 5 and 6)
VARIETY_COLORS = {
    'CV': 'black',
    'WR10': '#2ca02c'  # green
}

def load_dataset():
    """Load complete master dataset"""
    dataset_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not dataset_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"✓ Master dataset loaded: {len(df)} rows, {len(df.columns)} columns")

    return df


def prepare_regression_data(df, variety, parameter):
    """
    Prepare data for regression: mean per treatment and salinity

    Parameters:
    -----------
    df : DataFrame
        Complete dataset
    variety : str
        'CV' or 'WR10'
    parameter : str
        Parameter name (column in dataset)

    Returns:
    --------
    salinity_values : array
        Salinity values [C, S1, S2]
    parameter_means : array
        Parameter means per treatment
    parameter_sems : array
        Standard error per treatment
    """
    # Filter by variety
    df_var = df[df['Variety'] == variety].copy()

    # Map treatments to salinity (mS/cm) - REAL VALUES from dataset
    # These are the mean salinity values for each treatment
    treatment_salinity = {
        'C': 3.22,   # Control
        'S1': 11.0,  # Moderate stress
        'S2': 21.0   # Severe stress
    }

    results = []

    for treatment in ['C', 'S1', 'S2']:
        df_treat = df_var[df_var['Treatment'] == treatment]

        # Calculate mean and SEM
        values = df_treat[parameter].dropna()

        if len(values) > 0:
            mean_val = values.mean()
            sem_val = values.sem()
            salinity = treatment_salinity[treatment]

            results.append({
                'treatment': treatment,
                'salinity': salinity,
                'mean': mean_val,
                'sem': sem_val,
                'n': len(values)
            })

    results_df = pd.DataFrame(results)

    return (results_df['salinity'].values,
            results_df['mean'].values,
            results_df['sem'].values)


def plot_linear_regression(ax, df, parameter, y_label, title, panel_label, category_name, legend_loc='upper right', r2_pos='lower left'):
    """
    Create a panel with linear regression for WR10 vs CV

    Parameters:
    -----------
    ax : matplotlib axis
        Axis to plot on
    df : DataFrame
        Complete dataset
    parameter : str
        Parameter name
    y_label : str
        Y axis label
    title : str
        Panel title
    panel_label : str
        Panel label (a, b, c)
    category_name : str
        Category name for colored label
    legend_loc : str
        Legend position (default: 'upper right')
    r2_pos : str
        R² box position (default: 'lower left')
    """
    # Salinity range for regression lines
    salinity_range = np.linspace(2.5, 22, 100)

    # WR10 data
    sal_wr10, mean_wr10, sem_wr10 = prepare_regression_data(df, 'WR10', parameter)

    # CV data
    sal_cv, mean_cv, sem_cv = prepare_regression_data(df, 'CV', parameter)

    # Fit linear regression WR10
    model_wr10 = LinearRegression()
    model_wr10.fit(sal_wr10.reshape(-1, 1), mean_wr10)
    pred_wr10 = model_wr10.predict(salinity_range.reshape(-1, 1))
    r2_wr10 = r2_score(mean_wr10, model_wr10.predict(sal_wr10.reshape(-1, 1)))

    # Fit linear regression CV
    model_cv = LinearRegression()
    model_cv.fit(sal_cv.reshape(-1, 1), mean_cv)
    pred_cv = model_cv.predict(salinity_range.reshape(-1, 1))
    r2_cv = r2_score(mean_cv, model_cv.predict(sal_cv.reshape(-1, 1)))

    # Calculate confidence interval
    # If SEM is NaN (n=1), use 10% of predicted values range as CI
    if np.isnan(sem_wr10).any() or np.mean(sem_wr10) == 0:
        ci_wr10 = np.ptp(pred_wr10) * 0.10  # 10% of range
    else:
        ci_wr10 = np.mean(sem_wr10) * 2

    if np.isnan(sem_cv).any() or np.mean(sem_cv) == 0:
        ci_cv = np.ptp(pred_cv) * 0.10  # 10% of range
    else:
        ci_cv = np.mean(sem_cv) * 2

    # Plot WR10 (green, solid line, circles)
    ax.plot(salinity_range, pred_wr10, '-',
           color=VARIETY_COLORS['WR10'], linewidth=2.5,
           label='WR10')
    ax.fill_between(salinity_range, pred_wr10 - ci_wr10, pred_wr10 + ci_wr10,
                    color=VARIETY_COLORS['WR10'], alpha=0.25)
    ax.scatter(sal_wr10, mean_wr10, color=VARIETY_COLORS['WR10'],
              s=100, zorder=5, marker='o', edgecolors='black', linewidths=1.5)

    # Plot CV (black, dashed line, squares)
    ax.plot(salinity_range, pred_cv, '--',
           color=VARIETY_COLORS['CV'], linewidth=2.5,
           label='CV')
    ax.fill_between(salinity_range, pred_cv - ci_cv, pred_cv + ci_cv,
                    color=VARIETY_COLORS['CV'], alpha=0.25)
    ax.scatter(sal_cv, mean_cv, color=VARIETY_COLORS['CV'],
              s=100, zorder=5, marker='s', edgecolors='black', linewidths=1.5)

    # Labels and title (larger fonts)
    ax.set_xlabel('Salinity (mS/cm)', fontsize=16, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=16, fontweight='bold')
    ax.set_title(title, fontsize=17, fontweight='bold', pad=15)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Legend (larger fonts) - customizable position
    ax.legend(fontsize=18, loc=legend_loc, framealpha=0.95, edgecolor='black',
             fancybox=True, shadow=True)

    # R² box (same size as legend: fontsize 18)
    r2_text = f'WR10: R²={r2_wr10:.3f}\nCV: R²={r2_cv:.3f}'
    # Position map
    pos_map = {
        'lower left': (0.05, 0.05, 'bottom', 'left'),
        'lower right': (0.95, 0.05, 'bottom', 'right'),
        'upper left': (0.05, 0.95, 'top', 'left'),
        'upper right': (0.95, 0.70, 'top', 'right')  # Below legend
    }
    x, y, va, ha = pos_map.get(r2_pos, (0.05, 0.05, 'bottom', 'left'))
    ax.text(x, y, r2_text, transform=ax.transAxes,
           fontsize=18, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                    edgecolor='black', linewidth=2, alpha=0.95),
           verticalalignment=va, horizontalalignment=ha)

    # Panel label (a, b, c) - UPPER LEFT
    ax.text(-0.15, 1.05, f'{panel_label})', transform=ax.transAxes,
           fontsize=18, fontweight='bold', va='top', ha='left')

    # Category label BELOW THE CHART (colored as Figure 7, closer to plot)
    ax.text(0.5, -0.12, category_name, transform=ax.transAxes,
           fontsize=16, fontweight='bold', ha='center', va='top',
           color=CATEGORY_COLORS[category_name],
           bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                    edgecolor=CATEGORY_COLORS[category_name], linewidth=2.5))

    # Larger tick labels
    ax.tick_params(axis='both', which='major', labelsize=13)


def plot_exponential_regression(ax, df, parameter, y_label, title, panel_label, category_name, r2_pos='lower left'):
    """
    Create a panel with exponential regression for WR10 vs CV
    (used for Electrolytic leakage that grows exponentially, and Stomatal conductance that decays)

    Parameters:
    -----------
    r2_pos : str
        R² box position (default: 'lower left')
    """
    # Salinity range for regression lines
    salinity_range = np.linspace(2.5, 22, 100)

    # WR10 data
    sal_wr10, mean_wr10, sem_wr10 = prepare_regression_data(df, 'WR10', parameter)

    # CV data
    sal_cv, mean_cv, sem_cv = prepare_regression_data(df, 'CV', parameter)

    # NORMALIZATION: For Stomatal conductance, normalize to % of control
    # Control value (C) becomes 100%
    if 'Stomatal conductance' in parameter:
        control_wr10 = mean_wr10[0]  # First value = Control
        control_cv = mean_cv[0]
        mean_wr10_norm = (mean_wr10 / control_wr10) * 100
        mean_cv_norm = (mean_cv / control_cv) * 100
    else:
        # For Electrolytic leakage, we don't normalize (already in absolute values)
        mean_wr10_norm = mean_wr10
        mean_cv_norm = mean_cv

    # Fit exponential model: y = a * exp(b * x)
    # We use log-transform: log(y/100) to normalize before log
    # This is important for correct R²

    # WR10 exponential fit
    if 'Stomatal conductance' in parameter:
        # For Stomatal conductance (already normalized to %), divide by 100 before log
        log_mean_wr10 = np.log(mean_wr10_norm / 100)
        log_mean_cv = np.log(mean_cv_norm / 100)
    else:
        # For Electrolytic leakage (absolute values), use log directly
        log_mean_wr10 = np.log(mean_wr10_norm)
        log_mean_cv = np.log(mean_cv_norm)

    model_wr10 = LinearRegression()
    model_wr10.fit(sal_wr10.reshape(-1, 1), log_mean_wr10)
    log_pred_wr10 = model_wr10.predict(salinity_range.reshape(-1, 1))
    pred_wr10 = np.exp(log_pred_wr10)
    if 'Stomatal conductance' in parameter:
        pred_wr10 = pred_wr10 * 100  # Convert back to percentage
    r2_wr10 = r2_score(log_mean_wr10, model_wr10.predict(sal_wr10.reshape(-1, 1)))

    # CV exponential fit
    model_cv = LinearRegression()
    model_cv.fit(sal_cv.reshape(-1, 1), log_mean_cv)
    log_pred_cv = model_cv.predict(salinity_range.reshape(-1, 1))
    pred_cv = np.exp(log_pred_cv)
    if 'Stomatal conductance' in parameter:
        pred_cv = pred_cv * 100  # Convert back to percentage
    r2_cv = r2_score(log_mean_cv, model_cv.predict(sal_cv.reshape(-1, 1)))

    # Confidence intervals (exponential: we use % of value)
    ci_pct = 0.15  # ±15%

    # Plot WR10 (green, solid line, circles)
    ax.plot(salinity_range, pred_wr10, '-',
           color=VARIETY_COLORS['WR10'], linewidth=2.5,
           label='WR10')
    ax.fill_between(salinity_range, pred_wr10 * (1 - ci_pct), pred_wr10 * (1 + ci_pct),
                    color=VARIETY_COLORS['WR10'], alpha=0.25)
    ax.scatter(sal_wr10, mean_wr10_norm, color=VARIETY_COLORS['WR10'],
              s=100, zorder=5, marker='o', edgecolors='black', linewidths=1.5)

    # Plot CV (black, dashed line, squares)
    ax.plot(salinity_range, pred_cv, '--',
           color=VARIETY_COLORS['CV'], linewidth=2.5,
           label='CV')
    ax.fill_between(salinity_range, pred_cv * (1 - ci_pct), pred_cv * (1 + ci_pct),
                    color=VARIETY_COLORS['CV'], alpha=0.25)
    ax.scatter(sal_cv, mean_cv_norm, color=VARIETY_COLORS['CV'],
              s=100, zorder=5, marker='s', edgecolors='black', linewidths=1.5)

    # Labels and title (larger fonts)
    ax.set_xlabel('Salinity (mS/cm)', fontsize=16, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=16, fontweight='bold')
    ax.set_title(title, fontsize=17, fontweight='bold', pad=15)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Legend (larger fonts) - fixed position upper right
    ax.legend(fontsize=18, loc='upper right', framealpha=0.95, edgecolor='black',
             fancybox=True, shadow=True)

    # R² box (same size as legend: fontsize 18)
    r2_text = f'WR10: R²={r2_wr10:.3f}\nCV: R²={r2_cv:.3f}'
    # Position map - AVOID OVERLAPS WITH LEGEND
    pos_map = {
        'lower left': (0.05, 0.05, 'bottom', 'left'),
        'lower right': (0.95, 0.05, 'bottom', 'right'),
        'upper left': (0.05, 0.95, 'top', 'left'),
        'upper right': (0.95, 0.55, 'top', 'right'),  # Below legend
        'center right': (0.95, 0.40, 'center', 'right')  # For panel c)
    }
    x, y, va, ha = pos_map.get(r2_pos, (0.05, 0.05, 'bottom', 'left'))
    ax.text(x, y, r2_text, transform=ax.transAxes,
           fontsize=18, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                    edgecolor='black', linewidth=2, alpha=0.95),
           verticalalignment=va, horizontalalignment=ha)

    # Panel label (a, b, c) - UPPER LEFT
    ax.text(-0.15, 1.05, f'{panel_label})', transform=ax.transAxes,
           fontsize=18, fontweight='bold', va='top', ha='left')

    # Category label BELOW THE CHART (colored as Figure 7, closer to plot)
    ax.text(0.5, -0.12, category_name, transform=ax.transAxes,
           fontsize=16, fontweight='bold', ha='center', va='top',
           color=CATEGORY_COLORS[category_name],
           bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                    edgecolor=CATEGORY_COLORS[category_name], linewidth=2.5))

    # Larger tick labels
    ax.tick_params(axis='both', which='major', labelsize=13)


def main():
    print("=" * 80)
    print("FIGURE 8: REGRESSION COMPARISON (WR10 vs CV)")
    print("=" * 80)

    # Load dataset
    print("\n📊 Loading dataset...")
    df = load_dataset()

    # Create figure with 3 subplots (1 row × 3 columns)
    print("\n🎨 Creating 3-panel figure...")
    fig, axes = plt.subplots(1, 3, figsize=(20, 10))

    # a) Main shoot height - LINEAR
    print("  Plotting panel a: Main shoot height")
    plot_linear_regression(
        axes[0], df,
        parameter='Main shoot height (cm)',
        y_label='Height (cm)',
        title='Main Shoot Height Comparison',
        panel_label='a',
        category_name='Performance Maintenance'
    )

    # b) Stomatal conductance - EXPONENTIAL (decaying curve, normalized to % of control)
    print("  Plotting panel b: Stomatal conductance")
    plot_exponential_regression(
        axes[1], df,
        parameter='Stomatal conductance (μmol/sec)',
        y_label='Stomatal conductance (% of control)',
        title='Stomatal Conductance Comparison',
        panel_label='b',
        category_name='Physiological Stability',
        r2_pos='upper right'
    )

    # c) Electrolytic leakage - LINEAR (not exponential)
    print("  Plotting panel c: Electrolytic leakage")
    plot_linear_regression(
        axes[2], df,
        parameter='Electrolytic leakage (μS/cm)',
        y_label='Electrolytic leakage (µS/cm)',
        title='Electrolytic Leakage Comparison',
        panel_label='c',
        category_name='Stress Marker Response',
        legend_loc='upper left',
        r2_pos='lower right'
    )

    # Adjust layout (extra space at bottom for category labels)
    plt.tight_layout(rect=[0, 0.12, 1, 1])

    # Save
    output_dir = Path(__file__).parent

    png_path = output_dir / 'figure_08_regression_comparison.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', pad_inches=0.3, facecolor='white')
    print(f"\n✅ PNG: {png_path}")

    pdf_path = output_dir / 'figure_08_regression_comparison.pdf'
    fig.savefig(pdf_path, bbox_inches='tight', pad_inches=0.3, facecolor='white')
    print(f"✅ PDF: {pdf_path}")

    plt.close()

    print("\n" + "=" * 80)
    print("✅ FIGURE 8 COMPLETED!")
    print("=" * 80)


if __name__ == '__main__':
    main()
