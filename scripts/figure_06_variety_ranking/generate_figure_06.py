#!/usr/bin/env python3
"""
Figure 6: Variety Ranking and Category Contribution

Two-panel figure showing:
a) Final Stress Tolerance Ranking - Simple horizontal bars with total scores
b) Category Contribution - Stacked horizontal bars showing 3 categories

Based on: integrated_systems_biology_report page 29
Data: CALCULATED from master_dataset.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

# Configuration
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

# Varieties
VARIETIES = ['CV', 'WR2', 'WR9', 'WR10', 'WR11', 'WR14']

# Variety colors (same as Figure 5)
VARIETY_COLORS = {
    'CV': '#000000',      # black
    'WR2': '#FF0000',     # red
    'WR9': '#00BFFF',     # light blue (deep sky blue)
    'WR10': '#00FF00',    # green
    'WR11': '#FFFF00',    # yellow
    'WR14': '#9370DB'     # purple (medium purple)
}

# THREE categories (as in original report)
CATEGORY_COLORS = {
    'Performance Maintenance': '#4ECDC4',      # turquoise
    'Physiological Stability': '#F38181',      # pink/coral
    'Stress Marker Response': '#FFA07A'        # light orange
}

# Category weights (from variety_ranking_analyzer.py)
CATEGORY_WEIGHTS = {
    'Performance Maintenance': 0.55,
    'Physiological Stability': 0.25,
    'Stress Marker Response': 0.20
}

# Parameters per category
PERFORMANCE_PARAMS = [
    'Total dry weight (g)',
    'fresh weight 10 fruits (g)',
    'Fruit set (trusses number)',
    'Main shoot height (cm)',
    'Flowering (trusses number)',
    'Leaves surface (cm²)',
    'Days_to_next_phase_from_prev_start',
    'Days_to_next_phase_from_time_0'
]

PHYSIOLOGICAL_PARAMS = [
    'Fv/Fm',
    'Total chlorophyll (μg/g FW)',
    'Relative water content (%)',
    'Stomatal conductance (μmol/sec)'
]

STRESS_MARKER_PARAMS = [
    'Electrolytic leakage (μS/cm)',
    'Na/K ratio leaves',
    'Na/K ratio roots',
    'ABA (ng/mg)',
    'Osmolytes (osm/kg)'
]


def load_data():
    """Load data from master dataset"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not data_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    print(f"✓ Master dataset loaded: {len(df)} rows")

    return df


def calculate_performance_score(df, variety):
    """Calculate performance maintenance score for a variety"""
    scores = []

    for param in PERFORMANCE_PARAMS:
        if param not in df.columns:
            continue

        # Control vs stress data
        control_data = df[
            (df['Variety'] == variety) &
            (df['Treatment'] == 'C')
        ][param].dropna()

        stress_data = df[
            (df['Variety'] == variety) &
            (df['Treatment'].isin(['S1', 'S2']))
        ][param].dropna()

        if len(control_data) == 0 or len(stress_data) == 0:
            continue

        # Stress/control ratio (performance maintenance)
        control_mean = control_data.mean()
        stress_mean = stress_data.mean()

        if control_mean != 0:
            ratio = stress_mean / control_mean

            # For temporal parameters (Days...), less is better
            # If stress increases days (delay), ratio > 1 -> penalty
            # If stress decreases days (advance), ratio < 1 -> bonus
            if 'Days_' in param:
                # Invert logic: 2.0 - ratio (max 2.0)
                # Example: ratio 1.1 (10% delay) -> 0.9 score
                # Example: ratio 0.9 (10% advance) -> 1.1 score
                ratio = min(2.0, 2.0 - ratio)

            scores.append(max(0, ratio))  # Min 0

    return np.mean(scores) if scores else 0


def calculate_stability_score(df, variety):
    """Calculate physiological stability score for a variety"""
    stability_scores = []

    for param in PHYSIOLOGICAL_PARAMS:
        if param not in df.columns:
            continue

        # Control vs stress variability
        control_data = df[
            (df['Variety'] == variety) &
            (df['Treatment'] == 'C')
        ][param].dropna()

        stress_data = df[
            (df['Variety'] == variety) &
            (df['Treatment'].isin(['S1', 'S2']))
        ][param].dropna()

        if len(control_data) < 2 or len(stress_data) < 2:
            continue

        control_std = control_data.std()
        stress_std = stress_data.std()

        # Stability = control_std / stress_std
        # Values > 1 = more stable under stress
        if stress_std > 0 and not pd.isna(stress_std) and not pd.isna(control_std):
            stability = control_std / stress_std
            stability_scores.append(min(2.0, stability))  # Max 2.0

    return np.mean(stability_scores) if stability_scores else 1.0


def calculate_marker_score(df, variety):
    """Calculate stress marker score for a variety"""
    marker_scores = []

    for param in STRESS_MARKER_PARAMS:
        if param not in df.columns:
            continue

        # Control vs stress data
        control_data = df[
            (df['Variety'] == variety) &
            (df['Treatment'] == 'C')
        ][param].dropna()

        stress_data = df[
            (df['Variety'] == variety) &
            (df['Treatment'].isin(['S1', 'S2']))
        ][param].dropna()

        if len(control_data) < 2 or len(stress_data) < 2:
            continue

        try:
            # T-test for significance
            t_stat, p_value = stats.ttest_ind(control_data, stress_data)

            # Score based on significance and direction
            control_mean = control_data.mean()
            stress_mean = stress_data.mean()

            # For stress markers: moderate increase = good
            if stress_mean > control_mean:
                # Increase: score based on moderate fold change
                fold_change = stress_mean / control_mean if control_mean != 0 else 1
                # Ideal: fold change between 1.2 and 2.0
                if 1.2 <= fold_change <= 2.0:
                    score = 1.0
                elif fold_change > 2.0:
                    score = max(0, 2.0 - (fold_change - 2.0) * 0.3)
                else:
                    score = fold_change / 1.2
            else:
                # Decrease: not ideal for stress markers
                score = 0.5

            marker_scores.append(score)
        except:
            continue

    return np.mean(marker_scores) if marker_scores else 0.5


def calculate_variety_ranking(df):
    """Calculate complete variety ranking from dataset"""
    print("\n📊 Calculating variety ranking from dataset...")

    variety_scores = {}

    for variety in VARIETIES:
        print(f"\n  Analyzing {variety}...")

        # Calculate score for each category
        perf_score = calculate_performance_score(df, variety)
        stab_score = calculate_stability_score(df, variety)
        marker_score = calculate_marker_score(df, variety)

        # Apply weights
        perf_weighted = perf_score * CATEGORY_WEIGHTS['Performance Maintenance']
        stab_weighted = stab_score * CATEGORY_WEIGHTS['Physiological Stability']
        marker_weighted = marker_score * CATEGORY_WEIGHTS['Stress Marker Response']

        # Total score
        total_score = perf_weighted + stab_weighted + marker_weighted

        variety_scores[variety] = {
            'Performance Maintenance': perf_weighted,
            'Physiological Stability': stab_weighted,
            'Stress Marker Response': marker_weighted,
            'Total': total_score
        }

        print(f"    Performance: {perf_score:.3f} × {CATEGORY_WEIGHTS['Performance Maintenance']} = {perf_weighted:.3f}")
        print(f"    Physiological: {stab_score:.3f} × {CATEGORY_WEIGHTS['Physiological Stability']} = {stab_weighted:.3f}")
        print(f"    Stress Marker: {marker_score:.3f} × {CATEGORY_WEIGHTS['Stress Marker Response']} = {marker_weighted:.3f}")
        print(f"    TOTALE: {total_score:.3f}")

    return variety_scores


def plot_final_ranking(ax, variety_scores):
    """
    Panel a) Final Stress Tolerance Ranking
    SORTED by descending score (best at top)
    """
    # Sort by descending score
    sorted_varieties = sorted(VARIETIES, key=lambda v: variety_scores[v]['Total'], reverse=True)
    scores = [variety_scores[v]['Total'] for v in sorted_varieties]
    colors = [VARIETY_COLORS[v] for v in sorted_varieties]

    # Plot horizontal bars
    bars = ax.barh(sorted_varieties, scores, color=colors, alpha=0.85,
                   edgecolor='black', linewidth=1.2)

    # Add values at end of bars - MUCH LARGER FONT
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f'{score:.3f}', va='center', fontweight='bold', fontsize=16)

    # Formatting - MUCH LARGER FONTS
    ax.set_xlabel('Score', fontsize=18, fontweight='bold')
    ax.set_xlim(0, max(scores) * 1.15)
    ax.set_title('a)', fontsize=18, fontweight='bold', loc='left', pad=10)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x')
    ax.set_axisbelow(True)

    # Tick settings - MUCH LARGER FONTS
    ax.tick_params(axis='y', labelsize=16)
    ax.tick_params(axis='x', labelsize=15)


def plot_category_contribution(ax, variety_scores):
    """
    Panel b) Category Contribution
    Stacked horizontal bars with THREE categories
    SORTED by descending score (same as panel a)
    """
    # Sort by descending score
    sorted_varieties = sorted(VARIETIES, key=lambda v: variety_scores[v]['Total'], reverse=True)

    # Three categories
    categories = ['Performance Maintenance', 'Physiological Stability', 'Stress Marker Response']

    # Values matrix
    data_matrix = []
    for variety in sorted_varieties:
        row = [variety_scores[variety][cat] for cat in categories]
        data_matrix.append(row)

    data_matrix = np.array(data_matrix)

    # Plot stacked bars
    left = np.zeros(len(sorted_varieties))

    for i, category in enumerate(categories):
        values = data_matrix[:, i]
        ax.barh(sorted_varieties, values, left=left,
               label=category,
               color=CATEGORY_COLORS[category],
               alpha=0.85,
               edgecolor='white',
               linewidth=0.5)
        left += values

    # Formatting - MUCH LARGER FONTS
    ax.set_xlabel('Score', fontsize=18, fontweight='bold')
    ax.set_xlim(0, max([variety_scores[v]['Total'] for v in VARIETIES]) * 1.15)
    ax.set_title('b)', fontsize=18, fontweight='bold', loc='left', pad=10)

    # Legend: NOT placed here, will be placed below the figure

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x')
    ax.set_axisbelow(True)

    # Tick settings - MUCH LARGER FONTS
    ax.tick_params(axis='y', labelsize=16)
    ax.tick_params(axis='x', labelsize=15)


def main():
    print("=" * 80)
    print("FIGURE 6: VARIETY RANKING AND CATEGORY CONTRIBUTION")
    print("=" * 80)

    # Load data
    print("\n📊 Loading dataset...")
    df = load_data()

    # Calculate ranking from REAL dataset
    variety_scores = calculate_variety_ranking(df)

    # Create figure with space for legend below
    print("\n🎨 Creating 2-panel figure...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    # Plot a) Final ranking
    print("\n  Plotting panel a: Final Ranking")
    plot_final_ranking(ax1, variety_scores)

    # Plot b) Category contribution
    print("  Plotting panel b: Category Contribution")
    plot_category_contribution(ax2, variety_scores)

    # Adjust layout with space for legend below
    plt.tight_layout(rect=[0, 0.08, 1, 1])

    # HORIZONTAL legend BELOW the figure
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CATEGORY_COLORS['Performance Maintenance'], label='Performance Maintenance'),
        Patch(facecolor=CATEGORY_COLORS['Physiological Stability'], label='Physiological Stability'),
        Patch(facecolor=CATEGORY_COLORS['Stress Marker Response'], label='Stress Marker Response')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3,
              fontsize=16, frameon=True, framealpha=0.9,
              bbox_to_anchor=(0.5, 0.01))

    # Save
    output_dir = Path(__file__).parent

    png_path = output_dir / 'figure_06_variety_ranking.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ PNG: {png_path}")

    pdf_path = output_dir / 'figure_06_variety_ranking.pdf'
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF: {pdf_path}")

    plt.close()

    print("\n" + "=" * 80)
    print("✅ FIGURE 6 COMPLETED!")
    print("=" * 80)


if __name__ == '__main__':
    main()
