"""
Centralized parameter mappings for the Tomato Salt Tolerance Analysis.
Defines biological levels (pathways) and responsiveness categories.
"""

# Mapping parameters to Biological Levels (used in Fig 1 and Fig 3)
PARAMETER_LEVELS = {
    # Hormonal
    'ABA (ng/mg)': 'hormonal',
    'IAA (ng/mg)': 'hormonal',
    'GA4 (ng/mg)': 'hormonal',
    'SA (ng/mg)': 'hormonal',
    'JA (ng/mg)': 'hormonal',
    'Z (ng/mg)': 'hormonal',
    'Melatonin (ng/mg)': 'hormonal',
    'Metatopolin (ng/mg)': 'hormonal',
    
    # Metabolic
    'Osmolytes (osm/kg)': 'metabolic',
    'Phenols (mg/g FW)': 'metabolic',
    'Flavonoids (mg/g FW)': 'metabolic',
    'Total chlorophyll (μg/g FW)': 'metabolic',
    
    # Ionic/Osmotic
    'Na/K ratio leaves': 'ionic_osmotic',
    'Na/K ratio roots': 'ionic_osmotic',
    'Electrolytic leakage (μS/cm)': 'ionic_osmotic',
    'Relative water content (%)': 'ionic_osmotic',
    
    # Leaf Functionality
    'Fv/Fm': 'leaf_functionality',
    'Stomatal conductance (μmol/sec)': 'leaf_functionality',
    
    # Phenological
    'Flowering (trusses number)': 'phenological',
    'Fruit set (trusses number)': 'phenological',
    'Trusses maturing (number)': 'phenological',
    'Cumulative floral truss length (cm)': 'phenological',
    'Days_to_next_phase_from_prev_start': 'phenological',
    'Days_to_next_phase_from_time_0': 'phenological',
    
    # Morphological
    'Main shoot height (cm)': 'morphological',
    'Main shoot nodes (number)': 'morphological',
    'Leaves surface (cm²)': 'morphological',
    'Total fresh weight (g)': 'morphological',
    'Total dry weight (g)': 'morphological',
    
    # Quality
    'fresh weight 10 fruits (g)': 'quality',
    'Fruits dry weight (g)': 'quality',
    'Fruits soluble solids (°brix)': 'quality'
}

# Mapping parameters to Responsiveness Categories (used in Fig 6 and Fig 7)
PARAMETER_CATEGORIES = {
    # Performance Maintenance
    'Total dry weight (g)': 'Performance Maintenance',
    'fresh weight 10 fruits (g)': 'Performance Maintenance',
    'Fruit set (trusses number)': 'Performance Maintenance',
    'Main shoot height (cm)': 'Performance Maintenance',
    'Flowering (trusses number)': 'Performance Maintenance',
    'Leaves surface (cm²)': 'Performance Maintenance',
    'Days_to_next_phase_from_prev_start': 'Performance Maintenance',
    'Days_to_next_phase_from_time_0': 'Performance Maintenance',
    
    # Physiological Stability
    'Fv/Fm': 'Physiological Stability',
    'Total chlorophyll (μg/g FW)': 'Physiological Stability',
    'Relative water content (%)': 'Physiological Stability',
    'Stomatal conductance (μmol/sec)': 'Physiological Stability',
    
    # Stress Marker Response
    'Electrolytic leakage (μS/cm)': 'Stress Marker Response',
    'Na/K ratio leaves': 'Stress Marker Response',
    'Na/K ratio roots': 'Stress Marker Response',
    'ABA (ng/mg)': 'Stress Marker Response',
    'Osmolytes (osm/kg)': 'Stress Marker Response'
}

# English translations for Pathways/Levels
LEVEL_TRANSLATIONS = {
    'hormonal': 'Hormonal System',
    'metabolic': 'Primary/Secondary Metabolism',
    'ionic_osmotic': 'Osmotic Regulation/Ionic Balance',
    'leaf_functionality': 'Leaf functionality',
    'phenological': 'Temporal Phenological Traits',
    'morphological': 'Morphology and Growth',
    'quality': 'Fruit Quality'
}
