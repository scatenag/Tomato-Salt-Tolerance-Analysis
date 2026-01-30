#!/usr/bin/env python3
"""
Figure 7: Parameter Responsiveness Heatmap by Category

Two-panel figure showing parameter responsiveness ranking:
a) WR10 - Best performing wild accession
b) CV - Cultivated variety

Score calculation (consistent with Table S2):
  Combined Score = (F_score × 0.4) + (η²_score × 0.4) + (%Change_score × 0.2)

The heatmap shows:
- Row 1: F-statistic contribution (score × 0.4)
- Row 2: Effect size η² contribution (score × 0.4)
- Row 3: % Change contribution (score × 0.2)
- Row 4: Combined Score (sum of above)

Modifications from original:
- Remove ranking numbers above heatmap (#9, #10, etc.)
- Increase all font sizes
- Match category label colors with Figure 6
- Use weighted contributions matching Table S2 formula
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
plt.rcParams['font.family'] = 'Arial'

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
    Plot heatmap for a variety
    show_yticklabels: show Y axis labels (only for panel a)
    show_colorbar: show colorbar (only for panel b)
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

    # Prepare matrix for heatmap - apply weights from Table S2 formula
    # Combined Score = (F_score × 0.4) + (η²_score × 0.4) + (%Change_score × 0.2)
    f_contrib = plot_df['f_stat_score'].values * 0.4
    eta_contrib = plot_df['eta_sq_score'].values * 0.4
    pct_contrib = plot_df['pct_change_score'].values * 0.2
    combined = f_contrib + eta_contrib + pct_contrib

    scores = np.column_stack([f_contrib, eta_contrib, pct_contrib, combined])

    # Replace NaN with 0
    scores = np.nan_to_num(scores, nan=0.0)

    # Abbreviated parameter names
    param_labels = [p.split('(')[0].strip() for p in PARAMETER_ORDER]

    # Metrics labels - weighted contributions (MUCH LARGER FONT)
    metric_labels = ['F-statistic\n(×0.4)', 'Effect size η²\n(×0.4)', '% Change\n(×0.2)', 'Combined\nScore']

    # Dynamic vmax based on data (Combined Score can be >> 100)
    vmax_val = max(50, np.nanmax(scores))  # At least 50, or data max

    # Create heatmap - LARGER FONTS
    sns.heatmap(
        scores.T,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        vmin=0,
        vmax=vmax_val,
        cbar_kws={'label': 'Weighted Score', 'shrink': 0.6},
        linewidths=0.5,
        linecolor='white',
        ax=ax,
        xticklabels=param_labels,
        yticklabels=metric_labels if show_yticklabels else False,
        cbar=show_colorbar,
        annot_kws={'fontsize': 12, 'fontweight': 'bold'}  # Slightly smaller for 4 rows
    )

    # Axis labels (LARGER FONT) - only for panel a
    if show_yticklabels:
        ax.set_ylabel('Metric', fontsize=16, fontweight='bold')
    else:
        ax.set_ylabel('', fontsize=0)
    ax.set_xlabel('', fontsize=0)  # Remove xlabel

    # Tick labels (LARGER FONT)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=14, fontweight='bold')
    if show_yticklabels:
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=16, fontweight='bold')

    # REMOVED: ranking numbers above parameters (as requested)

    # Add separator lines between categories
    category_boundaries = [4, 8]
    for boundary in category_boundaries:
        ax.axvline(x=boundary, color='black', linewidth=3, linestyle='-')

    # Panel label "a)" or "b)" AT TOP (above categories)
    y_panel_pos = -0.45  # Closer position
    ax.text(-0.5, y_panel_pos, f'{panel_label})',
           ha='left', va='bottom', fontsize=20, fontweight='bold')

    # Add category labels BELOW "a)" and "b)" but above the heatmap
    # FULL NAMES ON TWO LINES - MUCH LARGER FONTS
    y_category_pos = -0.25  # Position for two-line text
    for cat_name, (start, end) in CATEGORY_POSITIONS.items():
        mid_pos = (start + end) / 2
        # Full name on two lines
        if cat_name == 'Performance Maintenance':
            display_name = 'Performance\nMaintenance'
        elif cat_name == 'Physiological Stability':
            display_name = 'Physiological\nStability'
        else:  # Stress Marker Response
            display_name = 'Stress Marker\nResponse'
        ax.text(mid_pos, y_category_pos, display_name,
               ha='center', va='bottom', fontsize=16, fontweight='bold',
               linespacing=0.85,
               color=CATEGORY_COLORS[cat_name],
               bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                        edgecolor=CATEGORY_COLORS[cat_name], linewidth=2.5))


def main():
    print("=" * 80)
    print("FIGURE 7: PARAMETER RESPONSIVENESS HEATMAP BY CATEGORY")
    print("=" * 80)

    # Load data
    print("\n📊 Loading ranking data...")
    df_ranking = load_ranking_data()

    # Create figure with GridSpec to balance widths
    # Panel a) has Y labels but NO colorbar
    # Panel b) has colorbar but NO Y labels
    # So they should have the same final width
    # Now with 4 rows (3 weighted contributions + Combined Score)
    print("\n🎨 Creating 2-panel figure...")
    fig = plt.figure(figsize=(24, 10))  # Taller for 4 rows

    # GridSpec: panel a narrower (no colorbar), panel b wider (with colorbar)
    # Y labels of a) ~= colorbar space of b)
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.08], wspace=0.15,
                          top=0.85, bottom=0.22, left=0.06, right=0.95)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # Panel a) WR10 - with Y labels, without colorbar
    print("  Plotting panel a: WR10")
    plot_heatmap(ax1, df_ranking, 'WR10', 'a', show_yticklabels=True, show_colorbar=False)

    # Panel b) CV - without Y labels, with colorbar
    print("  Plotting panel b: CV")
    plot_heatmap(ax2, df_ranking, 'CV', 'b', show_yticklabels=False, show_colorbar=True)

    # Increase colorbar label font - EVEN LARGER
    cbar = ax2.collections[0].colorbar
    if cbar is not None:
        cbar.ax.tick_params(labelsize=16)  # Increased from 14
        cbar.set_label('Weighted Score', fontsize=18, fontweight='bold')  # Updated label

    # DO NOT use tight_layout because it overrides GridSpec

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
