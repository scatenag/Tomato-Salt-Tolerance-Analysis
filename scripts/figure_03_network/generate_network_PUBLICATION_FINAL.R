#!/usr/bin/env Rscript
# ==============================================================================
# FIGURE 3: CIRCULAR NETWORK VISUALIZATION - EXACT MANUSCRIPT STYLE
# Circular layout with colored external labels
# ==============================================================================

suppressPackageStartupMessages({
  library(igraph)
  library(ggplot2)
  library(dplyr)
  library(gridExtra)
})

# ==============================================================================
# CONFIGURATION
# ==============================================================================

FIG_WIDTH <- 14
FIG_HEIGHT <- 14
DPI <- 300

# ==============================================================================
# 0. ARGOMENTI DA RIGA DI COMANDO
# ==============================================================================
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 2) {
  THRESHOLD_POS <- as.numeric(args[1])
  THRESHOLD_NEG <- as.numeric(args[2])
} else {
  THRESHOLD_POS <- 0.35
  THRESHOLD_NEG <- -0.30
}

# New arguments for visibility toggles
SHOW_INTRA <- if (length(args) >= 3) as.logical(args[3]) else TRUE
SHOW_CROSS <- if (length(args) >= 4) as.logical(args[4]) else TRUE

cat(sprintf("Thresholds: pos >= %.2f, neg <= %.2f\n", THRESHOLD_POS, THRESHOLD_NEG))
cat(sprintf("Visibility: Intra=%s, Cross=%s\n", SHOW_INTRA, SHOW_CROSS))

# Specific node order in the circle (from reference image)
# Starting from Fv/Fm at top-left, clockwise
NODE_ORDER <- c(
  # Leaf functionality (green) - top left
  "Fv/Fm",
  # Ionic/Osmotic (blue)
  "Relative water content (%)",
  "Electrolytic leakage (μS/cm)",
  "Na/K ratio roots",
  "Na/K ratio leaves",
  # Metabolic (dark green)
  "Total chlorophyll (μg/g FW)",
  "Flavonoids (mg/g FW)",
  "Phenols (mg/g FW)",
  "Osmolytes (osm/kg)",
  # Hormonal (red) - right
  "Metatopolin (ng/mg)",
  "Melatonin (ng/mg)",
  "Z (ng/mg)",
  "JA (ng/mg)",
  "SA (ng/mg)",
  "GA4 (ng/mg)",
  "IAA (ng/mg)",
  "ABA (ng/mg)",
  # Quality (dark orange) - bottom right
  "Fruits soluble solids (°brix)",
  "Fruits dry weight (g)",
  "fresh weight 10 fruits (g)",
  # Morphological (purple) - bottom
  "Total dry weight (g)",
  "Total fresh weight (g)",
  "Leaves surface (cm²)",
  "Main shoot nodes (number)",
  "Main shoot height (cm)",
  # Phenological (orange) - bottom left
  "Cumulative floral truss length (cm)",
  "Trusses maturing (number)",
  "Fruit set (trusses number)",
  "Flowering (trusses number)",
  # Leaf functionality (green) - left
  "Stomatal conductance (μmol/sec)"
)

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================
# 1. LOAD DATA (Unified Source)
cat("Loading network data...\n")

nodes_df <- read.csv("nodes_unified.csv",
  stringsAsFactors = FALSE
)

# EXCLUDE SPECIFIC PHENOLOGICAL NODES AS REQUESTED BY USER
# "Days_to_next_phase_from_prev_start" and "Days_to_next_phase_from_time_0"
nodes_df <- nodes_df %>%
  filter(!id %in% c("Days_to_next_phase_from_prev_start", "Days_to_next_phase_from_time_0"))

edges_df <- read.csv("edges_unified.csv",
  stringsAsFactors = FALSE
)

# FILTER EDGES INVOLVING EXCLUDED NODES
edges_df <- edges_df %>%
  filter(source %in% nodes_df$id & target %in% nodes_df$id)

cat(sprintf("   %d nodes, %d edges\n", nrow(nodes_df), nrow(edges_df)))

# ==============================================================================
# 2. COLORS FOR BIOLOGICAL LEVEL (from original YAML configuration)
# ==============================================================================

level_colors <- c(
  "hormonal" = "#FF6B6B", # Coral red
  "metabolic" = "#4ECDC4", # Teal/cyan
  "ionic_osmotic" = "#45B7D1", # Light blue
  "leaf_functionality" = "#96CEB4", # Mint green
  "phenological" = "#D4A500", # Yellow ochre/mustard (readable on white)
  "morphological" = "#DDA0DD", # Light purple (plum)
  "quality" = "#FFB347" # Light orange
)

# ==============================================================================
# 3. PREPARE NODE DATA
# ==============================================================================

# Create abbreviated labels with initial capital
get_short_label <- function(name) {
  label <- gsub("\\s*\\(.*\\)\\s*$", "", name)
  # Specific abbreviations as requested
  label <- gsub("^Metatopolin$", "MET", label)
  label <- gsub("^Melatonin$", "MEL", label)
  # Abbreviations for long labels that get cut off
  label <- gsub("^Cumulative floral truss length$", "Cum. floral truss length", label)
  label <- gsub("^Stomatal conductance$", "Stomatal conduct.", label)
  label <- gsub("^Relative water content$", "Rel. water content", label)
  label <- gsub("^Electrolytic leakage$", "Electrolytic leak.", label)
  label <- gsub("^Total chlorophyll$", "Total chloroph.", label)
  label <- gsub("^Fruits soluble solids$", "Fruits sol. solids", label)
  label <- gsub("^Fresh weight 10 fruits$", "FW 10 fruits", label)
  label <- gsub("^fresh weight 10 fruits$", "FW 10 fruits", label)
  # First letter uppercase
  label <- paste0(toupper(substr(label, 1, 1)), substr(label, 2, nchar(label)))
  label
}

# Order nodes according to specified order
nodes_in_data <- nodes_df$id
nodes_ordered <- NODE_ORDER[NODE_ORDER %in% nodes_in_data]
# Add any missing nodes
missing_nodes <- setdiff(nodes_in_data, nodes_ordered)
if (length(missing_nodes) > 0) {
  nodes_ordered <- c(nodes_ordered, missing_nodes)
}

n_nodes <- length(nodes_ordered)

# Calculate circular positions
# Start from 120 degrees (top-left) and proceed clockwise
angles <- seq(from = 120, by = -360 / n_nodes, length.out = n_nodes)
angles_rad <- angles * pi / 180

# Circle radius for nodes
radius <- 1

# Create node dataframe with positions
node_positions <- data.frame(
  id = nodes_ordered,
  x = radius * cos(angles_rad),
  y = radius * sin(angles_rad),
  angle = angles,
  stringsAsFactors = FALSE
)

# Add level and color
node_positions <- merge(node_positions, nodes_df, by = "id", all.x = TRUE)
node_positions$color <- level_colors[node_positions$level]
node_positions$label <- sapply(node_positions$id, get_short_label)

# Reorder according to original order
node_positions <- node_positions[match(nodes_ordered, node_positions$id), ]
rownames(node_positions) <- NULL

# ==============================================================================
# 4. PREPARE EDGES AND FILTER
# ==============================================================================

# Ensure data is clean
nodes_ordered <- trimws(nodes_ordered)
node_positions$id <- trimws(node_positions$id)
edges_df$source <- trimws(edges_df$source)
edges_df$target <- trimws(edges_df$target)
edges_df$correlation <- as.numeric(edges_df$correlation)

# FILTER ONLY STRONGER CORRELATIONS and apply visibility toggles
cat(sprintf("Filtering strong correlations (|r| >= %.2f positive, |r| >= %.2f negative)...\n", THRESHOLD_POS, abs(THRESHOLD_NEG)))

edges_filtered <- edges_df %>%
  filter(source %in% nodes_ordered & target %in% nodes_ordered) %>%
  left_join(nodes_df %>% select(id, source_level = level), by = c("source" = "id")) %>%
  left_join(nodes_df %>% select(id, target_level = level), by = c("target" = "id")) %>%
  mutate(is_intra_level = source_level == target_level) %>%
  filter(
    (is_intra_level & SHOW_INTRA) | (!is_intra_level & SHOW_CROSS)
  ) %>%
  filter(
    (correlation >= THRESHOLD_POS) | # Strong positive
      (correlation <= THRESHOLD_NEG) # Strong negative
  )

cat(sprintf("   Edges after filter: %d (from %d original)\n", nrow(edges_filtered), nrow(edges_df)))

# ==============================================================================
# 5. CALCULATE DEGREE FOR NODE SIZE (DYNAMIC)
# ==============================================================================

# Create graph based on FILTERED edges to get dynamic degree
g <- graph_from_data_frame(
  d = edges_filtered[, c("source", "target")],
  vertices = node_positions[, c("id", "level")],
  directed = FALSE
)

node_degrees <- degree(g)
node_positions$degree <- node_degrees[node_positions$id]

# Scale node sizes based on filtered degree
size_min <- 4
size_max <- 14
max_deg <- max(node_positions$degree)

if (max_deg > 0) {
  node_positions$size <- size_min +
    (node_positions$degree / max_deg) * (size_max - size_min)
} else {
  # If no edges, keep all nodes at minimum size
  node_positions$size <- size_min
}

# ==============================================================================
# 6. PREPARE EDGE PLOTTING DATA
# ==============================================================================

# Create node -> level mapping
node_level_map <- setNames(node_positions$level, node_positions$id)

# Prepare edges with colors
edges_plot <- edges_filtered %>%
  mutate(
    # Colors:
    # Positive Cross -> Red
    # Positive Intra -> Green
    # Negative Cross -> Blue
    # Negative Intra -> Dark Green (addressing user query)
    edge_color = case_when(
      correlation < 0 & is_intra_level ~ "#33691E", # Negative Intra: Dark Green
      correlation < 0 ~ "#64B5F6", # Negative Cross: Blue
      is_intra_level ~ "#7CB342", # Positive Intra: Light Green
      TRUE ~ "#E57373" # Positive Cross: Red
    )
  )

# Add coordinates
edges_plot <- edges_plot %>%
  left_join(node_positions %>% select(id, x, y), by = c("source" = "id")) %>%
  rename(x_start = x, y_start = y) %>%
  left_join(node_positions %>% select(id, x, y), by = c("target" = "id")) %>%
  rename(x_end = x, y_end = y)

# ==============================================================================
# 6. CREATE MAIN PLOT
# ==============================================================================

cat("Creating figure...\n")

# Calculate label positions (outside circle) - farther for larger labels
label_radius <- 1.35
node_positions$label_x <- label_radius * cos(node_positions$angle * pi / 180)
node_positions$label_y <- label_radius * sin(node_positions$angle * pi / 180)

# Calculate label rotation angle - labels are always readable
node_positions$label_angle <- sapply(node_positions$angle, function(a) {
  # Normalize angle between 0 and 360
  a <- a %% 360
  if (a > 90 && a < 270) {
    return(a + 180)
  } else {
    return(a)
  }
})

# Hjust for labels
node_positions$hjust <- sapply(node_positions$angle, function(a) {
  a <- a %% 360
  if (a > 90 && a < 270) {
    return(1) # Aligned right
  } else {
    return(0) # Aligned left
  }
})

# Main plot
p_main <- ggplot() +
  # Edges (correlation lines) - GREATLY INCREASED THICKNESS
  geom_segment(
    data = edges_plot,
    aes(x = x_start, y = y_start, xend = x_end, yend = y_end, color = edge_color),
    alpha = 0.6,
    linewidth = 1.2
  ) +
  scale_color_identity() +

  # Nodes
  geom_point(
    data = node_positions,
    aes(x = x, y = y, fill = color, size = size),
    shape = 21,
    color = "black",
    stroke = 1.0
  ) +
  scale_fill_identity() +
  scale_size_identity() +

  # Colored labels (without background)
  geom_text(
    data = node_positions,
    aes(
      x = label_x, y = label_y, label = label, color = color,
      angle = label_angle, hjust = hjust
    ),
    size = 6,
    fontface = "bold",
    vjust = 0.5
  ) +

  # Theme - less white space
  coord_fixed(ratio = 1, xlim = c(-2.5, 2.5), ylim = c(-2.0, 2.0), clip = "off") +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    plot.margin = margin(5, 5, 5, 5)
  )

# ==============================================================================
# 7. CREATE BIOLOGICAL LEVELS LEGEND - two columns (4+3) with text beside
# ==============================================================================

# Labels for legend (on one line)
levels_labels_legend <- c(
  "hormonal" = "Hormonal system",
  "metabolic" = "Primary/secondary metabolism",
  "ionic_osmotic" = "Osmotic regulation / ion balance",
  "leaf_functionality" = "Leaf functionality",
  "phenological" = "Phenological",
  "morphological" = "Morphology and growth",
  "quality" = "Fruit quality"
)

# Column 1: 4 elements
col1_levels <- c("hormonal", "metabolic", "ionic_osmotic", "leaf_functionality")
col1_data <- data.frame(
  level = col1_levels,
  y = 4:1,
  color = level_colors[col1_levels],
  label = levels_labels_legend[col1_levels],
  stringsAsFactors = FALSE
)

# Column 2: 3 elements
col2_levels <- c("phenological", "morphological", "quality")
col2_data <- data.frame(
  level = col2_levels,
  y = 4:2,
  color = level_colors[col2_levels],
  label = levels_labels_legend[col2_levels],
  stringsAsFactors = FALSE
)

# BIOLOGICAL LEVELS legend - two columns with dot + text beside - LARGER FONTS
p_legend_levels <- ggplot() +
  # Title - LARGER
  annotate("text", x = 3.5, y = 5.3, label = "BIOLOGICAL LEVELS", fontface = "bold", size = 7) +
  # Column 1 - dots with black border - LARGER
  geom_point(
    data = col1_data, aes(x = 1, y = y, fill = color),
    shape = 21, color = "black", size = 10, stroke = 1.5, show.legend = FALSE
  ) +
  scale_fill_identity() +
  # Column 1 - text beside - LARGER
  geom_text(data = col1_data, aes(x = 1.5, y = y, label = label), size = 5, hjust = 0) +
  # Column 2 - dots with black border - LARGER
  geom_point(
    data = col2_data, aes(x = 5.5, y = y, fill = color),
    shape = 21, color = "black", size = 10, stroke = 1.5, show.legend = FALSE
  ) +
  # Column 2 - text beside - LARGER
  geom_text(data = col2_data, aes(x = 6.0, y = y, label = label), size = 5, hjust = 0) +
  coord_cartesian(ylim = c(0.5, 5.8), xlim = c(0.5, 9.5)) +
  theme_void() +
  theme(
    plot.margin = margin(0, 5, 0, 5)
  )

# ==============================================================================
# 8. CREATE CORRELATIONS LEGEND - exactly as in reference image
# ==============================================================================

# Updated CORRELATIONS legend
p_legend_corr <- ggplot() +
  # CORRELATIONS title - LARGER
  annotate("text", x = 1.8, y = 6.3, label = "CORRELATIONS", fontface = "bold", size = 7) +

  # Cross-level (Red/Blue)
  geom_segment(aes(x = 1, xend = 2.2, y = 5.0, yend = 5.0), color = "#E57373", linewidth = 5) +
  annotate("text", x = 2.5, y = 5.0, label = sprintf("Positive Cross-level (r \u2265 %.2f)", THRESHOLD_POS), size = 5, hjust = 0) +
  geom_segment(aes(x = 1, xend = 2.2, y = 4.0, yend = 4.0), color = "#64B5F6", linewidth = 5) +
  annotate("text", x = 2.5, y = 4.0, label = sprintf("Negative Cross-level (r \u2264 %.2f)", THRESHOLD_NEG), size = 5, hjust = 0) +

  # Intra-level (Greens)
  geom_segment(aes(x = 1, xend = 2.2, y = 2.5, yend = 2.5), color = "#7CB342", linewidth = 5) +
  annotate("text", x = 2.5, y = 2.5, label = sprintf("Positive Intra-level (r \u2265 %.2f)", THRESHOLD_POS), size = 5, hjust = 0) +
  geom_segment(aes(x = 1, xend = 2.2, y = 1.5, yend = 1.5), color = "#33691E", linewidth = 5) +
  annotate("text", x = 2.5, y = 1.5, label = sprintf("Negative Intra-level (r \u2264 %.2f)", THRESHOLD_NEG), size = 5, hjust = 0) +
  coord_cartesian(ylim = c(0.5, 6.8), xlim = c(0.5, 6.5)) +
  theme_void() +
  theme(
    plot.margin = margin(0, 5, 0, 5)
  )

# Combine the two legends horizontally
p_legend <- arrangeGrob(
  p_legend_levels,
  p_legend_corr,
  ncol = 2,
  widths = c(3, 1.5)
)

# Combine main plot with legend - less white space
p_final <- arrangeGrob(
  p_main,
  p_legend,
  ncol = 1,
  heights = c(4, 1)
)

# ==============================================================================
# 10. SAVE FIGURE WITH INTRA-LEVEL
# ==============================================================================

cat("Saving figure with intra-level...\n")

output_base <- "Figure_03_network_EXACT"

# PNG
ggsave(
  paste0(output_base, ".png"),
  plot = p_final,
  width = FIG_WIDTH,
  height = FIG_HEIGHT,
  dpi = DPI,
  bg = "white"
)

# PDF
ggsave(
  paste0(output_base, ".pdf"),
  plot = p_final,
  width = FIG_WIDTH,
  height = FIG_HEIGHT,
  device = cairo_pdf,
  bg = "white"
)

# TIFF for journal
ggsave(
  paste0(output_base, ".tiff"),
  plot = p_final,
  width = FIG_WIDTH,
  height = FIG_HEIGHT,
  dpi = DPI,
  bg = "white",
  compression = "lzw"
)

# ==============================================================================
# 11. GENERATE VERSION WITHOUT INTRA-LEVEL EDGES
# ==============================================================================

cat("Generating version without intra-level edges...\n")

# Filter only cross-level edges
edges_plot_cross <- edges_plot %>%
  filter(!is_intra_level)

# Recalculate degree and size for CROSS ONLY version (Dynamic)
g_cross <- graph_from_data_frame(
  d = edges_plot_cross[, c("source", "target")],
  vertices = node_positions[, c("id", "level")],
  directed = FALSE
)

node_degrees_cross <- degree(g_cross)
node_positions_cross <- node_positions
node_positions_cross$degree <- node_degrees_cross[node_positions_cross$id]

# Scale node sizes based on cross-only degree
max_deg_cross <- max(node_positions_cross$degree)
if (max_deg_cross > 0) {
  node_positions_cross$size <- size_min +
    (node_positions_cross$degree / max_deg_cross) * (size_max - size_min)
} else {
  node_positions_cross$size <- size_min
}

# Main plot without intra-level
p_main_cross <- ggplot() +
  # Edges (only cross-level)
  geom_segment(
    data = edges_plot_cross,
    aes(x = x_start, y = y_start, xend = x_end, yend = y_end, color = edge_color),
    alpha = 0.6,
    linewidth = 1.2
  ) +
  scale_color_identity() +
  # Nodes
  geom_point(
    data = node_positions_cross,
    aes(x = x, y = y, fill = color, size = size),
    shape = 21,
    color = "black",
    stroke = 1.0
  ) +
  scale_fill_identity() +
  scale_size_identity() +
  # Colored labels (without background)
  geom_text(
    data = node_positions_cross,
    aes(
      x = label_x, y = label_y, label = label, color = color,
      angle = label_angle, hjust = hjust
    ),
    size = 6,
    fontface = "bold",
    vjust = 0.5
  ) +
  coord_fixed(ratio = 1, xlim = c(-2.5, 2.5), ylim = c(-2.0, 2.0), clip = "off") +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    plot.margin = margin(5, 5, 5, 5)
  )

# CORRELATIONS legend without intra-level (only red and blue) - LARGER FONTS
p_legend_corr_cross <- ggplot() +
  annotate("text", x = 1.8, y = 5.3, label = "CORRELATIONS", fontface = "bold", size = 7) +
  geom_segment(aes(x = 1, xend = 2.2, y = 3.5, yend = 3.5), color = "#E57373", linewidth = 5) +
  annotate("text", x = 2.5, y = 3.5, label = sprintf("Positive (r \u2265 %.2f)", THRESHOLD_POS), size = 5, hjust = 0) +
  geom_segment(aes(x = 1, xend = 2.2, y = 2.5, yend = 2.5), color = "#64B5F6", linewidth = 5) +
  annotate("text", x = 2.5, y = 2.5, label = sprintf("Negative (r \u2264 %.2f)", THRESHOLD_NEG), size = 5, hjust = 0) +
  coord_cartesian(ylim = c(0.5, 5.8), xlim = c(0.5, 5.5)) +
  theme_void() +
  theme(
    plot.margin = margin(0, 5, 0, 5)
  )

# Combine cross-level legend
p_legend_cross <- arrangeGrob(
  p_legend_levels,
  p_legend_corr_cross,
  ncol = 2,
  widths = c(3, 1.2)
)

# Combine cross-level plot with legend
p_final_cross <- arrangeGrob(
  p_main_cross,
  p_legend_cross,
  ncol = 1,
  heights = c(4, 1)
)

# Save version without intra-level
output_base_cross <- "Figure_03_network_CROSS_LEVEL_ONLY"

ggsave(
  paste0(output_base_cross, ".png"),
  plot = p_final_cross,
  width = FIG_WIDTH,
  height = FIG_HEIGHT,
  dpi = DPI,
  bg = "white"
)

ggsave(
  paste0(output_base_cross, ".pdf"),
  plot = p_final_cross,
  width = FIG_WIDTH,
  height = FIG_HEIGHT,
  device = cairo_pdf,
  bg = "white"
)

ggsave(
  paste0(output_base_cross, ".tiff"),
  plot = p_final_cross,
  width = FIG_WIDTH,
  height = FIG_HEIGHT,
  dpi = DPI,
  bg = "white",
  compression = "lzw"
)

cat("\n======================================================================\n")
cat("COMPLETED!\n")
cat("======================================================================\n")
cat(sprintf("Generated files:\n"))
cat(sprintf("  WITH INTRA-LEVEL:\n"))
cat(sprintf("    - %s.png\n", output_base))
cat(sprintf("    - %s.pdf\n", output_base))
cat(sprintf("    - %s.tiff\n", output_base))
cat(sprintf("  WITHOUT INTRA-LEVEL (cross-level only):\n"))
cat(sprintf("    - %s.png\n", output_base_cross))
cat(sprintf("    - %s.pdf\n", output_base_cross))
cat(sprintf("    - %s.tiff\n", output_base_cross))
cat("======================================================================\n")
