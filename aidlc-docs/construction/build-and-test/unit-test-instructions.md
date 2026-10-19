# Pruebas unitarias (U0)

Sin red, sin credenciales y sin costo: GitHub se simula con respuestas HTTP, AWS con `moto`.

```bash
uv run pytest                                          # 144 pruebas (incluye las de la plantilla CDK)
uv run pytest --cov=documentador --cov-report=term     # cobertura
```

| Archivo | Qué prueba |
|---|---|
| `tests/unit/test_profile.py` | Carga del perfil y un caso por regla BR-U0-01 a 15 |
| `tests/unit/test_document.py` | Ficha, secciones, reglas, IDs, ida y vuelta estable (BR-U0-16 a 20) |
| `tests/unit/test_repository.py`, `test_github.py` | Contrato del repositorio y convenciones de Git (BR-U0-21 a 26) |
| `tests/unit/test_word.py` | Plantilla, marca Borrador, enlaces, PDF (BR-U0-27 a 30); se omiten si faltan Pandoc o LibreOffice |
| `tests/unit/test_repo_structure.py` | `contenido/` sin código (BR-U0-31) |
| `tests/unit/test_common.py`, `test_cost.py`, `test_state.py`, `test_cli.py` | Reintentos, secretos, configuración, presupuesto, estado y comandos |
| `infra/tests/test_base_stack.py` | Sin costo fijo, sin `*`, bucket privado y HTTPS, presupuesto con 4 avisos, tabla y parámetros |

Criterios: todas pasan; cobertura de `core/` ≥ 90 %.
