#!/usr/bin/env python3
"""
Unified Data Preprocessing Pipeline
Derives all intermediate datasets for Figures 1, 3, and 7 from primary raw data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import sys

# Import centralized mappings
sys.path.append(str(Path(__file__).parent))
from parameter_mapping import PARAMETER_LEVELS, PARAMETER_CATEGORIES

# Define paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'
FIG3_DIR = ROOT_DIR / 'scripts' / 'figure_03_network'

MASTER_DATA = DATA_DIR / 'master_dataset.csv'

def load_primary_data():
    """
    Load primary data from master_dataset.csv.

    Uses ALL REPLICATES directly (not aggregated by DAT) because:
    - Most parameters are from destructive measurements (independent samples)
    - Using all replicates provides more robust statistical inference
    - This is the standard approach in experimental biology publications

    Returns the raw dataframe with all replicates.
    """
    if not MASTER_DATA.exists():
        raise FileNotFoundError(f"Master dataset not found: {MASTER_DATA}")

    print(f"Loading master data from {MASTER_DATA.name}...")
    df_raw = pd.read_csv(MASTER_DATA)

    # Use all replicates directly - no DAT aggregation
    # This is the statistically correct approach for destructive measurements
    print(f"✓ Unified data ready: {len(df_raw)} rows (all replicates)")
    return df_raw

def derive_figure_1_data(df):
    """Generate pathway activity data (Fold Change vs Control)"""
    print("Generating Figure 1 intermediate data...")
    
    results = []
    varieties = df['Variety'].unique()
    
    # Process each parameter that has a defined level
    params = [p for p in PARAMETER_LEVELS.keys() if p in df.columns]
    
    for variety in varieties:
        for treatment in ['C', 'S1', 'S2']:
            subset = df[(df['Variety'] == variety) & (df['Treatment'] == treatment)]
            if subset.empty: continue
            
            # Group by Level
            for level in set(PARAMETER_LEVELS.values()):
                level_params = [p for p, l in PARAMETER_LEVELS.items() if l == level and p in df.columns]
                if not level_params: continue
                
                # Calculate mean normalization factor from Control
                control_subset = df[(df['Variety'] == variety) & (df['Treatment'] == 'C')]
                
                activities = []
                for p in level_params:
                    c_mean = control_subset[p].mean()
                    t_mean = subset[p].mean()
                    if pd.notna(c_mean) and c_mean != 0:
                        # Score = t_mean / c_mean
                        activities.append(t_mean / c_mean)
                
                if activities:
                    results.append({
                        'Pathway': level,
                        'Variety': variety,
                        'Treatment': treatment,
                        'Activity_Score': np.mean(activities)
                    })
    
    output_df = pd.DataFrame(results)
    output_path = DATA_DIR / 'classic_pathway_activities_unified.csv'
    output_df.to_csv(output_path, index=False)
    print(f"✓ Saved to {output_path}")

def derive_figure_7_data(df):
    """Generate parameter ranking data (ANOVA, Eta-squared, % Change)"""
    print("Generating Figure 7 intermediate data...")
    
    results = []
    
    # Only use parameters defined in categories
    params = [p for p in PARAMETER_CATEGORIES.keys() if p in df.columns]
    
    for variety in df['Variety'].unique():
        v_data = df[df['Variety'] == variety]
        
        for param in params:
            # Prepare data groups for ANOVA
            groups = [v_data[v_data['Treatment'] == t][param].dropna() for t in ['C', 'S1', 'S2']]
            groups = [g for g in groups if not g.empty]
            
            if len(groups) < 2: continue
            
            # ANOVA
            try:
                f_stat, p_val = stats.f_oneway(*groups)
            except:
                f_stat, p_val = np.nan, np.nan
            
            # Eta-squared = SS_between / SS_total
            all_vals = pd.concat(groups)
            if len(all_vals) > 0:
                overall_mean = all_vals.mean()
                ss_total = np.sum((all_vals - overall_mean)**2)
                ss_between = np.sum([len(g) * (g.mean() - overall_mean)**2 for g in groups])
                eta_sq = ss_between / ss_total if ss_total != 0 else 0
            else:
                eta_sq = 0
            
            # % Change C to S2
            mean_c = v_data[v_data['Treatment'] == 'C'][param].mean()
            mean_s2 = v_data[v_data['Treatment'] == 'S2'][param].mean()
            pct_change = ((mean_s2 - mean_c) / mean_c * 100) if pd.notna(mean_c) and mean_c != 0 else 0
            
            # Normalized scores (0-100) for heatmap
            # Handled in the plotting script, but we'll provide the raw metrics
            
            results.append({
                'parameter': param,
                'variety': variety,
                'category': PARAMETER_CATEGORIES[param],
                'f_statistic': f_stat,
                'p_value': p_val,
                'eta_squared': eta_sq,
                'pct_change_C_to_S2': pct_change,
                'f_stat_score': min(100, f_stat * 10), # Heuristic matching original
                'eta_sq_score': eta_sq * 100,
                'pct_change_score': abs(pct_change) # Heuristic matching original
            })
            
    output_df = pd.DataFrame(results)
    output_path = DATA_DIR / 'parameter_ranking_unified.csv'
    output_df.to_csv(output_path, index=False)
    print(f"✓ Saved to {output_path}")

def derive_figure_3_data(df):
    """Generate network nodes and edges (Spearman correlation)"""
    print("Generating Figure 3 intermediate data...")
    
    # 1. Nodes
    nodes = []
    params = [p for p in PARAMETER_LEVELS.keys() if p in df.columns]
    for p in params:
        nodes.append({
            'id': p,
            'level': PARAMETER_LEVELS[p]
        })
    nodes_df = pd.DataFrame(nodes)
    nodes_path = FIG3_DIR / 'nodes_unified.csv'
    nodes_df.to_csv(nodes_path, index=False)
    
    # 2. Edges (Spearman Correlation across all variety/treatment)
    data_for_corr = df[params].dropna(how='all')
    corr_matrix, p_matrix = stats.spearmanr(data_for_corr, nan_policy='omit')
    
    edges = []
    for i in range(len(params)):
        for j in range(i + 1, len(params)):
            r = corr_matrix[i, j]
            p = p_matrix[i, j]
            
            # Filter: |R| > 0.3 and p < 0.05 (allowing R visualization script to apply its own 0.35/0.30 logic)
            if abs(r) > 0.3 and p < 0.05:
                p1, p2 = params[i], params[j]
                l1, l2 = PARAMETER_LEVELS[p1], PARAMETER_LEVELS[p2]
                
                edges.append({
                    'source': p1,
                    'target': p2,
                    'correlation': r,
                    'p_value': p,
                    'level1': l1,
                    'level2': l2,
                    'connection_type': 'intra_level' if l1 == l2 else 'cross_level'
                })
                
    edges_df = pd.DataFrame(edges)
    edges_path = FIG3_DIR / 'edges_unified.csv'
    edges_df.to_csv(edges_path, index=False)
    print(f"✓ Saved nodes/edges to {FIG3_DIR}")

def main():
    try:
        df = load_primary_data()
        derive_figure_1_data(df)
        derive_figure_7_data(df)
        derive_figure_3_data(df)
        print("\n✅ All intermediate data generated successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
