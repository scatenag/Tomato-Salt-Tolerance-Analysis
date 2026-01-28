#!/usr/bin/env python3
"""
Figure 2: Adaptive Differences - FINAL VERSION
Using standardized difference: (WR_mean - CV_mean) / |CV_mean|
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from scipy.stats import ttest_ind
import warnings
warnings.filterwarnings('ignore')

# Biological systems with parameters (exact order)
BIOLOGICAL_SYSTEMS = [
    ('Hormonal system', [
        'ABA (ng/mg)', 'IAA (ng/mg)', 'GA4 (ng/mg)', 'SA (ng/mg)',
        'JA (ng/mg)', 'Z (ng/mg)', 'Melatonin (ng/mg)', 'Metatopolin (ng/mg)'
    ]),
    ('Primary/secondary metabolism', [
        'Osmolytes (osm/kg)', 'Phenols (mg/g FW)', 'Flavonoids (mg/g FW)',
        'Antioxidant capacity (μmol Fe II/g FW)', 'Total chlorophyll (μg/g FW)',
        'Lutein (μg/g FW)', 'Violaxanthin (μg/g FW)'
    ]),
    ('Osmotic regulaion/ionic balance', [
        'Na/K ratio leaves', 'Na/K ratio roots', 'Na/Ca ratio leaves',
        'Na/Ca ratio roots', 'Electrolytic leakage (μS/cm)', 'Relative water content (%)'
    ]),
    ('Leaf functionality', [
        'Fv/Fm', 'Stomatal conductance (μmol/sec)'
    ]),
    ('Morphology and growth', [
        'Main shoot height (cm)', 'Main shoot leaves (number)', 'Main shoot nodes (number)',
        'Primary shoot height (cm)', 'Primary shoot leaves (number)', 'Stem diameter (cm)',
        'Lateral shoots (number)', 'Leaves surface (cm²)', 'Total fresh weight (g)',
        'Total dry weight (g)', 'Dry matter (%)'
    ]),
    ('Fruit quality', [
        'fresh weight 10 fruits (g)', 'Fruits dry weight (%)', 'Fruits soluble solids (°brix)',
        'Fruits pH', 'Fruits firmness (kg/cm2)', 'Fruits lycopene (μg/g DW)',
        'Fruits β carotene (μg/g DW)', 'Acidity (g citric acid/100 g)', 'Fruits EC (mS/cm)'
    ])
]

def load_data():
    """Load data from master dataset"""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'master_dataset.csv'

    if not data_path.exists():
        raise FileNotFoundError(f"Master dataset not found: {data_path}")

    df = pd.read_csv(data_path)
    print(f"✓ Master dataset loaded: {len(df)} rows")

    return df

def load_and_calculate_adaptive_differences():
    """Load data and calculate WR vs CV adaptive differences from master dataset"""
    df = load_data()

    # Separate CV and WR data
    cv_data = df[df['Variety'] == 'CV']
    wr_data = df[df['Variety'].isin(['WR2', 'WR9', 'WR10', 'WR11', 'WR14'])]

    results = {}

    for system_name, params in BIOLOGICAL_SYSTEMS:
        for param in params:
            # If parameter doesn't exist in dataset, assign 0 value (will show as white cell)
            if param not in df.columns:
                results[param] = {
                    'value': 0.0,
                    'p_value': None,
                    'sig_level': ''
                }
                continue

            try:
                cv_mean = cv_data[param].dropna().mean()
                wr_mean = wr_data[param].dropna().mean()

                if np.isnan(cv_mean) or np.isnan(wr_mean) or cv_mean == 0:
                    # Assign 0 for missing/invalid data
                    results[param] = {
                        'value': 0.0,
                        'p_value': None,
                        'sig_level': ''
                    }
                    continue

                # CORRECT CALCULATION: Standardized difference
                adaptive_diff = (wr_mean - cv_mean) / abs(cv_mean)

                # Statistical test
                cv_values = cv_data[param].dropna()
                wr_values = wr_data[param].dropna()

                p_value = None
                if len(cv_values) >= 2 and len(wr_values) >= 2:
                    try:
                        _, p_value = ttest_ind(wr_values, cv_values, equal_var=False)
                    except:
                        p_value = 1.0

                # Determine significance level
                abs_diff = abs(adaptive_diff)
                if abs_diff > 1.0:
                    sig_level = '***'
                elif abs_diff > 0.5:
                    sig_level = '**'
                elif abs_diff > 0.3:
                    sig_level = '*'
                else:
                    sig_level = ''

                results[param] = {
                    'value': adaptive_diff,
                    'p_value': p_value,
                    'sig_level': sig_level
                }

            except Exception as e:
                print(f"⚠️  Error with parameter {param}: {e}")
                continue

    return results

def create_publication_heatmap(results):
    """Create publication-quality heatmap using EXACT approach from original script"""

    # Figure size - NO LEGEND, more space for heatmap
    fig = plt.figure(figsize=(26, 14))

    # Setup grid: ONLY category labels (left) and heatmap (center) - NO LEGEND
    n_categories = len(BIOLOGICAL_SYSTEMS)
    gs = fig.add_gridspec(n_categories, 2,
                         width_ratios=[0.22, 1],  # Labels, Heatmap (NO legend column)
                         hspace=0.75, wspace=0.05,  # MUCH MORE space between rows to avoid overlaps
                         left=0.05, right=0.98, top=0.96, bottom=0.15)  # MORE bottom margin

    # Original colormap from carmassi script
    colors = ['#2e86ab', '#ffffff', '#d62728']  # Blue, White, Red
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

    for i, (category, params) in enumerate(BIOLOGICAL_SYSTEMS):
        # Label axis (left column)
        label_ax = fig.add_subplot(gs[i, 0])
        label_ax.axis('off')

        # Category label - EXTREMELY LARGE, no parameter count
        label_ax.text(0.95, 0.5, f'{category}',
                     transform=label_ax.transAxes, fontweight='bold', fontsize=22,
                     ha='right', va='center', rotation=0)

        # Heatmap axis (center column)
        ax = fig.add_subplot(gs[i, 1])

        # Get values for this category
        values = []
        param_labels = []

        for param in params:
            if param in results:
                values.append(results[param]['value'])
            else:
                values.append(np.nan)
            param_labels.append(param)

        n_params = len(params)

        # Prepare data for heatmap (1 row, n columns)
        # Replace NaN with 0 (white) to avoid empty cells
        heatmap_data = np.array(values).reshape(1, -1)
        heatmap_data_filled = np.where(np.isnan(heatmap_data), 0, heatmap_data)

        # Create heatmap using imshow - scale -1 to +1
        im = ax.imshow(heatmap_data_filled, cmap=cmap, aspect='auto', vmin=-1, vmax=1)

        # Parameter labels with adaptive wrapping based on number of parameters
        formatted_labels = []

        # Uniform fontsize for all categories
        fontsize = 16
        linespacing = 0.75
        # Adjust wrap threshold based on parameter count - MORE AGGRESSIVE
        if n_params >= 11:
            wrap_threshold = 5  # Very aggressive for 11 params
        elif n_params >= 9:
            wrap_threshold = 6
        elif n_params >= 7:
            wrap_threshold = 7  # More aggressive for 7-8 params
        else:
            wrap_threshold = 9

        # Parameter -> acronym mapping (updated as requested)
        PARAM_ACRONYMS = {
            # Hormonal System
            'ABA (ng/mg)': 'ABA',
            'IAA (ng/mg)': 'IAA',
            'GA4 (ng/mg)': 'GA4',
            'SA (ng/mg)': 'SA',
            'JA (ng/mg)': 'JA',
            'Z (ng/mg)': 'Z',
            'Melatonin (ng/mg)': 'MEL',
            'Metatopolin (ng/mg)': 'MET',
            # Primary/Secondary Metabolism
            'Osmolytes (osm/kg)': 'OSM',
            'Phenols (mg/g FW)': 'PHE',
            'Flavonoids (mg/g FW)': 'FLA',
            'Antioxidant capacity (μmol Fe II/g FW)': 'ANTIOX',
            'Total chlorophyll (μg/g FW)': 'CHL',
            'Lutein (μg/g FW)': 'LUT',
            'Violaxanthin (μg/g FW)': 'VIO',
            # Osmotic Regulation/Ionic Balance
            'Na/K ratio leaves': 'Na/K L',
            'Na/K ratio roots': 'Na/K R',
            'Na/Ca ratio leaves': 'Na/Ca L',
            'Na/Ca ratio roots': 'Na/Ca R',
            'Electrolytic leakage (μS/cm)': 'EL',
            'Relative water content (%)': 'RWC',
            # Leaf functionality
            'Stomatal conductance (μmol/sec)': 'SC',
            'Fv/Fm': 'Fv/Fm',
            # Morphology and Growth
            'Main shoot height (cm)': 'MSH',
            'Main shoot leaves (number)': 'MSL',
            'Main shoot nodes (number)': 'MSN',
            'Primary shoot height (cm)': 'PSH',
            'Primary shoot leaves (number)': 'PSL',
            'Stem diameter (cm)': 'SD',
            'Lateral shoots (number)': 'LAS',
            'Leaves surface (cm²)': 'LES',
            'Total fresh weight (g)': 'FW',
            'Total dry weight (g)': 'DW',
            'Dry matter (%)': 'DM%',
            # Fruit Quality
            'fresh weight 10 fruits (g)': 'FFW',
            'Fruits dry weight (%)': 'FDW',
            'Fruits soluble solids (°brix)': 'SS',
            'Fruits pH': 'pH',
            'Fruits firmness (kg/cm2)': 'FF',
            'Fruits lycopene (μg/g DW)': 'LYC',
            'Fruits β carotene (μg/g DW)': 'βC',
            'Acidity (g citric acid/100 g)': 'AC',
            'Fruits EC (mS/cm)': 'EC',
        }

        for param in param_labels:
            # Use acronym if available
            if param in PARAM_ACRONYMS:
                formatted_labels.append(PARAM_ACRONYMS[param])
            else:
                # Fallback: Remove units of measurement (everything in parentheses)
                param_no_units = param.split('(')[0].strip()
                formatted_labels.append(param_no_units)

        ax.set_xticks(range(n_params))
        ax.set_xticklabels(formatted_labels, rotation=0, ha='center', fontsize=22,  # MUCH LARGER
                          linespacing=linespacing, fontweight='bold')
        # MUCH MORE padding for labels to avoid cutting
        ax.tick_params(axis='x', pad=15, length=0)

        # Remove y ticks
        ax.set_yticks([])

        # Add values in cells
        for j, val in enumerate(values):
            if not np.isnan(val):
                # Format value with significance
                param = param_labels[j]
                sig_level = results[param]['sig_level'] if param in results else ''

                if abs(val) > 1.0:
                    text = f'{val:.2f}***'
                elif abs(val) > 0.5:
                    text = f'{val:.2f}**'
                elif abs(val) > 0.3:
                    text = f'{val:.2f}*'
                else:
                    text = f'{val:.2f}'

                # Text color based on intensity - GIGANTIC FONT
                color = 'white' if abs(val) > 0.7 else 'black'
                ax.text(j, 0, text, ha='center', va='center',
                       fontweight='bold', fontsize=20, color=color)

    # Add colorbar legend at bottom - CENTERED relative to heatmap (not page)
    # Heatmap spans from ~0.22 to 0.98 (based on gridspec layout)
    # Calculate center position relative to heatmap
    heatmap_left = 0.05 + 0.22 * (0.98 - 0.05) / 1.22  # ~0.22
    heatmap_right = 0.98
    heatmap_center = (heatmap_left + heatmap_right) / 2  # ~0.60
    cbar_width = 0.4  # Width of colorbar
    cbar_left = heatmap_center - cbar_width / 2  # Center colorbar on heatmap
    cbar_ax = fig.add_axes([cbar_left, 0.04, cbar_width, 0.02])  # [left, bottom, width, height]

    # Create a ScalarMappable for the colorbar
    import matplotlib.cm as cm
    from matplotlib.colors import Normalize
    norm = Normalize(vmin=-1, vmax=1)
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
    cbar.set_ticklabels(['-1.0', '-0.5', '0', '+0.5', '+1.0'])
    cbar.ax.tick_params(labelsize=18)

    # Add labels to colorbar
    cbar_ax.text(-0.02, 0.5, 'CV > WR', transform=cbar_ax.transAxes,
                 fontsize=20, fontweight='bold', ha='right', va='center', color='#2e86ab')
    cbar_ax.text(1.02, 0.5, 'WR > CV', transform=cbar_ax.transAxes,
                 fontsize=20, fontweight='bold', ha='left', va='center', color='#d62728')

    # Title for colorbar
    cbar.set_label('Adaptive Difference (WR vs CV)', fontsize=18, fontweight='bold', labelpad=10)

    plt.tight_layout(rect=[0, 0.08, 1, 1])  # Leave space at bottom for colorbar

    return fig

def main():
    """Main execution"""
    print("=" * 70)
    print("FIGURE 2: ADAPTIVE DIFFERENCES - FINAL VERSION")
    print("=" * 70)

    # Calculate adaptive differences
    print("\n1. Calculating adaptive differences (WR vs CV)...")
    print("   Formula: (WR_mean - CV_mean) / |CV_mean|")
    results = load_and_calculate_adaptive_differences()
    print(f"✅ Calculated {len(results)} adaptive differences")

    # Create heatmap
    print("\n2. Creating final publication heatmap...")
    fig = create_publication_heatmap(results)

    # Save figure
    output_dir = Path('.')

    fig.savefig(output_dir / 'figure_02_adaptive_differences.png',
               dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(output_dir / 'figure_02_adaptive_differences.svg',
               bbox_inches='tight', facecolor='white')
    fig.savefig(output_dir / 'figure_02_adaptive_differences.pdf',
               bbox_inches='tight', facecolor='white')

    print("✓ Final heatmap saved")
    print(f"\n✅ FIGURE 2 COMPLETED!")
    print(f"📁 Output: figure_02_adaptive_differences.[png/svg/pdf]")

    plt.close(fig)

if __name__ == "__main__":
    main()
