#!/usr/bin/env python3
"""
Figure 1: Classic Pathway Activity Analysis Heatmap
High-quality publication figure showing pathway responses to salt stress
Removes control columns and shows only stress treatments (S1, S2) as fold change vs control
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add scripts directory to path to import parameter_mapping
sys.path.append(str(Path(__file__).parent.parent))
from parameter_mapping import LEVEL_TRANSLATIONS

# Set publication-quality parameters with larger fonts
plt.rcParams.update({
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'font.size': 16,
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'font.family': 'Arial',
    'figure.figsize': (12, 8)
})


def load_and_process_data():
    """Load pathway activities data and process for heatmap visualization"""

    # Load the pathway activities data (unified source)
    data_path = Path(__file__).parent.parent.parent / 'data' / 'classic_pathway_activities_unified.csv'
    df = pd.read_csv(data_path)


    # Map pathway names to English translations if needed (unified source uses biological level names)
    df['Pathway_EN'] = df['Pathway'].map(LEVEL_TRANSLATIONS)

    # Create pivot tables for S2 and Control
    df_s2 = df[df['Treatment'] == 'S2'].pivot(
        index='Pathway_EN', columns='Variety', values='Activity_Score'
    )

    df_control = df[df['Treatment'] == 'C'].pivot(
        index='Pathway_EN', columns='Variety', values='Activity_Score'
    )

    # Calculate fold change: S2 - Control (since Control is normalized to 1.0)
    fold_change = df_s2 - df_control

    # Reorder columns to have logical grouping
    variety_order = ['CV', 'WR2', 'WR9', 'WR10', 'WR11', 'WR14']
    available_cols = [col for col in variety_order if col in fold_change.columns]
    fold_change = fold_change[available_cols]

    # Reorder pathways in order from original figure (bottom to top in display)
    pathway_order = [
        'Fruit Quality',
        'Hormonal System',
        'Leaf functionality',
        'Morphology and Growth',
        'Osmotic Regulation/Ionic Balance',
        'Primary/Secondary Metabolism'
    ]

    available_pathways = [p for p in pathway_order if p in fold_change.index]
    fold_change = fold_change.loc[available_pathways]

    return fold_change

def create_publication_heatmap(data):
    """Create publication-quality heatmap"""

    fig, ax = plt.subplots(figsize=(12, 7))

    # Create saturated colormap with distinct colors
    from matplotlib.colors import LinearSegmentedColormap

    # Custom colormap with stronger saturation for better differentiation
    # Very dark blues for negative, whites for zero, reds/oranges for positive
    colors = [
        '#021B3D', '#08306B', '#08519C', '#2171B5', '#4292C6', '#6BAED6', '#9ECAE1', '#C6DBEF', '#DEEBF7',  # Blues (negative, from very dark to light)
        '#FFFFFF',  # White (zero)
        '#FEE5D9', '#FCBBA1', '#FC9272', '#FB6A4A', '#EF3B2C', '#CB181D', '#99000D', '#67000D'  # Reds/oranges (positive)
    ]
    cmap = LinearSegmentedColormap.from_list('custom_diverging', colors, N=256)

    # Create the heatmap without annotations (we'll add them manually)
    # Scale from -1 to +6 to show full range including extreme values
    sns.heatmap(
        data,
        annot=False,
        cmap=cmap,
        center=0.0,  # Center colormap at 0 (no change)
        cbar_kws={
            'label': 'Activity Score (Fold Change vs Control)',
            'shrink': 0.8
        },
        ax=ax,
        square=False,
        linewidths=0.5,
        linecolor='white',
        vmin=-1.0,
        vmax=6.0
    )

    # Add custom annotations with asterisks for significant changes
    for i, pathway in enumerate(data.index):
        for j, variety in enumerate(data.columns):
            value = data.iloc[i, j]
            if pd.notna(value):
                # Format with + sign for positive values
                text = f"{value:+.2f}"

                # Add asterisk for significant changes (|fold change| > 0.5)
                if abs(value) > 0.5:
                    text += "\n*"

                # Choose text color based on background intensity
                text_color = 'white' if abs(value) > 3.0 else 'black'

                ax.text(j + 0.5, i + 0.5, text,
                       ha='center', va='center',
                       fontsize=12, fontweight='bold',
                       color=text_color)

    # Remove title
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Rotate x-axis labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    ax.grid(False)

    plt.tight_layout()

    return fig

def main():
    """Main function to generate the figure"""
    
    print("Generating Figure 1: Classic Pathway Activity Analysis Heatmap...")
    
    # Load and process data
    heatmap_data = load_and_process_data()
    
    print(f"Data shape: {heatmap_data.shape}")
    print(f"Pathways: {list(heatmap_data.index)}")
    print(f"Treatments: {list(heatmap_data.columns)}")
    
    # Create the figure
    fig = create_publication_heatmap(heatmap_data)
    
    # Save in multiple formats
    output_dir = Path('.')
    
    # Save as high-resolution PNG
    fig.savefig(output_dir / 'figure_01_pathway_activity_heatmap.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    
    # Save as vector format (SVG)
    fig.savefig(output_dir / 'figure_01_pathway_activity_heatmap.svg', 
                bbox_inches='tight', facecolor='white')
    
    # Save as PDF for publication
    fig.savefig(output_dir / 'figure_01_pathway_activity_heatmap.pdf', 
                bbox_inches='tight', facecolor='white')
    
    print("✓ Figure saved in PNG, SVG, and PDF formats")
    
    # Display basic statistics
    print("\nData Statistics:")
    print(f"Mean activity: {heatmap_data.mean().mean():.3f}")
    print(f"Max activity: {heatmap_data.max().max():.3f}")
    print(f"Min activity: {heatmap_data.min().min():.3f}")
    
    # Show which pathways are most/least responsive
    pathway_ranges = (heatmap_data.max(axis=1) - heatmap_data.min(axis=1))
    print(f"\nMost variable pathway: {pathway_ranges.idxmax()} (range: {pathway_ranges.max():.3f})")
    print(f"Least variable pathway: {pathway_ranges.idxmin()} (range: {pathway_ranges.min():.3f})")
    
    # Close the figure to free memory
    plt.close(fig)

if __name__ == "__main__":
    main()