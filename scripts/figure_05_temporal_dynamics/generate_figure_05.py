#!/usr/bin/env python3
"""
Figure 5: Temporal Dynamics of Phenological Development

12-panel figure showing temporal progression of:
- Main shoot height (a, b, c)
- Flowering trusses (d, e, f)
- Fruit set trusses (g, h, i)
- Fruit ripening trusses (l, m, n)

Each metric shown across Control (C), Moderate stress (S1), and Severe stress (S2)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

# Configuration - MUCH LARGER FONTS
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 18  # Base font size increased

# Varieties and treatments
VARIETIES = ['CV', 'WR2', 'WR9', 'WR10', 'WR11', 'WR14']
TREATMENTS = ['C', 'S1', 'S2']

# Accession colors (as requested, same as Figure 6)
VARIETY_COLORS = {
    'CV': '#000000',      # black
    'WR2': '#FF0000',     # red
    'WR9': '#00BFFF',     # light blue (deep sky blue)
    'WR10': '#00FF00',    # green
    'WR11': '#DAA520',    # dark yellow (goldenrod) - more visible on white
    'WR14': '#9370DB'     # purple (medium purple)
}

# Mapping dataset columns → display names
METRIC_MAPPING = {
    'Main shoot height (cm)': {
        'column': 'Main shoot height (cm)',
        'display': 'Main shoot height (cm)',
        'ylabel': 'Main shoot height\n(cm)'
    },
    'Flowering (trusses number)': {
        'column': 'Flowering (trusses number)',
        'display': 'Flowering',
        'ylabel': 'Flowering\n(trusses number)'
    },
    'Fruit set (trusses number)': {
        'column': 'Fruit set (trusses number)',
        'display': 'Fruit set',
        'ylabel': 'Fruit set\n(trusses number)'
    },
    'Trusses maturing (number)': {
        'column': 'Trusses maturing (number)',
        'display': 'Fruit ripening',
        'ylabel': 'Fruit ripening\n(trusses number)'
    }
}

TREATMENT_TITLES = {
    'C': 'Control (C)',
    'S1': 'Moderate stress (S1)',
    'S2': 'Severe stress (S2)'
}


def load_data():
    """Load data from master dataset (calculates means internally)"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not data_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {data_path}")

    df_raw = pd.read_csv(data_path)

    # Calculate means for line plotting
    # Filter columns of interest for Figure 5
    pheno_cols = [
        'Main shoot height (cm)',
        'Flowering (trusses number)',
        'Fruit set (trusses number)',
        'Trusses maturing (number)'
    ]

    df_means = df_raw.groupby(['DAT', 'Variety', 'Treatment'])[pheno_cols].mean().reset_index()
    print(f"✓ Means calculated from master dataset: {len(df_means)} rows")

    return df_means


def load_raw_replicates():
    """Load raw replicate data from master dataset for t-test statistics"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not data_path.exists():
        print(f"⚠ Master dataset not found: {data_path}")
        return None

    df = pd.read_csv(data_path)
    print(f"✓ Replicates loaded from master dataset: {len(df)} rows")

    return df


WR_VARIETIES = ['WR2', 'WR9', 'WR10', 'WR11', 'WR14']


def calculate_ttest_vs_cv(df_raw, metric_col, treatment, dat_value, variety):
    """
    Calculate t-test between a WR variety and CV for a given timepoint
    Returns p-value (Bonferroni corrected) and significance symbol
    """
    if df_raw is None:
        return None, ''

    subset = df_raw[(df_raw['Treatment'] == treatment) & (df_raw['DAT'] == dat_value)].copy()

    cv_data = subset[subset['Variety'] == 'CV'][metric_col].dropna()
    wr_data = subset[subset['Variety'] == variety][metric_col].dropna()

    if len(cv_data) < 2 or len(wr_data) < 2:
        return None, ''

    try:
        # Welch's t-test (does not assume equal variances)
        t_stat, p_value = stats.ttest_ind(cv_data, wr_data, equal_var=False)

        # Bonferroni correction for 5 comparisons (WR2, WR9, WR10, WR11, WR14 vs CV)
        p_corrected = min(p_value * 5, 1.0)

        # Determine significance with corrected p-value
        if p_corrected < 0.001:
            sig = '***'
        elif p_corrected < 0.01:
            sig = '**'
        elif p_corrected < 0.05:
            sig = '*'
        else:
            sig = ''

        return p_corrected, sig
    except:
        return None, ''


def get_significant_varieties_at_dat(df_raw, metric_col, treatment, dat_value):
    """
    Return a dictionary variety -> significance for a given DAT
    Only WR varieties significantly different from CV
    """
    significant = {}
    for variety in WR_VARIETIES:
        p_val, sig = calculate_ttest_vs_cv(df_raw, metric_col, treatment, dat_value, variety)
        if sig:
            significant[variety] = sig
    return significant


def plot_timeseries(ax, df, df_raw, metric_key, treatment, panel_label, is_top_row=False, is_first_col=True, is_bottom_row=False, show_legend=True, y_limits=None, global_max_dat=100):
    """
    Plot a single timeseries for a metric and treatment
    df: main dataset with means
    df_raw: dataset with raw replicates for statistics and plotting
    is_bottom_row: True only for last row (shows X axis label)
    show_legend: True only for panels a, b, c (first row)
    y_limits: tuple (y_min, y_max) to standardize Y scale per row
    global_max_dat: global maximum DAT to use for all panels
    """
    metric_info = METRIC_MAPPING[metric_key]
    metric_col = metric_info['column']

    # USE df_raw for plotting (has all data including zeros)
    df_plot = df_raw if df_raw is not None else df
    df_treatment = df_plot[df_plot['Treatment'] == treatment].copy()

    # DAT values from df_raw (has all DATs including those with zero values)
    dat_values = sorted(df_treatment['DAT'].dropna().unique())

    # EXCLUDE DAT 98 for Fruit set and Fruit ripening (values return to 0 after destructive measurements)
    # Main shoot height and Flowering have valid data at DAT 98
    if metric_key in ['Trusses maturing (number)', 'Fruit set (trusses number)']:
        dat_values = [d for d in dat_values if d != 98]

    # FIRST: Calculate which varieties are significantly different from CV for each DAT
    # Dictionary: DAT -> {variety -> significance}
    significant_varieties_per_dat = {}
    for dat in dat_values:
        sig_vars = get_significant_varieties_at_dat(df_raw, metric_col, treatment, dat)
        if sig_vars:
            significant_varieties_per_dat[dat] = sig_vars

    # Plot for each variety
    for variety in VARIETIES:
        df_var = df_treatment[df_treatment['Variety'] == variety]

        # Calculate mean and SE for each DAT
        means = []
        sems = []
        dats = []

        for dat in dat_values:
            dat_data = df_var[df_var['DAT'] == dat][metric_col].dropna()
            if len(dat_data) > 0:
                means.append(dat_data.mean())
                sems.append(dat_data.sem() if len(dat_data) > 1 else 0)
                dats.append(dat)

        if len(means) > 0:
            means = np.array(means)
            sems = np.array(sems)
            dats = np.array(dats)

            # Plot line - INCREASED THICKNESS
            color = VARIETY_COLORS[variety]
            linewidth = 3.5 if variety == 'CV' else 2.5  # Thicker lines

            ax.plot(dats, means,
                   color=color,
                   linewidth=linewidth,
                   marker='o',
                   markersize=7 if variety == 'CV' else 5,
                   label=variety,
                   linestyle='-' if variety == 'CV' else '--',
                   alpha=0.9,
                   zorder=10,
                   markeredgewidth=0)  # No border

            # Error bars (SE)
            ax.fill_between(dats, means - sems, means + sems,
                           color=color, alpha=0.15, zorder=5)

    # ADD ASTERISKS below the X axis (as in original figures)
    # Asterisks are added AFTER setting the axis limits

    # Formatting - X LABEL ONLY FOR LAST ROW
    if is_bottom_row:
        ax.set_xlabel('DAT', fontsize=20, fontweight='bold')
    else:
        ax.set_xlabel('')
        ax.tick_params(axis='x', labelbottom=False)  # Hide tick labels

    # Y-label only for first column - LARGER FONT
    if is_first_col:
        ax.set_ylabel(metric_info['ylabel'], fontsize=18, fontweight='bold')
    else:
        ax.set_ylabel('')  # Remove label for columns 2 and 3

    # Panel title (only label, NOT the treatment) - LARGER FONT
    ax.set_title(f"{panel_label})", fontsize=20, fontweight='bold', loc='left', pad=10)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, zorder=0)

    # X limits - use GLOBAL maximum DAT for all panels
    ax.set_xlim(0, global_max_dat + 5)  # Small margin beyond maximum DAT

    # MUCH larger tick labels
    ax.tick_params(axis='both', labelsize=16)

    # Hide Y tick labels for columns 2 and 3 (not first column)
    if not is_first_col:
        ax.tick_params(axis='y', labelleft=False)

    # Apply uniform Y limits if specified
    if y_limits is not None:
        ax.set_ylim(y_limits[0], y_limits[1])
    else:
        # IMPORTANT: For CV in fruit ripening (which is at 0), force a visible minimum
        y_min, y_max = ax.get_ylim()
        if y_max < 0.5:
            ax.set_ylim(-0.1, 2.0)

    # Column title (only for first row) - MUCH LARGER FONT
    if is_top_row:
        ax.text(0.5, 1.35, TREATMENT_TITLES[treatment],
               transform=ax.transAxes,
               ha='center', va='bottom',
               fontsize=22, fontweight='bold')

    # Legend only for first row (panels a, b, c) - EVEN LARGER FONT
    if show_legend and treatment == 'C':
        ax.legend(loc='upper left', fontsize=18, frameon=True,
                 framealpha=0.9, ncol=2)

    # ADD SIGNIFICANCE ASTERISKS ABOVE THE PLOTS
    # Colored asterisks for varieties positioned above data
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min

    # Base position above axis (in data coordinates)
    # Each variety has a dedicated row
    variety_row_offset = {
        'WR2': 0,    # First row (closest to data)
        'WR9': 1,    # Second row
        'WR10': 2,   # Third row
        'WR11': 3,   # Fourth row
        'WR14': 4    # Fifth row (highest)
    }

    # Spacing between asterisk rows (proportional to Y range)
    row_spacing = y_range * 0.04
    base_y = y_max + y_range * 0.02  # Base position above data

    for dat, sig_varieties in significant_varieties_per_dat.items():
        # For each significant variety at this DAT
        for variety, sig in sig_varieties.items():
            # Asterisk color = variety color
            variety_color = VARIETY_COLORS[variety]

            # Y position: dedicated row for this variety
            row_idx = variety_row_offset[variety]
            y_asterisk = base_y + (row_idx * row_spacing)

            # Asterisk text size based on significance level - LARGER
            if sig == '***':
                fontsize = 18
            elif sig == '**':
                fontsize = 16
            else:
                fontsize = 14

            # Draw asterisk as colored text above data
            ax.text(dat, y_asterisk, sig,
                   ha='center', va='bottom',
                   fontsize=fontsize, fontweight='bold',
                   color=variety_color,
                   clip_on=False,  # Allows drawing outside axis limits
                   zorder=100)


def main():
    print("=" * 80)
    print("FIGURE 5: TEMPORAL DYNAMICS OF PHENOLOGICAL DEVELOPMENT")
    print("=" * 80)

    # Load data
    print("\n📊 Loading dataset...")
    df = load_data()
    df_raw = load_raw_replicates()

    # Create 12-panel figure (4 rows × 3 columns) - INCREASED DIMENSIONS
    print("\n🎨 Creating 12-panel figure...")
    fig = plt.figure(figsize=(20, 18))

    # Metrics to plot (in specified order)
    metrics = [
        'Main shoot height (cm)',
        'Flowering (trusses number)',
        'Fruit set (trusses number)',
        'Trusses maturing (number)'
    ]

    # Panel labels: a-c, d-f, g-i, l-n
    panel_labels = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f'],
        ['g', 'h', 'i'],
        ['l', 'm', 'n']
    ]

    # FIRST: Calculate GLOBAL maximum DAT from all data
    # Use df_raw which has all DATs
    print("\n📏 Calculating global maximum DAT...")
    global_max_dat = int(df_raw['DAT'].max()) if df_raw is not None else int(df['DAT'].max())
    print(f"    Global maximum DAT: {global_max_dat}")

    # Calculate Y limits for each metric (row) to standardize scales
    # Use df_raw to have all data
    print("\n📏 Calculating uniform Y limits for each row...")
    y_limits_per_metric = {}
    df_for_limits = df_raw if df_raw is not None else df
    for metric in metrics:
        metric_info = METRIC_MAPPING[metric]
        metric_col = metric_info['column']
        # Find global min and max for this metric (all treatments)
        metric_data = df_for_limits[metric_col].dropna()
        if len(metric_data) > 0:
            y_min = max(0, metric_data.min() - metric_data.std() * 0.1)  # Slightly below minimum
            y_max = metric_data.max() + metric_data.std() * 0.35  # More space above for asterisks
            y_limits_per_metric[metric] = (y_min, y_max)
            print(f"    {metric_info['display']}: Y = [{y_min:.1f}, {y_max:.1f}]")
        else:
            y_limits_per_metric[metric] = None

    # Create subplot for each combination
    for row_idx, metric in enumerate(metrics):
        y_limits = y_limits_per_metric.get(metric, None)

        for col_idx, treatment in enumerate(TREATMENTS):
            ax = plt.subplot(4, 3, row_idx * 3 + col_idx + 1)

            panel_label = panel_labels[row_idx][col_idx]
            is_top_row = (row_idx == 0)  # Only first row shows column titles
            is_first_col = (col_idx == 0)  # Only first column shows Y-label
            is_bottom_row = (row_idx == 3)  # Only last row shows X labels
            # Legend only for panel l) (last row, first column)
            show_legend = (row_idx == 3 and col_idx == 0)

            print(f"  Plotting panel {panel_label}: {metric} - {treatment}")
            plot_timeseries(ax, df, df_raw, metric, treatment, panel_label, is_top_row, is_first_col, is_bottom_row, show_legend, y_limits, global_max_dat)

    # Adjust layout with space at top for titles and bottom for asterisks
    plt.tight_layout(rect=[0, 0.02, 1, 0.92])
    # Add extra space between subplots for asterisks below X axis
    plt.subplots_adjust(hspace=0.35)

    # Save
    output_dir = Path(__file__).parent

    png_path = output_dir / 'figure_05_temporal_dynamics.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ PNG: {png_path}")

    pdf_path = output_dir / 'figure_05_temporal_dynamics.pdf'
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF: {pdf_path}")

    plt.close()

    print("\n" + "=" * 80)
    print("✅ FIGURE 5 COMPLETED!")
    print("=" * 80)


if __name__ == '__main__':
    main()
