# Scripts Directory

Python and R scripts for generating all manuscript and supplementary figures.

## Directory Structure

```
scripts/
├── figure_01_pathway_activity/     # Figure 1: Pathway activity heatmap
├── figure_02_adaptive_differences/ # Figure 2: WR vs CV differences
├── figure_03_network/              # Figure 3: Correlation network (R)
├── figure_04_phenological_timing/  # Figure 4: GDD timing analysis
├── figure_05_temporal_dynamics/    # Figure 5: Temporal evolution
├── figure_06_variety_ranking/      # Figure 6: Tolerance ranking
├── figure_07_responsiveness/       # Figure 7: Parameter responsiveness
├── figure_08_regression_comparison/# Figure 8: Regression comparison
├── supplementary_figures/          # Supplementary figures (S1-S4, Tab. S2)
├── parameter_mapping.py            # Centralized parameter definitions
└── unify_data_sources.py           # Data preprocessing pipeline
```

---

## Core Scripts

### unify_data_sources.py

**Data preprocessing pipeline** that derives intermediate datasets from `master_dataset.csv`.

```bash
python scripts/unify_data_sources.py
```

**Generates**:
- `data/classic_pathway_activities_unified.csv` (for Figure 1)
- `data/parameter_ranking_unified.csv` (for Figure 7)
- `scripts/figure_03_network/nodes_unified.csv` (for Figure 3)
- `scripts/figure_03_network/edges_unified.csv` (for Figure 3)

**Methodological note**: Uses all biological replicates directly (not aggregated by DAT) for robust statistical inference.

### parameter_mapping.py

**Centralized parameter definitions** used by multiple scripts:
- `PARAMETER_LEVELS`: Maps parameters to biological levels
- `PARAMETER_CATEGORIES`: Maps parameters to ranking categories
- `LEVEL_TRANSLATIONS`: English translations for pathway names

---

## Manuscript Figures

| Directory | Figure | Script | Language |
|-----------|--------|--------|----------|
| `figure_01_pathway_activity/` | Pathway Activity Heatmap | `generate_pathway_heatmap.py` | Python |
| `figure_02_adaptive_differences/` | Adaptive Differences | `generate_figure_02.py` | Python |
| `figure_03_network/` | Correlation Network | `generate_network_PUBLICATION_FINAL.R` | R |
| `figure_04_phenological_timing/` | GDD Timing | `generate_figure_04.py` | Python |
| `figure_05_temporal_dynamics/` | Temporal Dynamics | `generate_figure_05.py` | Python |
| `figure_06_variety_ranking/` | Variety Ranking | `generate_figure_06.py` | Python |
| `figure_07_responsiveness/` | Parameter Responsiveness | `generate_figure_07.py` | Python |
| `figure_08_regression_comparison/` | Regression Comparison | `generate_figure_08.py` | Python |

---

## Supplementary Figures

Located in `supplementary_figures/`:

| File | Description |
|------|-------------|
| `generate_figure_S1.py` | Osmotic Regulation/Ionic Balance heatmap |
| `generate_figure_S2.py` | Primary/Secondary Metabolism heatmap |
| `generate_figure_S3.py` | Hormonal System heatmap |
| `generate_figure_S4.py` | Morphology and Growth heatmap |

**Tab. S2** (Parameter Scores) is generated in the `SM_FIGURES.ipynb` notebook and saved as `table_S2_parameter_scores.csv`.

---

## Running Scripts

### All Manuscript Figures

```bash
# From repository root
cd Tomato-Salt-Tolerance-Analysis

# First, generate intermediate data
python scripts/unify_data_sources.py

# Then generate each figure
python scripts/figure_01_pathway_activity/generate_pathway_heatmap.py
python scripts/figure_02_adaptive_differences/generate_figure_02.py
Rscript scripts/figure_03_network/generate_network_PUBLICATION_FINAL.R
python scripts/figure_04_phenological_timing/generate_figure_04.py
python scripts/figure_05_temporal_dynamics/generate_figure_05.py
python scripts/figure_06_variety_ranking/generate_figure_06.py
python scripts/figure_07_responsiveness/generate_figure_07.py
python scripts/figure_08_regression_comparison/generate_figure_08.py
```

### Supplementary Figures

```bash
python scripts/supplementary_figures/generate_figure_S1.py
python scripts/supplementary_figures/generate_figure_S2.py
python scripts/supplementary_figures/generate_figure_S3.py
python scripts/supplementary_figures/generate_figure_S4.py
```

Or use the `SM_FIGURES.ipynb` notebook for interactive generation.

---

## Output Format

All scripts generate:
- **PNG**: 300 DPI, white background
- **PDF**: Vector format for publication

Output files are saved in each script's directory.

---

## Dependencies

### Python
- pandas, numpy
- matplotlib, seaborn
- scipy

### R (Figure 3 only)
- igraph
- RColorBrewer

---

## Statistical Methods

| Method | Used In |
|--------|---------|
| **Fold Change** (T/C) | Figures 1, S1-S4 |
| **Standardized Difference** ((WR-CV)/\|CV\|) | Figure 2 |
| **Spearman Correlation** | Figure 3 |
| **Welch's t-test** | Figures 5, S1-S4 |
| **One-way ANOVA** | Figures 6, 7, Tab. S2 |
| **Linear/Exponential Regression** | Figure 8 |
| **Effect Size (η²)** | Figure 7, Tab. S2 |

All statistical tests use **all biological replicates** for maximum statistical power.

---

## Troubleshooting

**FileNotFoundError**: Run scripts from the repository root directory, or run `unify_data_sources.py` first.

**ImportError**: Install dependencies with `pip install -r requirements.txt`.

**R errors**: Install igraph with `install.packages("igraph")` in R console.

**Font warnings**: Safe to ignore - figures will use system default font.
