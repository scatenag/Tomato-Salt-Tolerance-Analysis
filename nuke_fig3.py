import json
import os

notebook_path = 'notebooks/MANUSCRIPT_FIGURES.ipynb'
if not os.path.exists(notebook_path):
    print(f"Error: {notebook_path} not found.")
    exit(1)

with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Aggressive deletion of ANY cell related to Figure 3
new_cells = []
for i, cell in enumerate(nb['cells']):
    source_str = "".join(cell.get('source', [])).lower()
    # Broad markers for Figure 3 and interactive code
    kill_markers = ['figure 3', 'fig3', 'correlation network', 'render_fig3', 'generate_interactive_network', 'interactive figure 3']
    if any(m in source_str for m in kill_markers):
        print(f"Deleting cell {i} (contains marker)")
        continue
    new_cells.append(cell)

nb['cells'] = new_cells

# Re-insert Header and Code
# Header
header = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        '## Figure 3: Integrated Multi-Level Biological Network\n',
        '\n',
        '> **Datasets:** `nodes_unified.csv` and `edges_unified.csv` (derived from primary data)\n',
        '\n',
        '**Key Features:**\n',
        '- Multi-level connectivity (Hormonal, Metabolic, Physiological, etc.)\n',
        '- Dynamic thresholding for positive and negative correlations\n',
        '- Automatic recalculation of node importance (degree) based on selected filters\n'
    ]
}

# Version 3.0 Code - Even more robust
code_content = [
    '# CODE VERSION: 3.0 (Definitive Nuclear Fix)\n',
    'import shutil\n',
    'from IPython.display import display, Image, clear_output, Markdown\n',
    'import ipywidgets as widgets\n',
    'import subprocess\n',
    '\n',
    '# 1. Global clear to remove ANY artifacts from this cell or others\n',
    'clear_output(wait=True)\n',
    '\n',
    '# 2. Namespace isolation: unique prefix "nuke_f3"\n',
    'def nuke_f3_render():\n',
    '    display(Markdown("### Figure 3: Integrated Multi-Level Biological Network (Interactive)"))\n',
    '\n',
    '    nuke_f3_r_script = project_root / "scripts" / "figure_03_network" / "generate_network_PUBLICATION_FINAL.R"\n',
    '    nuke_f3_R_BIN = shutil.which("Rscript")\n',
    '\n',
    '    def nuke_f3_run(pos_thr, neg_thr, show_intra, show_cross, btn=None):\n',
    '        if not nuke_f3_R_BIN: return\n',
    '        if btn: \n',
    '            btn.disabled = True\n',
    '            btn.description = "⏳ Processing..."\n',
    '        \n',
    '        try:\n',
    '            # Force uppercase for R booleans\n',
    '            args = [nuke_f3_R_BIN, str(nuke_f3_r_script.name), str(pos_thr), str(neg_thr), str(show_intra).upper(), str(show_cross).upper()]\n',
    '            subprocess.run(args, cwd=str(nuke_f3_r_script.parent), capture_output=True, text=True)\n',
    '            \n',
    '            # Identify which image to show\n',
    '            if show_intra or not show_cross:\n',
    '                img = nuke_f3_r_script.parent / "Figure_03_network_EXACT.png"\n',
    '                label = "Full Network (Intra + Cross level)"\n',
    '            else:\n',
    '                img = nuke_f3_r_script.parent / "Figure_03_network_CROSS_LEVEL_ONLY.png"\n',
    '                label = "Cross-level Only Network"\n',
    '            \n',
    '            if img.exists():\n',
    '                display(Markdown(f"#### {label} (|r| \u2265 {pos_thr} / |r| \u2264 {abs(neg_thr)})"))\n',
    '                display(Image(filename=str(img), width=850))\n',
    '        finally:\n',
    '            if btn:\n',
    '                btn.disabled = False\n',
    '                btn.description = "Generate Figure"\n',
    '\n',
    '    if not nuke_f3_R_BIN:\n',
    '        print("⚠️ Rscript not found in environment.")\n',
    '    else:\n',
    '        # Unique widget names to avoid kernel state collisions\n',
    '        nuke_f3_s_pos = widgets.FloatSlider(value=0.35, min=0.1, max=0.9, step=0.05, description="Pos r \u2265:")\n',
    '        nuke_f3_s_neg = widgets.FloatSlider(value=-0.30, min=-0.9, max=-0.1, step=0.05, description="Neg r \u2264:")\n',
    '        nuke_f3_c_intra = widgets.Checkbox(value=True, description="Show Intra-level")\n',
    '        nuke_f3_c_cross = widgets.Checkbox(value=True, description="Show Cross-level")\n',
    '        nuke_f3_b_run = widgets.Button(description="Generate Figure", button_style="primary")\n',
    '        \n',
    '        # Dedicated output widget\n',
    '        nuke_f3_out = widgets.Output()\n',
    '        \n',
    '        def nuke_f3_on_click(b): \n',
    '            with nuke_f3_out: \n',
    '                clear_output(wait=True)\n',
    '                nuke_f3_run(nuke_f3_s_pos.value, nuke_f3_s_neg.value, nuke_f3_c_intra.value, nuke_f3_c_cross.value, btn=nuke_f3_b_run)\n',
    '        \n',
    '        nuke_f3_b_run.on_click(nuke_f3_on_click)\n',
    '        \n',
    '        # Display widgets\n',
    '        ui = widgets.VBox([\n',
    '            widgets.HBox([nuke_f3_s_pos, nuke_f3_s_neg]), \n',
    '            widgets.HBox([nuke_f3_c_intra, nuke_f3_c_cross]), \n',
    '            nuke_f3_b_run\n',
    '        ])\n',
    '        display(ui, nuke_f3_out)\n',
    '        \n',
    '        # 3. Initial generation ONLY if explicitly triggered to avoid multiples on start\n',
    '        with nuke_f3_out:\n',
    '            print("🚀 Initializing network...")\n',
    '            nuke_f3_run(0.35, -0.30, True, True)\n',
    '\n',
    'nuke_f3_render()\n'
]

code_cell = {
    'cell_type': 'code',
    'metadata': {},
    'execution_count': None,
    'outputs': [],
    'source': code_content
}

# Find Figure 2 code and insert after
insert_idx = -1
for i, cell in enumerate(nb['cells']):
    if 'figure_02' in "".join(cell.get('source', [])).lower():
        insert_idx = i + 1
        break

if insert_idx == -1:
    insert_idx = 10 

nb['cells'].insert(insert_idx, header)
nb['cells'].insert(insert_idx + 1, code_cell)

with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Successfully reconstructed Figure 3 section at index {insert_idx}.")
