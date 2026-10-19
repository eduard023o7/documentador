# U0 Fundación — plan de generación de código

**Base aprobada:** diseño funcional (BR-U0-01 a 32), requisitos y diseño NFR, diseño de infraestructura. Datos de despliegue: I1=A (correo de tu cuenta, se pasa como parámetro al desplegar; no se guarda en el repositorio), I2=B (usuario IAM con llaves).

Cada paso termina con sus pruebas pasando. Al final se ejecutan `ruff`, `mypy` y `pytest` completos.

## Pasos

### 1. Proyecto y herramientas (HU-0.1)
- [x] `pyproject.toml` (Python ≥ 3.12, dependencias fijadas, comando `doc`), configuración de ruff, mypy y pytest
- [x] Estructura `src/documentador/` con subpaquetes vacíos según `repo-structure.md`
- [x] `.gitignore`, `README.md` actualizado (qué va en cada carpeta)
- [x] Prueba BR-U0-31: `contenido/` no contiene archivos ejecutables

### 2. Utilidades comunes (P4, P7, P8)
- [x] `common/errors.py`: errores con mensaje en español y acción sugerida
- [x] `common/retry.py`: `with_retries` (solo errores transitorios) + pruebas
- [x] `common/logging.py`: registro estructurado y filtro de tokens de GitHub + pruebas
- [x] `config.py`: `Settings` desde Parameter Store, `config/local.yaml` y variables de entorno, con caché + pruebas (moto)

### 3. Núcleo: perfil del marco (HU-0.3, HU-0.5)
- [x] `core/profile_models.py`: esquemas Pydantic de los 11 YAML, plantillas y catálogo
- [x] `core/profile.py`: `load_profile` con validaciones cruzadas BR-U0-01 a 11, invariantes BR-U0-12 a 15, errores acumulados y advertencias `# POR DEFINIR`
- [x] Pruebas: perfil válido; un caso por cada regla BR-U0-01 a 15

### 4. Núcleo: documentos y reglas (HU-0.4)
- [x] `core/document.py`: `Ficha`, `Rule`, `Document`; `parse_document`, `render_document`, `extract_references`
- [x] `core/ids.py`: formateo y validación de IDs según `codificacion.yaml`
- [x] Pruebas: BR-U0-16 a 20, incluida la ida y vuelta estable

### 5. Contenido inicial del marco (HU-0.3, F1–F3)
- [x] `contenido/marco/*.yaml`, `principios.md`, `contexto.yaml`, plantillas y catálogo con los valores del doc; `# POR DEFINIR` donde falte
- [x] `contenido/documentos/{FUN,LIN,EST}/` vacías y `contenido/pendientes.yaml`
- [x] Documento de ejemplo para pruebas en `tests/fixtures/` (no en `contenido/`)
- [x] Prueba: el perfil real carga sin errores (con advertencias de borrador)

### 6. Costo y enrutamiento de modelos (P1, P2)
- [x] `cost/budget.py`: `Budget`, `BudgetExceeded`, cálculo con tabla de precios (incluye caché)
- [x] `cost/routing.py`: `ModelConfig`, `model_for`
- [x] Pruebas: cobro, tope, comprobación previa del peor caso

### 7. Adaptadores (HU-0.7, P10)
- [x] `adapters/repository.py`: interfaz `ContentRepository` + `InMemoryRepository`
- [x] `adapters/github.py`: `GitHubRepository` (API REST con httpx: leer, listar, rama, commit de varios archivos, PR, comentarios, fusión, etiqueta), reglas BR-U0-21 a 26
- [x] `adapters/state.py`: interfaz `StateStore` + implementación DynamoDB + en memoria
- [x] Pruebas: contrato común para ambas implementaciones del repositorio; GitHub con respuestas HTTP simuladas; DynamoDB con moto

### 8. Conversión a Word y PDF (HU-0.6)
- [x] `publish/word.py`: referencias `[[ID]]` → enlaces, Pandoc con documento de referencia, derivación de la plantilla "Borrador" con python-docx, PDF con LibreOffice
- [x] Plantilla genérica en `contenido/marco/plantilla-word/corporativa.docx` (F4=B; se reemplaza por la corporativa)
- [x] Pruebas: el Word usa los estilos de la plantilla, lleva la marca en borrador, tiene enlaces; el PDF se genera (se omiten si no hay Pandoc/LibreOffice)

### 9. CLI (HU-0.5, HU-0.6)
- [x] `cli/main.py` con Typer: `doc perfil validar [--para-aprobar]`, `doc publicar --ejemplo`, `doc estado verificar`
- [x] Pruebas de cada comando (salida y código de retorno)

### 10. Infraestructura (HU-0.2)
- [x] `infra/` con CDK v2 en Python: stack `DocumentadorBase` (presupuesto, S3, DynamoDB, parámetros, política operador)
- [x] `infra/tests/test_base_stack.py`: sin costo fijo, sin `*`, bucket privado y HTTPS, presupuesto con tres avisos
- [x] `infra/README.md`: guía de despliegue para usuario IAM con llaves (I2=B), creación del token y del parámetro SecureString

### 11. Cierre
- [x] `ruff`, `mypy` (estricto en `core/`), `pytest` con cobertura ≥ 90 % en `core/`
- [x] Resumen de código en `construction/u0-fundacion/code/code-summary.md` con trazabilidad historia → archivos → pruebas
- [x] Presentar para aprobación (aprobado el 2026-10-19)

**Fuera de este plan:** desplegar en tu cuenta, crear el token y probar con la plantilla corporativa (los haces tú en la etapa de build y pruebas, con la guía).
