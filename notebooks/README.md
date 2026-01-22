# Reproducibility Notebooks

Interactive Jupyter notebooks for reproducing all manuscript and supplementary figures.

## Available Notebooks

| Notebook | Description | Figures |
|----------|-------------|---------|
| **MANUSCRIPT_FIGURES.ipynb** | Main paper figures | Figures 1-8 |
| **SM_FIGURES.ipynb** | Supplementary materials | Fig. S1-S4, Tab. S2 |

---

## Run in the Cloud

No installation required - run the notebooks directly in your browser:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scatenag/Tomato-Salt-Tolerance-Analysis/HEAD?labpath=notebooks%2FMANUSCRIPT_FIGURES.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb)
[![Kaggle](https://kaggle.com/static/images/open-in-kaggle.svg)](https://kaggle.com/kernels/welcome?src=https://github.com/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb)

| Platform | Description | Notes |
|----------|-------------|-------|
| **Binder** | Full environment, no account needed | May take 1-2 min to start |
| **Google Colab** | Fast startup, GPU available | Requires Google account |
| **Kaggle** | Pre-installed packages | Requires Kaggle account |

> **Note**: Figure 3 (network) requires R and may not work in all cloud environments. All Python figures will generate correctly.

---

## MANUSCRIPT_FIGURES.ipynb

**Purpose**: Generate all 8 manuscript figures from primary data

### Generates:

| Figure | Description |
|--------|-------------|
| **Figure 1** | Pathway Activity Heatmap (7 levels × 6 genotypes) |
| **Figure 2** | Adaptive Differences (WR vs CV) - parameters across biological levels |
| **Figure 3** | Multilevel Correlation Network (circular layout) |
| **Figure 4** | Phenological Timing Analysis (GDD heatmap + delay scatter) |
| **Figure 5** | Temporal Dynamics (4×3 panel with significance asterisks) |
| **Figure 6** | Variety Ranking (total scores + category contribution) |
| **Figure 7** | Parameter Responsiveness Heatmap (WR10 vs CV) |
| **Figure 8** | Regression Comparison (3-panel dose-response curves) |

---

## SM_FIGURES.ipynb

**Purpose**: Generate supplementary figures and tables

### Generates:

| Item | Description |
|------|-------------|
| **Fig. S1** | Osmotic Regulation/Ionic Balance - pathway activity heatmap |
| **Fig. S2** | Primary/Secondary Metabolism - pathway activity heatmap |
| **Fig. S3** | Hormonal System - pathway activity heatmap |
| **Fig. S4** | Morphology and Growth - pathway activity heatmap |
| **Tab. S2** | Parameter Scores for CV and WR10 (F-statistic, η², % Change) |

### Tab. S2 Output:
- Formatted tables for CV and WR10
- Side-by-side comparison heatmap
- Summary statistics by category
- CSV export: `table_S2_parameter_scores.csv`

---

## Methodological Note

All calculations use **all biological replicates** directly (not aggregated by DAT), because:
- Most parameters are from **destructive measurements** (independent samples)
- Using all replicates provides higher statistical power
- This is the standard approach in experimental biology publications

---

## Local Usage

```bash
cd notebooks

# Main paper figures
jupyter notebook MANUSCRIPT_FIGURES.ipynb

# Supplementary materials
jupyter notebook SM_FIGURES.ipynb
```

The notebooks use data and scripts from the parent directories.

---

## Data Source

- **File**: `../data/master_dataset.csv`
- **Design**: 6 genotypes × 3 treatments × multiple timepoints × 6 replicates
- **Parameters**: 68+ biological measurements
- **Rows**: 1173 (all biological replicates)

---

## Output

### Manuscript Figures
Saved in their respective script directories:
- `../scripts/figure_01_pathway_activity/`
- `../scripts/figure_02_adaptive_differences/`
- `../scripts/figure_03_network/`
- `../scripts/figure_04_phenological_timing/`
- `../scripts/figure_05_temporal_dynamics/`
- `../scripts/figure_06_variety_ranking/`
- `../scripts/figure_07_responsiveness/`
- `../scripts/figure_08_regression_comparison/`

### Supplementary Figures
Saved in:
- `../scripts/supplementary_figures/`

Each figure is saved as PNG (300 DPI) and PDF.

---

## Requirements

```bash
pip install -r ../requirements.txt
```

**Figure 3** requires R with igraph:
```r
install.packages(c("igraph", "RColorBrewer"))
```

---

## Troubleshooting

**Script not found**: Ensure you're in the `notebooks/` directory

**Data file not found**: Verify `../data/master_dataset.csv` exists

**Import errors**: Install missing packages via `pip install <package>`

**Figure 3 needs R**: Install R and run `install.packages("igraph")` in R console

**Colab/Kaggle issues**: Clone the repository first with:
```python
!git clone https://github.com/scatenag/Tomato-Salt-Tolerance-Analysis.git
%cd Tomato-Salt-Tolerance-Analysis/notebooks
```
