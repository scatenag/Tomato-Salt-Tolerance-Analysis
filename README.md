# Tomato Salt Tolerance Analysis - Manuscript Reproducibility

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17792340.svg)](https://doi.org/10.5281/zenodo.17792340)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scatenag/Tomato-Salt-Tolerance-Analysis/HEAD?labpath=notebooks%2FMANUSCRIPT_FIGURES.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb)

Complete reproducibility repository for the manuscript:

---

## Interactive Notebooks

| Notebook | Content | Run Online |
|----------|---------|------------|
| **[MANUSCRIPT_FIGURES.ipynb](notebooks/MANUSCRIPT_FIGURES.ipynb)** | Main paper figures (1-8) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scatenag/Tomato-Salt-Tolerance-Analysis/HEAD?labpath=notebooks%2FMANUSCRIPT_FIGURES.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb) |
| **[SM_FIGURES.ipynb](notebooks/SM_FIGURES.ipynb)** | Supplementary materials (Fig. S1-S4, Tab. S2) | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scatenag/Tomato-Salt-Tolerance-Analysis/HEAD?labpath=notebooks%2FSM_FIGURES.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/SM_FIGURES.ipynb) |

---

**"A multilevel trait-integration framework identifies key predictors of tomato salt tolerance"**

*Susanna Cialli, Giulia Carmassi, Guido Scatena, Rita Maggini, Luca Incrocci, Anna Mensuali, Alice Trivellini*

Journal of Experimental Botany (JXB)

---

## Quick Start

### Run in the Cloud (No Installation)

Click to run the notebook directly in your browser:

| Platform | Link | Notes |
|----------|------|-------|
| **Binder** | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/scatenag/Tomato-Salt-Tolerance-Analysis/HEAD?labpath=notebooks%2FMANUSCRIPT_FIGURES.ipynb) | No account needed |
| **Google Colab** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scatenag/Tomato-Salt-Tolerance-Analysis/blob/main/notebooks/MANUSCRIPT_FIGURES.ipynb) | Requires Google account |

### Local Installation

#### Generate All Figures

```bash
# Clone repository
git clone https://github.com/scatenag/Tomato-Salt-Tolerance-Analysis.git
cd Tomato-Salt-Tolerance-Analysis

# Install dependencies
pip install -r requirements.txt

# Generate intermediate data files
python scripts/unify_data_sources.py

# Generate all 8 manuscript figures
python scripts/figure_01_pathway_activity/generate_pathway_heatmap.py
python scripts/figure_02_adaptive_differences/generate_figure_02.py
Rscript scripts/figure_03_network/generate_network_PUBLICATION_FINAL.R
python scripts/figure_04_phenological_timing/generate_figure_04.py
python scripts/figure_05_temporal_dynamics/generate_figure_05.py
python scripts/figure_06_variety_ranking/generate_figure_06.py
python scripts/figure_07_responsiveness/generate_figure_07.py
python scripts/figure_08_regression_comparison/generate_figure_08.py
```

### Interactive Notebooks

```bash
# Manuscript figures (main paper)
jupyter notebook notebooks/MANUSCRIPT_FIGURES.ipynb

# Supplementary materials figures
jupyter notebook notebooks/SM_FIGURES.ipynb
```

---

## Repository Structure

```
Tomato-Salt-Tolerance-Analysis/
├── data/
│   └── master_dataset.csv              # Primary experimental data (all replicates)
├── notebooks/
│   ├── MANUSCRIPT_FIGURES.ipynb        # Interactive figure generation (Figures 1-8)
│   └── SM_FIGURES.ipynb                # Supplementary materials (Fig. S1-S4, Tab. S2)
├── scripts/
│   ├── figure_01_pathway_activity/     # Figure 1: Pathway activity heatmap
│   ├── figure_02_adaptive_differences/ # Figure 2: WR vs CV differences
│   ├── figure_03_network/              # Figure 3: Correlation network (R)
│   ├── figure_04_phenological_timing/  # Figure 4: GDD timing analysis
│   ├── figure_05_temporal_dynamics/    # Figure 5: Temporal evolution
│   ├── figure_06_variety_ranking/      # Figure 6: Tolerance ranking
│   ├── figure_07_responsiveness/       # Figure 7: Parameter responsiveness
│   ├── figure_08_regression_comparison/# Figure 8: Regression comparison
│   ├── supplementary_figures/          # Supplementary figures (S1-S4, Tab. S2)
│   ├── parameter_mapping.py            # Centralized parameter definitions
│   └── unify_data_sources.py           # Data preprocessing pipeline
├── documentation/
│   └── MANUSCRIPT_TO_CODE_MAPPING.md   # Figure-to-code traceability
├── requirements.txt                    # Python dependencies
└── LICENSE                             # MIT License
```

---

## Experimental Design

- **Genotypes**: 6 total
  - 1 cultivated variety (CV): *Solanum lycopersicum* 'Principe Borghese'
  - 5 wild accessions (WR): *Solanum pimpinellifolium* (WR2, WR9, WR10, WR11, WR14)
- **Salinity treatments**:
  - Control (C): 3.22 dS/m
  - Moderate stress (S1): 11 dS/m
  - Severe stress (S2): 21 dS/m
- **Time points**: 12 DAT (Days After Transplant) for non-destructive measurements, 4 DAT for destructive measurements
- **Replicates**: 6 per treatment (3-6 depending on timepoint)

---

## Manuscript Figures

| Figure | Description | Script |
|--------|-------------|--------|
| **Figure 1** | Pathway Activity Heatmap | `figure_01_pathway_activity/generate_pathway_heatmap.py` |
| **Figure 2** | Adaptive Differences (WR vs CV) | `figure_02_adaptive_differences/generate_figure_02.py` |
| **Figure 3** | Multilevel Correlation Network | `figure_03_network/generate_network_PUBLICATION_FINAL.R` |
| **Figure 4** | Phenological GDD Timing | `figure_04_phenological_timing/generate_figure_04.py` |
| **Figure 5** | Temporal Dynamics | `figure_05_temporal_dynamics/generate_figure_05.py` |
| **Figure 6** | Variety Ranking | `figure_06_variety_ranking/generate_figure_06.py` |
| **Figure 7** | Parameter Responsiveness | `figure_07_responsiveness/generate_figure_07.py` |
| **Figure 8** | Regression Comparison | `figure_08_regression_comparison/generate_figure_08.py` |

## Supplementary Materials

| Item | Description | Location |
|------|-------------|----------|
| **Fig. S1** | Osmotic Regulation/Ionic Balance | `supplementary_figures/` |
| **Fig. S2** | Primary/Secondary Metabolism | `supplementary_figures/` |
| **Fig. S3** | Hormonal System | `supplementary_figures/` |
| **Fig. S4** | Morphology and Growth | `supplementary_figures/` |
| **Tab. S2** | Parameter Scores (CV vs WR10) | `supplementary_figures/table_S2_parameter_scores.csv` |

All figures are generated as PNG (300 DPI) and PDF.

---

## Data Source

All analyses use a single primary data file:

- **File**: `data/master_dataset.csv`
- **Content**: 68+ biological parameters measured across all genotype × treatment × timepoint combinations
- **Rows**: 1173 (all biological replicates)

No simulated or synthetic data is used.

---

## Statistical Methods

### Methodological Note

All calculations use **all biological replicates** directly (not aggregated by DAT), because:
- Most parameters are from **destructive measurements** where each observation comes from a different plant (independent samples)
- Using all replicates provides more robust statistical inference with higher statistical power
- This is the standard approach in experimental biology publications

### Statistical Tests

- **Correlations**: Spearman rank correlation with significance testing
- **ANOVA**: One-way ANOVA with F-statistic and effect size (η²)
- **t-tests**: Welch's t-test with Bonferroni correction
- **Regression**: Linear and exponential dose-response models
- **Network analysis**: Correlation-based edge filtering (|r| > 0.3, p < 0.05)

---

## Requirements

### Python
- Python 3.8+
- pandas, numpy, matplotlib, seaborn, scipy

### R (Figure 3 only)
- R 4.0+
- igraph, RColorBrewer

Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## Citation

If you use this code or data, please cite:

```
Cialli S, Carmassi G, Scatena G, Maggini R, Incrocci L, Mensuali A, Trivellini A.
A multilevel trait-integration framework identifies key predictors of tomato salt tolerance.
Journal of Experimental Botany. 2026.
```

Data available at: https://doi.org/10.5281/zenodo.17792340

---

## Funding

This research was supported by Agritech National Research Center, PNRR M4C2, ID: CN00000022.

---

## Authors

- **Susanna Cialli** - Sant'Anna School of Advanced Studies, Pisa
- **Giulia Carmassi** - University of Pisa
- **Guido Scatena** - ISPRA
- **Rita Maggini** - University of Pisa
- **Luca Incrocci** - University of Pisa
- **Anna Mensuali** - Sant'Anna School of Advanced Studies, Pisa
- **Alice Trivellini** - University of Pisa

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Troubleshooting

**ModuleNotFoundError**: Ensure virtual environment is activated and dependencies installed.

**FileNotFoundError**: Run scripts from the repository root directory.

**Arial font warning**: Safe to ignore - figures will use system default font.

**R package errors**: Install igraph with `install.packages("igraph")` in R.

---

**Repository**: https://github.com/scatenag/Tomato-Salt-Tolerance-Analysis
