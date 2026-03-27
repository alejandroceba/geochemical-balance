# Geochemical Balance Analyzer

## English

### Overview
A Python-based analytical pipeline for water geochemistry analysis. This project processes water sample data to calculate ionic balances, molecular weights, and charge-balance errors for quality assessment.

### Features
- **Data Ingestion**: Load water sample data (17 samples, 11 ion species)
- **Chemistry Constants**: IUPAC-standard atomic weights and ionic charges
- **Unit Conversions**: 
  - mg/dm³ → mmol/dm³ (via molar mass division)
  - mmol/dm³ → meq/dm³ (via ionic charge weighting)
- **Ionic Aggregation**: Sum cation and anion contributions per sample
- **Charge-Balance Error (CBE)**: Calculate CBE% = ((ΣCations - ΣAnions) / (ΣCations + ΣAnions)) × 100
- **Quality Flagging**: Pass/fail assessment based on ±5% CBE threshold

### Project Structure
```
geochemical-balance/
├── notebooks/
│   └── 001_balance.ipynb          # Main analysis notebook
├── data/
│   ├── muestras_sonora.csv        # Input: 17 water samples (11 ion species)
│   ├── geochem_ocr_raw.csv        # Standardized input table
│   ├── geochem_molecular_weights.csv
│   ├── geochem_mmol_dm3.csv
│   ├── geochem_meq_dm3.csv
│   ├── geochem_cation_sum_meq_dm3.csv
│   ├── geochem_anion_sum_meq_dm3.csv
│   ├── geochem_charge_balance_error_percent.csv
│   └── geochem_charge_balance_flag_5pct.csv
├── main.py
├── pyproject.toml
└── README.md
```

### Ion Species Covered
**Cations**: Na⁺, K⁺, Ca²⁺, Mg²⁺, Li⁺  
**Anions**: Cl⁻, F⁻, SO₄²⁻, HCO₃⁻, CO₃²⁻, PO₄³⁻

### Requirements
- Python 3.8+
- pandas
- numpy
- rapidocr-onnxruntime (optional, for OCR preprocessing)
- opencv-python (optional, for image handling)

### Usage
Open `notebooks/001_balance.ipynb` in Jupyter and run all cells sequentially. The pipeline:
1. Loads standardized data from `data/geochem_ocr_raw.csv`
2. Computes molecular weights for all species
3. Converts concentration units through mmol and meq stages
4. Aggregates ionic contributions
5. Calculates charge-balance metrics
6. Exports all intermediate and final results as CSV files

### Output Interpretation
- **CBE Range**: -1.15% to +9.29% for this dataset
- **Pass Threshold**: |CBE| ≤ ±5% (most samples pass; 6 marginal cases)
- **Quality Metrics**: Realistic for spring/groundwater (~300–320 meq/dm³ per sample)

### References
- Charge-balance calculations follow IAH (International Association of Hydrogeologists) guidelines
- Atomic weights: IUPAC 2021 standard
- Ionic charges: Standard hydrochemistry reference values

---

## Español

### Descripción General
Una tubería analítica basada en Python para análisis de geoquímica de aguas. Este proyecto procesa datos de muestras de agua para calcular balances iónicos, pesos moleculares y errores de balance de carga para evaluación de calidad.

### Características
- **Ingesta de Datos**: Carga de datos de muestras de agua (17 muestras, 11 especies iónicas)
- **Constantes Químicas**: Pesos atómicos IUPAC estándar y cargas iónicas
- **Conversiones de Unidades**: 
  - mg/dm³ → mmol/dm³ (mediante división por masa molar)
  - mmol/dm³ → meq/dm³ (mediante ponderación de carga iónica)
- **Agregación Iónica**: Suma de contribuciones de cationes y aniones por muestra
- **Error de Balance de Carga (CBE)**: Cálculo CBE% = ((ΣCationes - ΣAniones) / (ΣCationes + ΣAniones)) × 100
- **Indicadores de Calidad**: Evaluación aprobado/reprobado basada en umbral CBE ±5%

### Estructura del Proyecto
```
geochemical-balance/
├── notebooks/
│   └── 001_balance.ipynb          # Notebook de análisis principal
├── data/
│   ├── muestras_sonora.csv        # Entrada: 17 muestras de agua (11 especies iónicas)
│   ├── geochem_ocr_raw.csv        # Tabla de entrada estandarizada
│   ├── geochem_molecular_weights.csv
│   ├── geochem_mmol_dm3.csv
│   ├── geochem_meq_dm3.csv
│   ├── geochem_cation_sum_meq_dm3.csv
│   ├── geochem_anion_sum_meq_dm3.csv
│   ├── geochem_charge_balance_error_percent.csv
│   └── geochem_charge_balance_flag_5pct.csv
├── main.py
├── pyproject.toml
└── README.md
```

### Especies Iónicas Cubiertas
**Cationes**: Na⁺, K⁺, Ca²⁺, Mg²⁺, Li⁺  
**Aniones**: Cl⁻, F⁻, SO₄²⁻, HCO₃⁻, CO₃²⁻, PO₄³⁻

### Requisitos
- Python 3.8+
- pandas
- numpy
- rapidocr-onnxruntime (opcional, para preprocesamiento OCR)
- opencv-python (opcional, para manejo de imágenes)

### Uso
Abra `notebooks/001_balance.ipynb` en Jupyter y ejecute todas las celdas secuencialmente. La tubería:
1. Carga datos estandarizados de `data/geochem_ocr_raw.csv`
2. Calcula pesos moleculares para todas las especies
3. Convierte unidades de concentración a través de etapas mmol y meq
4. Agrega contribuciones iónicas
5. Calcula métricas de balance de carga
6. Exporta todos los resultados intermedios y finales como archivos CSV

### Interpretación de Resultados
- **Rango CBE**: -1.15% a +9.29% para este conjunto de datos
- **Umbral de Aprobación**: |CBE| ≤ ±5% (la mayoría de muestras aprobadas; 6 casos marginales)
- **Métricas de Calidad**: Realistas para agua de manantial/subterránea (~300–320 meq/dm³ por muestra)

### Referencias
- Los cálculos de balance de carga siguen directrices IAH (Asociación Internacional de Hidrogeólogos)
- Pesos atómicos: estándar IUPAC 2021
- Cargas iónicas: Valores de referencia estándar de geoquímica de aguas

---

**License**: MIT  
**Author**: Geochemical Analysis Team  
**Last Updated**: March 26, 2026
