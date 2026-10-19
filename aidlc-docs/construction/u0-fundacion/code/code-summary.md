# U0 Fundación — resumen de código

**Resultado:** 143 pruebas pasan (sin red ni costo), cobertura total 96 % y 95–98 % en `core/` (NFR-Q1). `ruff` sin observaciones; `mypy` sin errores (estricto en `core/`).

## Trazabilidad historia → código → pruebas

| Historia | Código | Pruebas |
|---|---|---|
| HU-0.1 Estructura del monorepo | `pyproject.toml`, `contenido/`, `src/documentador/`, `infra/`, `README.md` | `tests/unit/test_repo_structure.py` (BR-U0-31) |
| HU-0.2 Despliegue base con control de costo | `infra/app.py`, `infra/documentador_infra/base_stack.py`, `valores.py`, `infra/README.md` | `infra/tests/test_base_stack.py` (sin costo fijo, sin `*`, bucket privado y HTTPS, presupuesto con 4 avisos, tabla, parámetros) |
| HU-0.3 Perfil del marco inicial | `contenido/marco/*.yaml`, `principios.md`, `contexto.yaml` | `test_profile.py::test_real_profile_loads_with_pending_warnings` |
| HU-0.4 Plantillas por tipo | `contenido/marco/plantillas/`, `core/document.py`, `core/ids.py` | `tests/unit/test_document.py` (BR-U0-16 a 20) |
| HU-0.5 Validación del perfil e invariantes | `core/profile_models.py`, `core/profile.py`, `doc perfil validar` | `tests/unit/test_profile.py` (un caso por BR-U0-01 a 15), `test_cli.py` |
| HU-0.6 Conversión con la plantilla | `publish/word.py`, `publish/ejemplo.md`, plantilla genérica `plantilla-word/corporativa.docx`, `doc publicar` | `tests/unit/test_word.py` (BR-U0-27 a 30, incluye PDF real), `test_cli.py` |
| HU-0.7 Adaptador del repositorio | `adapters/repository.py`, `adapters/github.py` | `test_repository.py` (BR-U0-21 a 26), `test_github.py` (API simulada) |

**Soporte transversal (diseño NFR):** `common/errors.py`, `common/retry.py` (P4), `common/logging.py` (P7, P8), `config.py` (P2, P7), `cost/budget.py` (P1), `cost/routing.py` (P2), `adapters/state.py` (P10) — pruebas en `test_common.py`, `test_cost.py`, `test_state.py`, y `doc estado verificar` en `test_cli.py`.

## Ajustes respecto del diseño (registrados)

| Ajuste | Motivo |
|---|---|
| Parámetros extra `/documentador/tabla`, `/documentador/bucket` y `/documentador/github/rama` | La CLI necesita los nombres reales de la tabla y el bucket, y la rama base de GitHub (por defecto `main`) |
| El método `list` del repositorio se llama `list_files` | `list` tapaba al tipo `list` dentro de la clase (lo detectó mypy) |
| Los campos de una regla se separan con una línea en blanco | Sin ella, Word une los cuatro campos en un solo párrafo |
| La marca "Borrador" usa la forma `PowerPlusWaterMarkObject` | Es la estructura que escribe Word; con otro nombre LibreOffice no la dibuja en el PDF (verificado visualmente) |
| Sin función de vaciado automático del bucket | Evita crear una Lambda auxiliar; la guía indica vaciarlo antes de `cdk destroy` |
| La política de operador no incluye `kms:Decrypt` | El parámetro cifrado usa la llave administrada `aws/ssm`, que no requiere ese permiso |

## Pendiente fuera del código (etapa de build y pruebas)

- Desplegar `DocumentadorBase` en tu cuenta (guía en `infra/README.md`).
- Crear el token de GitHub y guardarlo en `/documentador/github/token`.
- `uv run doc estado verificar` con todo en ✓. La verificación de GitHub lee la rama `main`, que se crea al fusionar este trabajo.
- Probar `doc publicar --ejemplo --plantilla <corporativa.docx>` con la plantilla corporativa (F4=B).
- Revisar y aprobar el perfil del marco (`marco@1.0.0`) completando los `POR DEFINIR` obligatorios.
- BR-U0-32 (cambios solo de contenido no despliegan): hoy no hay despliegue automático, así que se cumple; se vuelve a comprobar en U4 al configurar Amplify.
