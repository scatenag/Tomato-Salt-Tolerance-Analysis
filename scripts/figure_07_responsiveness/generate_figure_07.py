#!/usr/bin/env python3
"""
Figure 7: Parameter Responsiveness Heatmap by Category

Two-panel figure showing parameter responsiveness ranking:
a) WR10 - Best performing wild accession
b) CV - Cultivated variety

The heatmap shows raw (unweighted) statistical metrics with ROW-WISE normalization:
- Row 1: F-statistic (from one-way ANOVA) - scale 0-1000
- Row 2: Effect size η² (proportion of variance explained) - scale 0-100%
- Row 3: % Change (Control → S2) - scale varies by actual data

Each row uses its own color scale to ensure all metrics are visually comparable.
Values displayed are raw (unscaled), but colors reflect position within each metric.

Note: Combined Score is not shown (already in Table S2)

Modifications from original:
- Remove ranking numbers above heatmap (#9, #10, etc.)
- Increase all font sizes
- Match category label colors with Figure 6
- Show raw parameter values without coefficient weighting
- ROW-WISE NORMALIZATION: Each metric row has its own color scale
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


def compute_row_ranges(df_ranking, varieties=['WR10', 'CV']):
    """
    Compute min/max for each metric row across all varieties.
    This allows row-wise normalization so each metric uses its own color scale.

    Returns dict with 'f_stat', 'eta_sq', 'pct_change' keys, each containing (min, max).
    """
    f_values = []
    eta_values = []
    pct_values = []

    for variety in varieties:
        subset = df_ranking[df_ranking['variety'] == variety].copy()
        for param in PARAMETER_ORDER:
            param_row = subset[subset['parameter'] == param]
            if len(param_row) > 0:
                row = param_row.iloc[0]
                f_values.append(np.clip(row['f_statistic'], 0, 1000))
                eta_values.append(row['eta_squared'] * 100)
                pct_values.append(np.abs(row['pct_change_C_to_S2']))

    f_values = np.nan_to_num(f_values, nan=0.0)
    eta_values = np.nan_to_num(eta_values, nan=0.0)
    pct_values = np.nan_to_num(pct_values, nan=0.0)

    return {
        'f_stat': (0, max(1, np.max(f_values))),
        'eta_sq': (0, max(1, np.max(eta_values))),
        'pct_change': (0, max(1, np.max(pct_values)))
    }


def plot_heatmap(ax, df_ranking, variety, panel_label, show_yticklabels=True, show_colorbar=True, row_ranges=None):
    """
    Plot heatmap for a variety with ROW-WISE NORMALIZATION.

    Each metric row (F-stat, η², % Change) is normalized to its own 0-1 scale
    for coloring, but displays raw values as annotations.

    show_yticklabels: show Y axis labels (only for panel a)
    show_colorbar: show colorbar (only for panel b)
    row_ranges: dict with min/max for each metric (for consistent normalization across panels)
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

    # Prepare raw values for annotations
    f_raw = plot_df['f_statistic'].values
    f_raw = np.clip(f_raw, 0, 1000)  # Cap infinite values
    eta_raw = plot_df['eta_squared'].values * 100  # η² as percentage
    pct_raw = np.abs(plot_df['pct_change_C_to_S2'].values)  # Absolute % change

    # Replace NaN with 0
    f_raw = np.nan_to_num(f_raw, nan=0.0)
    eta_raw = np.nan_to_num(eta_raw, nan=0.0)
    pct_raw = np.nan_to_num(pct_raw, nan=0.0)

    # Store raw values for annotations
    raw_values = np.column_stack([f_raw, eta_raw, pct_raw])

    # ROW-WISE NORMALIZATION: normalize each metric to 0-1 scale for coloring
    if row_ranges:
        f_min, f_max = row_ranges['f_stat']
        eta_min, eta_max = row_ranges['eta_sq']
        pct_min, pct_max = row_ranges['pct_change']
    else:
        f_min, f_max = 0, max(1, np.max(f_raw))
        eta_min, eta_max = 0, max(1, np.max(eta_raw))
        pct_min, pct_max = 0, max(1, np.max(pct_raw))

    # Normalize to 0-1 for coloring
    f_norm = (f_raw - f_min) / (f_max - f_min) if f_max > f_min else np.zeros_like(f_raw)
    eta_norm = (eta_raw - eta_min) / (eta_max - eta_min) if eta_max > eta_min else np.zeros_like(eta_raw)
    pct_norm = (pct_raw - pct_min) / (pct_max - pct_min) if pct_max > pct_min else np.zeros_like(pct_raw)

    normalized_scores = np.column_stack([f_norm, eta_norm, pct_norm])

    # Abbreviated parameter names
    param_labels = [p.split('(')[0].strip() for p in PARAMETER_ORDER]

    # Metrics labels with actual ranges shown
    metric_labels = [
        f'F-statistic\n(0-{f_max:.0f})',
        f'Effect size η²\n(0-{eta_max:.0f}%)',
        f'% Change\n(0-{pct_max:.0f}%)'
    ]

    # Create heatmap with normalized values (0-1 scale for all rows)
    # But we'll add custom annotations with raw values
    im = ax.imshow(normalized_scores.T, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)

    # Add gridlines
    ax.set_xticks(np.arange(normalized_scores.shape[0]+1)-.5, minor=True)
    ax.set_yticks(np.arange(normalized_scores.shape[1]+1)-.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Add raw value annotations
    for i in range(raw_values.shape[0]):  # columns (parameters)
        for j in range(raw_values.shape[1]):  # rows (metrics)
            raw_val = raw_values[i, j]
            norm_val = normalized_scores[i, j]
            # Choose text color based on background intensity
            text_color = 'white' if norm_val > 0.6 else 'black'
            # Format: show integer if >= 100, one decimal otherwise
            if raw_val >= 100:
                text = f'{raw_val:.0f}'
            else:
                text = f'{raw_val:.1f}'
            ax.text(i, j, text, ha='center', va='center',
                   fontsize=11, fontweight='bold', color=text_color)

    # Set tick labels
    ax.set_xticks(np.arange(len(param_labels)))
    ax.set_xticklabels(param_labels, rotation=45, ha='right', fontsize=14, fontweight='bold')

    if show_yticklabels:
        ax.set_yticks(np.arange(len(metric_labels)))
        ax.set_yticklabels(metric_labels, rotation=0, fontsize=14, fontweight='bold')
        ax.set_ylabel('Metric', fontsize=16, fontweight='bold')
    else:
        ax.set_yticks([])
        ax.set_ylabel('', fontsize=0)

    ax.set_xlabel('', fontsize=0)

    # Add colorbar if requested
    if show_colorbar:
        cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
        cbar.set_label('Relative intensity\n(row-normalized)', fontsize=14, fontweight='bold')
        cbar.ax.tick_params(labelsize=12)
        cbar.set_ticks([0, 0.5, 1])
        cbar.set_ticklabels(['Low', 'Medium', 'High'])

    # Add separator lines between categories
    category_boundaries = [3.5, 7.5]  # Between param indices (0-based)
    for boundary in category_boundaries:
        ax.axvline(x=boundary, color='black', linewidth=3, linestyle='-')

    # Panel label "a)" or "b)" AT TOP (above categories)
    y_panel_pos = -0.55  # Position above heatmap
    ax.text(-0.5, y_panel_pos, f'{panel_label})',
           ha='left', va='bottom', fontsize=20, fontweight='bold',
           transform=ax.get_yaxis_transform())

    # Add category labels ABOVE the heatmap
    y_category_pos = -0.35  # Position for category labels
    for cat_name, (start, end) in CATEGORY_POSITIONS.items():
        mid_pos = (start + end) / 2 - 0.5  # Adjust for 0-based indexing
        # Full name on two lines
        if cat_name == 'Performance Maintenance':
            display_name = 'Performance\nMaintenance'
        elif cat_name == 'Physiological Stability':
            display_name = 'Physiological\nStability'
        else:  # Stress Marker Response
            display_name = 'Stress Marker\nResponse'
        ax.text(mid_pos, y_category_pos, display_name,
               ha='center', va='bottom', fontsize=14, fontweight='bold',
               linespacing=0.85,
               color=CATEGORY_COLORS[cat_name],
               transform=ax.get_xaxis_transform(),
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                        edgecolor=CATEGORY_COLORS[cat_name], linewidth=2.5))


def main():
    print("=" * 80)
    print("FIGURE 7: PARAMETER RESPONSIVENESS HEATMAP BY CATEGORY")
    print("=" * 80)

    # Load data
    print("\n📊 Loading ranking data...")
    df_ranking = load_ranking_data()

    # Compute row ranges for consistent normalization across both panels
    print("\n📏 Computing row ranges for row-wise normalization...")
    row_ranges = compute_row_ranges(df_ranking, varieties=['WR10', 'CV'])
    print(f"   F-statistic range: 0 - {row_ranges['f_stat'][1]:.1f}")
    print(f"   η² range: 0 - {row_ranges['eta_sq'][1]:.1f}%")
    print(f"   % Change range: 0 - {row_ranges['pct_change'][1]:.1f}%")

    # Create figure with GridSpec to balance widths
    # Panel a) has Y labels but NO colorbar
    # Panel b) has colorbar but NO Y labels
    print("\n🎨 Creating 2-panel figure with row-normalized heatmaps...")
    fig = plt.figure(figsize=(24, 8))  # Slightly shorter for 3 rows

    # GridSpec: panel a narrower (no colorbar), panel b wider (with colorbar)
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.12], wspace=0.08,
                          top=0.82, bottom=0.25, left=0.08, right=0.92)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # Panel a) WR10 - with Y labels, without colorbar
    print("  Plotting panel a: WR10")
    plot_heatmap(ax1, df_ranking, 'WR10', 'a', show_yticklabels=True, show_colorbar=False, row_ranges=row_ranges)

    # Panel b) CV - without Y labels, with colorbar
    print("  Plotting panel b: CV")
    plot_heatmap(ax2, df_ranking, 'CV', 'b', show_yticklabels=False, show_colorbar=True, row_ranges=row_ranges)

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
