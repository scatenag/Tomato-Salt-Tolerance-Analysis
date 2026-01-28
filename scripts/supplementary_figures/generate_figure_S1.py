#!/usr/bin/env python3
"""
Figure S1: Effect of salinity on Osmotic Regulation/Ionic Balance

Heatmap showing pathway activity levels (Fold Change vs Control) across varieties
and treatments for Osmotic Regulation/Ionic Balance parameters.

Comparison: Control (C) vs Severe Salinity Stress (S2)
Statistical significance: Welch's t-test with asterisks (***p<0.001, **p<0.01, *p<0.05)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

# Parameters for Figure S1: Osmotic Regulation/Ionic Balance
FIGURE_PARAMS = [
    'Electrolytic leakage (μS/cm)',
    'Na/Ca ratio leaves',
    'Na/Ca ratio roots',
    'Na/K ratio leaves',
    'Na/K ratio roots',
    'Relative water content (%)'
]

# Display names (shorter for heatmap)
PARAM_DISPLAY_NAMES = {
    'Electrolytic leakage (μS/cm)': 'Electrolytic leakage (μS/cm)',
    'Na/Ca ratio leaves': 'Na/Ca ratio leaves',
    'Na/Ca ratio roots': 'Na/Ca ratio roots',
    'Na/K ratio leaves': 'Na/K ratio leaves',
    'Na/K ratio roots': 'Na/K ratio roots',
    'Relative water content (%)': 'Relative water content (%)'
}

# Varieties in order
VARIETIES = ['CV', 'WR2', 'WR9', 'WR10', 'WR11', 'WR14']

# Figure title
FIGURE_TITLE = 'Osmotic Regulation/Ionic Balance'


def load_data():
    """Load master dataset"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not data_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    print(f"✓ Master dataset loaded: {len(df)} rows")

    return df


def calculate_activity_score(df, param, variety):
    """
    Calculate Activity Score (Fold Change vs Control)

    Activity Score = (mean_S2 - mean_C) / mean_C
    """
    control_data = df[(df['Treatment'] == 'C') & (df['Variety'] == variety)][param].dropna()
    stress_data = df[(df['Treatment'] == 'S2') & (df['Variety'] == variety)][param].dropna()

    if len(control_data) == 0 or len(stress_data) == 0:
        return np.nan

    control_mean = control_data.mean()
    stress_mean = stress_data.mean()

    if control_mean == 0:
        return np.nan

    # Activity score = fold change
    activity_score = (stress_mean - control_mean) / control_mean

    return activity_score


def calculate_significance(df, param, variety):
    """
    Calculate statistical significance using Welch's t-test

    Returns: p-value and significance symbol
    """
    control_data = df[(df['Treatment'] == 'C') & (df['Variety'] == variety)][param].dropna()
    stress_data = df[(df['Treatment'] == 'S2') & (df['Variety'] == variety)][param].dropna()

    if len(control_data) < 2 or len(stress_data) < 2:
        return np.nan, ''

    try:
        # Welch's t-test (does not assume equal variances)
        t_stat, p_value = stats.ttest_ind(control_data, stress_data, equal_var=False)

        # Determine significance symbol
        if p_value < 0.001:
            sig = '***'
        elif p_value < 0.01:
            sig = '**'
        elif p_value < 0.05:
            sig = '*'
        else:
            sig = ''

        return p_value, sig
    except:
        return np.nan, ''


def create_heatmap_data(df):
    """
    Create matrix for heatmap: parameters (rows) x varieties (columns)
    """
    data_matrix = []
    sig_matrix = []

    for param in FIGURE_PARAMS:
        row_data = []
        row_sig = []

        for variety in VARIETIES:
            score = calculate_activity_score(df, param, variety)
            p_val, sig = calculate_significance(df, param, variety)

            row_data.append(score)
            row_sig.append(sig)

        data_matrix.append(row_data)
        sig_matrix.append(row_sig)

    return np.array(data_matrix), sig_matrix


def plot_heatmap(data_matrix, sig_matrix, ax):
    """
    Plot heatmap with activity scores and significance asterisks
    """
    # Create heatmap
    # Use diverging colormap: blue (negative) - white (0) - red (positive)
    vmax = max(abs(np.nanmin(data_matrix)), abs(np.nanmax(data_matrix)))
    vmin = -vmax

    # Custom colormap similar to the PDF
    cmap = sns.diverging_palette(240, 10, as_cmap=True)  # Blue to Red

    im = ax.imshow(data_matrix, cmap=cmap, aspect='auto', vmin=-3, vmax=3)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('Activity Score (Fold Change vs Control)', fontsize=11, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)

    # Set tick labels
    ax.set_xticks(range(len(VARIETIES)))
    ax.set_xticklabels(VARIETIES, fontsize=12, fontweight='bold')

    ax.set_yticks(range(len(FIGURE_PARAMS)))
    param_labels = [PARAM_DISPLAY_NAMES.get(p, p) for p in FIGURE_PARAMS]
    ax.set_yticklabels(param_labels, fontsize=11)

    # Add values and significance asterisks in cells
    for i in range(len(FIGURE_PARAMS)):
        for j in range(len(VARIETIES)):
            value = data_matrix[i, j]
            sig = sig_matrix[i][j]

            if np.isnan(value):
                text = 'N/A'
            else:
                # Format: value with asterisks
                text = f'{value:.2f}'
                if sig:
                    text = f'{value:.2f}\n{sig}'

            # Text color: white for dark cells, black for light cells
            text_color = 'white' if abs(value) > 1.5 else 'black'

            ax.text(j, i, text, ha='center', va='center',
                   fontsize=10, fontweight='bold', color=text_color)

    # Add grid lines
    for i in range(len(FIGURE_PARAMS) + 1):
        ax.axhline(i - 0.5, color='white', linewidth=0.5)
    for j in range(len(VARIETIES) + 1):
        ax.axvline(j - 0.5, color='white', linewidth=0.5)

    ax.tick_params(length=0)


def main():
    print("=" * 70)
    print("FIGURE S1: OSMOTIC REGULATION/IONIC BALANCE")
    print("=" * 70)

    # Load data
    print("\n📊 Loading dataset...")
    df = load_data()

    # Create heatmap data
    print("\n📈 Calculating activity scores and significance...")
    data_matrix, sig_matrix = create_heatmap_data(df)

    # Print summary
    print("\n📋 Activity Scores Summary:")
    for i, param in enumerate(FIGURE_PARAMS):
        print(f"  {param}:")
        for j, variety in enumerate(VARIETIES):
            score = data_matrix[i, j]
            sig = sig_matrix[i][j]
            if not np.isnan(score):
                print(f"    {variety}: {score:.2f} {sig}")

    # Create figure
    print("\n🎨 Creating figure...")
    fig, ax = plt.subplots(figsize=(10, 7))

    plot_heatmap(data_matrix, sig_matrix, ax)

    # Title
    ax.set_title(f'Fig. S1: {FIGURE_TITLE}', fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    # Save
    output_dir = Path(__file__).parent

    png_path = output_dir / 'figure_S1_osmotic_regulation.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ PNG: {png_path}")

    pdf_path = output_dir / 'figure_S1_osmotic_regulation.pdf'
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF: {pdf_path}")

    plt.close()

    print("\n" + "=" * 70)
    print("✅ FIGURE S1 COMPLETED!")
    print("=" * 70)


if __name__ == '__main__':
    main()
