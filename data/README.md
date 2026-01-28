# Data Directory

This directory contains the primary experimental data and derived intermediate files.

## Primary Data

### master_dataset.csv

**The single source of truth for all analyses.**

| Property | Value |
|----------|-------|
| **Rows** | 1173 (all biological replicates) |
| **Columns** | 69 (including identifiers and 68+ parameters) |
| **Format** | CSV (UTF-8) |

#### Structure

| Column | Description |
|--------|-------------|
| `DAT` | Days After Transplant (9-98) |
| `Variety` | Genotype: CV, WR2, WR9, WR10, WR11, WR14 |
| `Treatment` | Salinity: C (control), S1 (moderate), S2 (severe) |
| `Reply` | Replicate number (1-6) |
| `Species` | *S. lycopersicum* (CV) or *S. pimpinellifolium* (WR) |
| `Phenological phase` | vegetative, bloom, bloom fruit set, maturazione |
| *68+ parameters* | Biological measurements (hormones, metabolites, morphology, etc.) |

#### Parameter Categories

| Category | Examples |
|----------|----------|
| **Hormonal** | ABA, IAA, GA4, SA, JA, Z, Melatonin, Metatopolin |
| **Metabolic** | Osmolytes, Phenols, Flavonoids, Antioxidant capacity, Chlorophyll |
| **Ionic/Osmotic** | Na/K ratio, Na/Ca ratio, Electrolytic leakage, RWC |
| **Morphological** | Main shoot height, Leaves, Nodes, Stem diameter, Biomass |
| **Fruit quality** | Lycopene, β-carotene, Soluble solids, pH, Firmness |

---

## Derived Intermediate Files

These files are **automatically generated** by `scripts/unify_data_sources.py` and should not be edited manually.

### classic_pathway_activities_unified.csv

**Used by**: Figure 1 (Pathway Activity Heatmap)

| Column | Description |
|--------|-------------|
| `Pathway` | Biological level (Hormonal, Metabolic, etc.) |
| `Variety` | Genotype |
| `Treatment` | C, S1, or S2 |
| `Activity_Score` | Mean fold change (T/C) for pathway |

### parameter_ranking_unified.csv

**Used by**: Figure 7 (Parameter Responsiveness)

| Column | Description |
|--------|-------------|
| `parameter` | Parameter name |
| `variety` | Genotype |
| `category` | Performance Maintenance, Physiological Stability, or Stress Marker Response |
| `f_statistic` | ANOVA F-statistic |
| `eta_squared` | Effect size (η²) |
| `pct_change_C_to_S2` | Percent change from Control to S2 |

### summary_dataset_for_inspection.csv

**Used by**: Human inspection only (not used by scripts)

Aggregated means per DAT × Variety × Treatment combination (216 rows).

---

## Methodological Note

All analyses use **all biological replicates** directly (not pre-aggregated), because:

1. **Most parameters are from destructive measurements** - each observation comes from a different plant (independent samples)
2. **Higher statistical power** - more observations provide more robust inference
3. **Standard approach** - this is the norm in experimental biology publications

The derived intermediate files are generated from the raw replicates for specific figure requirements.

---

## Data Provenance

- **Source**: Original experimental measurements
- **Collection period**: 2023-2024
- **Location**: University of Pisa / Sant'Anna School of Advanced Studies
- **DOI**: [10.5281/zenodo.17792340](https://doi.org/10.5281/zenodo.17792340)

---

## Regenerating Intermediate Files

If intermediate files are missing or need to be regenerated:

```bash
cd /path/to/Tomato-Salt-Tolerance-Analysis
python scripts/unify_data_sources.py
```

This will create:
- `data/classic_pathway_activities_unified.csv`
- `data/parameter_ranking_unified.csv`
- `data/summary_dataset_for_inspection.csv`
- `scripts/figure_03_network/nodes_unified.csv`
- `scripts/figure_03_network/edges_unified.csv`
