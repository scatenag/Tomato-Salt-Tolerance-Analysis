#!/usr/bin/env python3
"""
Figure 4: Phenological Phase Temporal Analysis

a) Heatmap with cumulative GDD per phenological phase
b) Scatter plot phenological delays (Y axis = positional index, X axis = delay %)

Based on: variety_ranking_analyzer.py (create_phenological_timing_plots)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Configuration - LARGER FONTS
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

# Varieties and treatments (updated names)
VARIETIES = ['CV', 'WR2', 'WR9', 'WR10', 'WR11', 'WR14']
TREATMENTS = ['C', 'S1', 'S2']

# Phenological phases (as in original code)
PHASE_ORDER = ['vegetative', 'bloom', 'bloom fruit set', 'maturazione']
PHASES_DISPLAY = ['Vegetative', 'Flowering', 'Fruit set', 'Fruit ripening']

# Colors
PHASE_COLORS = {
    'vegetative': '#2E8B57',
    'bloom': '#FFD700',
    'bloom fruit set': '#FF8C00',
    'maturazione': '#DC143C'
}

TREATMENT_COLORS = {
    'C': '#1f77b4',
    'S1': '#ff7f0e',
    'S2': '#d62728'
}


def load_and_prepare_data():
    """Load and prepare phenological data from master dataset"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not data_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    print(f"✓ Master dataset loaded: {len(df)} rows")

    # Extract phenological phases and GDD
    # Phenological phases (vegetative, bloom, etc.) are already in the 'Phenological phase' column
    target_phases = ['vegetative', 'bloom', 'bloom fruit set', 'maturazione']

    timing_data = {}

    for variety in VARIETIES:
        timing_data[variety] = {}
        for treatment in TREATMENTS:
            timing_data[variety][treatment] = {}
            for phase in target_phases:
                # Select subset for this combination (Variety, Treatment, Phase)
                # NOTE: we use 'GDD cumulative' which is unique per DAT/Variety/Treatment in master
                subset = df[
                    (df['Variety'] == variety) &
                    (df['Treatment'] == treatment) &
                    (df['Phenological phase'] == phase)
                ]

                if not subset.empty:
                    # In this script (Figure 4), we are interested in the mean GDD per phase and its deviation
                    # Since GDD cumulative is associated with DAT, and each DAT has multiple Reply (replicates) in master
                    # we take the mean of GDD (which should be equal for the same DAT)
                    gdd_mean = subset['GDD cumulative'].mean()

                    # Calculate the standard deviation of GDD for this phase?
                    # In the original dataset it was calculated on the temporal variability of the phase
                    # Here we keep it as subset['GDD cumulative'].std() for calculation consistency
                    gdd_std = subset['GDD cumulative'].std()

                    timing_data[variety][treatment][phase] = {
                        'gdd_mean': gdd_mean,
                        'gdd_std': gdd_std if not np.isnan(gdd_std) else 0.0
                    }
                else:
                    timing_data[variety][treatment][phase] = {'gdd_mean': 0, 'gdd_std': 0}

    return timing_data


def calculate_treatment_effects(timing_data):
    """
    Calculate treatment-induced delays compared to control
    (as in the original analyze_phenological_timing method)
    """
    effects = {}

    for variety, variety_data in timing_data.items():
        if 'C' not in variety_data:
            continue

        control_timing = variety_data['C']
        variety_effects = {}

        for treatment in ['S1', 'S2']:
            if treatment not in variety_data:
                continue

            treatment_timing = variety_data[treatment]
            phase_effects = {}

            for phase in PHASE_ORDER:
                if phase in control_timing and phase in treatment_timing:
                    control_gdd = control_timing[phase]['gdd_mean']
                    treatment_gdd = treatment_timing[phase]['gdd_mean']

                    delay_gdd = treatment_gdd - control_gdd
                    delay_percent = (delay_gdd / control_gdd) * 100 if control_gdd != 0 else 0

                    phase_effects[phase] = {
                        'gdd_delay': delay_gdd,
                        'percent_delay': delay_percent,
                        'control_gdd': control_gdd,
                        'treatment_gdd': treatment_gdd
                    }

            variety_effects[treatment] = phase_effects

        effects[variety] = variety_effects

    return effects


def plot_heatmap(timing_data, ax):
    """
    Plot a) - Cumulative GDD heatmap per phase
    (as in original method, subplot ax4)
    """
    varieties = sorted(timing_data.keys())
    treatments = ['C', 'S1', 'S2']
    phases = PHASE_ORDER

    heatmap_data = []
    row_labels = []

    for variety in varieties:
        variety_data = timing_data[variety]
        for treatment in treatments:
            if treatment in variety_data:
                row_data = []
                for phase in phases:
                    if phase in variety_data[treatment]:
                        gdd = variety_data[treatment][phase]['gdd_mean']
                        row_data.append(gdd if not np.isnan(gdd) else 0)
                    else:
                        row_data.append(0)

                heatmap_data.append(row_data)
                row_labels.append(f"{variety}-{treatment}")

    if heatmap_data:
        heatmap_array = np.array(heatmap_data)
        im = ax.imshow(heatmap_array, cmap='YlOrRd', aspect='auto',
                       vmin=250, vmax=950)

        # Separation lines
        for i in range(len(row_labels)):
            ax.axhline(i + 0.5, color='white', linewidth=0.5)

        # Add numeric values inside cells - LARGER FONT
        for i in range(len(row_labels)):
            for j in range(len(phases)):
                value = heatmap_array[i, j]
                # Text color: dark for light cells, light for dark cells
                text_color = 'black' if value < 600 else 'white'
                ax.text(j, i, f'{int(value)}',
                       ha='center', va='center',
                       color=text_color, fontsize=10, fontweight='bold')

        ax.set_xticks(range(len(phases)))
        ax.set_xticklabels(PHASES_DISPLAY, fontsize=13, fontweight='bold')
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels, fontsize=10, fontweight='bold')
        ax.set_title('a)', fontsize=16, fontweight='bold', loc='left', pad=10)

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, pad=0.02, aspect=30)
        cbar.set_label('Cumulative GDD', rotation=270, labelpad=20,
                      fontsize=12, fontweight='bold')
        cbar.ax.tick_params(labelsize=11)

        ax.tick_params(length=0)


def plot_delays_scatter(treatment_effects, ax):
    """
    Plot b) - Phenological delays scatter plot
    Y = position index (0, 1, 2, ...)
    X = delay %
    (as in original method, subplot ax2)
    """
    delays = []
    varieties_list = []
    treatments_list = []
    y_positions = []

    y_pos = 0
    for variety in sorted(treatment_effects.keys()):
        effects = treatment_effects[variety]
        for treatment in ['S1', 'S2']:
            if treatment in effects:
                phases = effects[treatment]
                if phases:
                    # Calculate average delay across all phases
                    avg_delay = np.mean([
                        p['percent_delay']
                        for p in phases.values()
                        if 'percent_delay' in p
                    ])

                    delays.append(avg_delay)
                    varieties_list.append(variety)
                    treatments_list.append(treatment)
                    y_positions.append(y_pos)
                    y_pos += 1

    if delays:
        # Scatter plot - LARGER POINTS
        colors = [TREATMENT_COLORS[t] for t in treatments_list]
        scatter = ax.scatter(delays, y_positions, c=colors,
                           s=200, alpha=0.8, edgecolors='black', linewidth=1.5)

        # Labels NEXT TO points - LARGER FONT
        for i, (variety, treatment, delay, y) in enumerate(
            zip(varieties_list, treatments_list, delays, y_positions)
        ):
            label = f"{variety}-{treatment}"
            # Position right or left based on delay sign
            if delay >= 0:
                ax.text(delay + 0.5, y, label, va='center', ha='left', fontsize=11, fontweight='bold')
            else:
                ax.text(delay - 0.5, y, label, va='center', ha='right', fontsize=11, fontweight='bold')

        # Vertical line at x=0
        ax.axvline(x=0, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)

        # Configure axes - CORRECT LABEL AND LARGER FONTS
        ax.set_xlabel('Phenological Delay (%)', fontsize=13, fontweight='bold')
        ax.set_ylabel('')  # Remove Y label (labels are near points)
        ax.set_title('b)', fontsize=16, fontweight='bold', loc='left', pad=10)

        # Limits
        ax.set_xlim(min(delays) - 3, max(delays) + 5)
        ax.set_ylim(-0.5, max(y_positions) + 0.5)

        # Hide Y ticks (labels are already on points)
        ax.set_yticks([])

        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='x')

        # Larger X ticks
        ax.tick_params(axis='x', labelsize=11)

        # Treatment legend - LARGER FONT
        legend_elements = [
            mpatches.Patch(color=TREATMENT_COLORS['S1'], label='S1 (Moderate stress)'),
            mpatches.Patch(color=TREATMENT_COLORS['S2'], label='S2 (Severe stress)')
        ]
        ax.legend(handles=legend_elements, loc='upper right',
                 fontsize=11, frameon=True, shadow=True)


def main():
    print("=" * 70)
    print("FIGURE 4: PHENOLOGICAL PHASE TEMPORAL ANALYSIS")
    print("=" * 70)

    # Load data
    print("\n📊 Loading/generating phenological data...")
    timing_data = load_and_prepare_data()
    print(f"   ✓ Data loaded for {len(timing_data)} varieties")

    # Calculate treatment effects
    print("\n📈 Calculating phenological delays...")
    treatment_effects = calculate_treatment_effects(timing_data)
    print(f"   ✓ Effects calculated for {len(treatment_effects)} varieties")

    # Create figure
    print("\n🎨 Creating figure...")
    fig = plt.figure(figsize=(14, 6))

    # Subplot a) - Heatmap
    ax1 = plt.subplot(1, 2, 1)
    plot_heatmap(timing_data, ax1)

    # Subplot b) - Scatter delays
    ax2 = plt.subplot(1, 2, 2)
    plot_delays_scatter(treatment_effects, ax2)

    plt.tight_layout()

    # Save
    output_dir = Path(__file__).parent

    png_path = output_dir / 'figure_04_phenological_timing.png'
    fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ PNG: {png_path}")

    pdf_path = output_dir / 'figure_04_phenological_timing.pdf'
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF: {pdf_path}")

    plt.close()

    print("\n" + "=" * 70)
    print("✅ COMPLETED!")
    print("=" * 70)


if __name__ == '__main__':
    main()
