#!/usr/bin/env python3
"""
Figure 7: Parameter Responsiveness Heatmap by Category

Two-panel figure showing parameter responsiveness ranking:
a) WR10 - Best performing wild accession
b) CV - Cultivated variety

The heatmap shows NORMALIZED scores (0-100) for each metric:
- Row 1: F-statistic score (normalized from ANOVA F-statistic)
- Row 2: Effect size (η²) score (normalized from eta-squared)
- Row 3: % Change C→S2 score (normalized absolute percentage change)

All scores are pre-computed in parameter_ranking_unified.csv and are on scale 0-100.
Higher values (red) indicate greater responsiveness to stress.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add scripts directory to path to import parameter_mapping
sys.path.append(str(Path(__file__).parent.parent))
from parameter_mapping import PARAMETER_CATEGORIES

# Configuration
plt.rcParams['font.family'] = 'DejaVu Sans'

# Category colors (SAME as Figure 6)
CATEGORY_COLORS = {
    'Performance Maintenance': '#4ECDC4',      # turquoise
    'Physiological Stability': '#F38181',      # pink/coral
    'Stress Marker Response': '#FFA07A'        # light orange
}

# Parameter order by category
PARAMETER_ORDER = [
    # Performance Maintenance
    'Main shoot height (cm)',
    'Leaves surface (cm²)',
    'Total dry weight (g)',
    'Fruit set (trusses number)',
    # Physiological Stability
    'Stomatal conductance (μmol/sec)',
    'Relative water content (%)',
    'Total chlorophyll (μg/g FW)',
    'Fv/Fm',
    # Stress Marker Response
    'Electrolytic leakage (μS/cm)',
    'Na/K ratio leaves',
    'ABA (ng/mg)',
    'Osmolytes (osm/kg)'
]

# Category positions
CATEGORY_POSITIONS = {
    'Performance Maintenance': (0, 4),
    'Physiological Stability': (4, 8),
    'Stress Marker Response': (8, 12)
}


def load_ranking_data():
    """Load ranking data (unified source)"""
    ranking_file = Path(__file__).parent.parent.parent / 'data' / 'parameter_ranking_unified.csv'

    if not ranking_file.exists():
        raise FileNotFoundError(f"Ranking file not found: {ranking_file}")

    df_ranking = pd.read_csv(ranking_file)
    print(f"✓ Ranking loaded: {len(df_ranking)} parameters")

    return df_ranking


def plot_heatmap(ax, df_ranking, variety, panel_label, show_yticklabels=True, show_colorbar=True):
    """
    Plot heatmap for a variety using PRE-NORMALIZED SCORES (0-100).

    Uses f_stat_score, eta_sq_score, pct_change_score from the CSV file.
    These are already normalized to 0-100 scale.
    """
    # Filter by variety
    subset = df_ranking[df_ranking['variety'] == variety].copy()

    # Reorder according to required order
    subset['param_order'] = subset['parameter'].map(
        {p: i for i, p in enumerate(PARAMETER_ORDER)}
    )
    subset = subset.sort_values('param_order')

    # Prepare data for heatmap
    plot_params = []
    for param in PARAMETER_ORDER:
        param_row = subset[subset['parameter'] == param]
        if len(param_row) > 0:
            plot_params.append(param_row.iloc[0])

    if len(plot_params) == 0:
        print(f"⚠️ No parameters found for {variety}")
        return

    plot_df = pd.DataFrame(plot_params)

    # Use PRE-NORMALIZED SCORES (already 0-100 in the CSV)
    f_score = plot_df['f_stat_score'].values
    eta_score = plot_df['eta_sq_score'].values
    pct_score = plot_df['pct_change_score'].values

    # Replace NaN/inf with 0, clip to 0-100
    f_score = np.clip(np.nan_to_num(f_score, nan=0.0, posinf=100.0), 0, 100)
    eta_score = np.clip(np.nan_to_num(eta_score, nan=0.0, posinf=100.0), 0, 100)
    pct_score = np.clip(np.nan_to_num(pct_score, nan=0.0, posinf=100.0), 0, 100)

    # Create score matrix (parameters x metrics)
    scores = np.column_stack([f_score, eta_score, pct_score])

    # Abbreviated parameter names
    param_labels = [p.split('(')[0].strip() for p in PARAMETER_ORDER]

    # Metrics labels - matching original figure format
    metric_labels = [
        'F-statistic\nscore',
        'Effect size\n(η²) score',
        '% Change\nC→S2 score'
    ]

    # Create heatmap with seaborn
    sns.heatmap(
        scores.T,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        vmin=0,
        vmax=100,
        cbar=show_colorbar,
        cbar_kws={'label': 'Normalized Score (0-100)', 'shrink': 0.8} if show_colorbar else {},
        linewidths=0.5,
        linecolor='white',
        ax=ax,
        xticklabels=param_labels,
        yticklabels=metric_labels if show_yticklabels else False,
        annot_kws={'fontsize': 10, 'fontweight': 'bold'}
    )

    # Axis labels
    if show_yticklabels:
        ax.set_ylabel('Metric', fontsize=14, fontweight='bold')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=12, fontweight='bold')
    else:
        ax.set_ylabel('', fontsize=0)

    ax.set_xlabel('', fontsize=0)

    # X tick labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=11, fontweight='bold')

    # Add separator lines between categories
    category_boundaries = [4, 8]
    for boundary in category_boundaries:
        ax.axvline(x=boundary, color='black', linewidth=2.5, linestyle='-')

    # Panel label "a)" or "b)" AT TOP
    ax.text(-0.5, -0.6, f'{panel_label})',
           ha='left', va='bottom', fontsize=18, fontweight='bold',
           transform=ax.transData)

    # Add category labels ABOVE the heatmap
    for cat_name, (start, end) in CATEGORY_POSITIONS.items():
        mid_pos = (start + end) / 2
        # Two-line category names
        if cat_name == 'Performance Maintenance':
            display_name = 'Performance\nMaintenance'
        elif cat_name == 'Physiological Stability':
            display_name = 'Physiological\nStability'
        else:  # Stress Marker Response
            display_name = 'Stress Marker\nResponse'
        ax.text(mid_pos, -0.35, display_name,
               ha='center', va='bottom', fontsize=12, fontweight='bold',
               linespacing=0.9,
               color=CATEGORY_COLORS[cat_name],
               transform=ax.transData,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                        edgecolor=CATEGORY_COLORS[cat_name], linewidth=2))

    # Adjust colorbar if present
    if show_colorbar:
        cbar = ax.collections[0].colorbar
        if cbar is not None:
            cbar.ax.tick_params(labelsize=11)
            cbar.set_label('Normalized Score (0-100)', fontsize=12, fontweight='bold')


def main():
    print("=" * 80)
    print("FIGURE 7: PARAMETER RESPONSIVENESS HEATMAP BY CATEGORY")
    print("=" * 80)

    # Load data
    print("\n📊 Loading ranking data...")
    df_ranking = load_ranking_data()

    # Verify we have the score columns
    required_cols = ['f_stat_score', 'eta_sq_score', 'pct_change_score']
    for col in required_cols:
        if col not in df_ranking.columns:
            raise ValueError(f"Missing required column: {col}")
    print("✓ All normalized score columns present")

    # Show sample values
    print("\n📏 Sample normalized scores (should be 0-100):")
    sample = df_ranking[df_ranking['variety'] == 'WR10'].head(3)
    for _, row in sample.iterrows():
        print(f"   {row['parameter'][:25]:25s}: F={row['f_stat_score']:.1f}, η²={row['eta_sq_score']:.1f}, %Chg={row['pct_change_score']:.1f}")

    # Create figure
    print("\n🎨 Creating 2-panel figure...")
    fig = plt.figure(figsize=(20, 7))

    # GridSpec for balanced panels
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.1], wspace=0.12,
                          top=0.82, bottom=0.22, left=0.08, right=0.95)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # Panel a) WR10 - with Y labels, without colorbar
    print("  Plotting panel a: WR10")
    plot_heatmap(ax1, df_ranking, 'WR10', 'a', show_yticklabels=True, show_colorbar=False)

    # Panel b) CV - without Y labels, with colorbar
    print("  Plotting panel b: CV")
    plot_heatmap(ax2, df_ranking, 'CV', 'b', show_yticklabels=False, show_colorbar=True)

    # Save
    output_dir = Path(__file__).parent

    png_path = output_dir / 'figure_07_parameter_responsiveness.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ PNG: {png_path}")

    pdf_path = output_dir / 'figure_07_parameter_responsiveness.pdf'
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF: {pdf_path}")

    plt.close()

    print("\n" + "=" * 80)
    print("✅ FIGURE 7 COMPLETED!")
    print("=" * 80)


if __name__ == '__main__':
    main()
