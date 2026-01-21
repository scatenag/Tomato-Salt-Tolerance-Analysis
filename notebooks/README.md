# Reproducibility Notebook

Interactive Jupyter notebook for reproducing all manuscript figures.

## Run in the Cloud

No installation required - run the notebook directly in your browser:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scatenag/Tomato-Salt-Tolerance-Analysis/HEAD?labpath=notebooks%2FMANUSCRIPT_FIGURES.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb)
[![Kaggle](https://kaggle.com/static/images/open-in-kaggle.svg)](https://kaggle.com/kernels/welcome?src=https://github.com/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb)

| Platform | Description | Notes |
|----------|-------------|-------|
| **Binder** | Full environment, no account needed | May take 1-2 min to start |
| **Google Colab** | Fast startup, GPU available | Requires Google account |
| **Kaggle** | Pre-installed packages | Requires Kaggle account |

> **Note**: Figure 3 (network) requires R and may not work in all cloud environments. All Python figures (1, 2, 4-8) will generate correctly.

---

## MANUSCRIPT_FIGURES.ipynb

**Purpose**: Generate all 8 manuscript figures from primary data
**Best for**: Reviewers, readers wanting to verify figures

### Generates:

1. **Figure 1**: Pathway Activity Heatmap (7 levels × 6 genotypes)
2. **Figure 2**: Adaptive Differences (WR vs CV) - parameters across biological levels
3. **Figure 3**: Multilevel Correlation Network (circular layout)
4. **Figure 4**: Phenological Timing Analysis (GDD heatmap + delay scatter)
5. **Figure 5**: Temporal Dynamics (4×3 panel with significance asterisks)
6. **Figure 6**: Variety Ranking (total scores + category contribution)
7. **Figure 7**: Parameter Responsiveness Heatmap (WR10 vs CV)
8. **Figure 8**: Regression Comparison (3-panel dose-response curves)

---

## Local Usage

```bash
cd notebooks
jupyter notebook MANUSCRIPT_FIGURES.ipynb
```

The notebook uses data and scripts from the parent directories.

## Data Source

- **File**: `../data/master_dataset.csv`
- **Design**: 6 genotypes × 3 treatments × 4 timepoints × 3 replicates
- **Parameters**: 68+ biological measurements

## Output

All figures are saved in their respective script directories:
- `../scripts/figure_01_pathway_activity/`
- `../scripts/figure_02_adaptive_differences/`
- `../scripts/figure_03_network/`
- `../scripts/figure_04_phenological_timing/`
- `../scripts/figure_05_temporal_dynamics/`
- `../scripts/figure_06_variety_ranking/`
- `../scripts/figure_07_responsiveness/`
- `../scripts/figure_08_regression_comparison/`

Each figure is saved as PNG (300 DPI) and PDF.

## Requirements

```bash
pip install -r ../requirements.txt
```

**Figure 3** requires R with igraph:
```r
install.packages(c("igraph", "RColorBrewer"))
```

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
