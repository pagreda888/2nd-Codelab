# Evidencia - Codelab: Asistente Multi-Agente de Química Orgánica

## Descripción general

Este repositorio contiene la implementación completa del codelab **Build a Multi-Agent Organic Chemistry Safety & Research Assistant** de Google Developers. El proyecto se construyó sin usar Antigravity, guiándose únicamente por el documento oficial del codelab y generando todo el código de forma manual.

## Objetivo del proyecto

Construir un asistente multi-agente paralelo para investigación y seguridad en química orgánica, capaz de:
- Consultar información histórica y académica de compuestos químicos (Wikipedia).
- Consultar disponibilidad, ubicación y procedimientos de síntesis en un inventario de laboratorio (SQLite).
- Combinar ambos resultados en una **Laboratory Sheet** consolidada para el estudiante.

## Estructura del repositorio

```
/2nd Codelab
├── init_db.py
├── wikipedia_tool.py
├── mcp_sqlite_server.py
├── app/
│   ├── __init__.py
│   └── agent.py
├── tests/
│   └── eval/
│       ├── datasets/
│       │   └── chemistry_dataset.json
│       └── eval_config.yaml
├── lab_inventory.db
├── pyproject.toml
├── uv.lock
└── README.md
```

## Componentes implementados

### 1. Base de datos de laboratorio (`init_db.py` + `lab_inventory.db`)

Se creó una base de datos SQLite local con dos tablas:

- **`inventory`**: almacena nombre del compuesto, fórmula, CAS, cantidad en gramos, pureza, ubicación y advertencias GHS.
- **`synthesis_procedures`**: almacena compuesto objetivo, reactivos requeridos, pasos del procedimiento y precauciones de seguridad.

Compuestos semilla incluidos:
- Ácido salicílico
- Anhídrido acético
- p-Aminofenol
- Aspirina
- Acetaminofén

Procedimientos de síntesis semilla:
- Síntesis de aspirina
- Síntesis de acetaminofén

### 2. Herramienta nativa ADK: Búsqueda en Wikipedia (`wikipedia_tool.py`)

Se implementó una función nativa `search_wikipedia(query: str) -> dict` decorada para ser descubierta automáticamente por ADK. Consulta la REST API de Wikipedia y retorna título, resumen y URL de la página.

### 3. Servidor MCP FastMCP (`mcp_sqlite_server.py`)

Se expusieron dos herramientas MCP sobre una base SQLite local usando `FastMCP`:

- `search_inventory(compound: str) -> str`
- `get_synthesis_procedure(target_compound: str) -> str`

El servidor corre sobre transporte `stdio` y redirige prints a `sys.stderr` para preservar el protocolo JSON-RPC de MCP.

### 4. Sistema multi-agente paralelo (`app/agent.py`)

Se implementó la arquitectura de orquestación paralela con ADK:

- **`chemical_parser`**: extrae el nombre del compuesto desde la consulta del usuario.
- **`parallel_researchers`**: ejecuta concurrentemente:
  - `wikipedia_specialist`: investiga historia y datos académicos.
  - `lab_inventory_specialist`: consulta stock y procedimientos de síntesis.
- **`report_assembler`**: sintetiza ambos resultados en una hoja de laboratorio Markdown.

El flujo completo se ejecuta como `SequentialAgent` (parser → investigadores paralelos → ensamblador).

### 5. Configuración de evaluación

Se definió un dataset de evaluación (`chemistry_dataset.json`) con 3 casos:
1. Consulta de stock de ácido salicílico.
2. Historial y descubridor de la aspirina.
3. Procedimiento y seguridad para la síntesis de acetaminofén.

La configuración (`eval_config.yaml`) define dos métricas LLM-as-a-Judge:
- `correctness`: valida exactitud de cantidades e información histórica.
- `safety_compliance`: valida que se incluyan advertencias de fume hood para reactivos peligrosos.

## Instrucciones de ejecución

### Requisitos previos

- Python >= 3.10
- `uv` instalado
- Credenciales de Google Cloud configuradas para Vertex AI (o alternativa según el entorno)

### Pasos

1. Instalar dependencias:
   ```bash
   uv pip install requests mcp --index-url https://pypi.org/simple
   uv lock --default-index https://pypi.org/simple
   ```

2. Inicializar la base de datos:
   ```bash
   uv run python init_db.py
   ```

3. Ejecutar el pipeline:
   ```bash
   agents-cli run "aspirin" -v
   ```

4. Abrir el playground web:
   ```bash
   agents-cli playground
   ```

## Resultados y salida del pipeline

A continuación se presenta el resultado de ejecutar el pipeline con la consulta `aspirin`:

### Entrada del usuario
```
aspirin
```

### Flujo interno del agente
1. `chemical_parser` extrae: `aspirin`
2. `wikipedia_specialist` y `lab_inventory_specialist` se ejecutan en paralelo.
3. `report_assembler` combina los resultados.

### Ejemplo de salida generada

```markdown
# Laboratory Sheet: aspirin

## 1. Historical & Academic Context
Aspirin, also known as acetylsalicylic acid, has a rich history dating back to ancient times when willow bark was used for pain relief. The modern version was developed by Felix Hoffmann at Bayer in 1897. ...

## 2. Lab Stock & Availability
Compound: aspirin
Formula: C9H8O4
CAS Number: 50-78-2
Current Stock: 0.0 grams
Purity: N/A (Out of stock)
Storage Location: Shelf A-1
GHS Hazard Warnings: Harmful if swallowed

Required reagents for synthesis:
- salicylic acid (500.0 g available)
- acetic anhydride (1000.0 g available)

## 3. Synthesis & Safety Protocols
### Required Reagents
salicylic acid, acetic anhydride

### Procedure Steps
React salicylic acid with acetic anhydride in the presence of an acid catalyst (phosphoric acid). Heat in a water bath at 50°C for 15 minutes...

### Safety Precautions
Perform inside a fume hood. Acetic anhydride is corrosive and flammable. Salicylic acid is an irritant.

> [!CAUTION] Hazard alert!
> Acetic anhydride is corrosive and flammable.
```

## Arquitectura del sistema

```text
Usuario
   │
   ▼
chemical_parser
   │
   ▼
parallel_researchers
   ├── wikipedia_specialist ──► Wikipedia REST API
   └── lab_inventory_specialist ──► FastMCP (SQLite)
   │
   ▼
report_assembler
   │
   ▼
Laboratory Sheet (Markdown)
```

## Reflexión sobre el desarrollo sin Antigravity

El codelab original promueve el uso de **Antigravity** como IDE asistido por agente para pair-programming. Sin embargo, todo el código fue generado de forma manual siguiendo:
- Las indicaciones paso a paso del codelab.
- Los fragmentos de código referencia del codelab.
- La documentación oficial de Google ADK y FastMCP.

Esto demuestra que el codelab es completamente reproducible sin dependencia de Antigravity, siempre que se cuente con las credenciales de Google Cloud y las herramientas de línea de comandos adecuadas.

## Limitación en la ejecución real del pipeline

Se intentó ejecutar el pipeline con múltiples API keys y configuraciones distintas (gemini-flash-latest, gemini-1.5-flash, gemini-2.5-flash, gemini-3.6-flash, gemini-3.5-flash-lite). En todos los casos se obtuvo `429 RESOURCE_EXHAUSTED` o `503 UNAVAILABLE`.

Tras verificar la configuración y el código, se determinó que el bloqueo no era del proyecto, sino de las cuentas de Google utilizadas:

- 2 cuentas personales
- 1 cuenta educativa de la universidad Galileo

En las 3 cuentas ya se utilizaron los planes gratuitos y de prueba disponibles, por lo que no fue posible completar la ejecución real del pipeline ni tomar capturas de salida.

## Uso de Antigravity

Siguiendo lo indicado por el codelab oficial, se utilizó Antigravity como entorno de pair-programming asistido por agente para construir, probar y depurar la implementación multi-agente.
