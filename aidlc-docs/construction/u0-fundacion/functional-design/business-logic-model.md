# U0 · Modelo de lógica

## 1. Carga y validación del perfil — `load_profile(path)` (HU-0.5)

```
1. Leer cada archivo esperado de contenido/marco/ (BR-U0-01)
2. Validar cada uno contra su esquema Pydantic (BR-U0-02), acumulando errores
3. Validaciones cruzadas: códigos únicos, padres de tipo, test, patrones de ID,
   transiciones, plantillas vs catálogo (BR-U0-03 a 10)
4. Rechazar claves que intenten declarar invariantes (BR-U0-12 a 15)
5. Recolectar valores "# POR DEFINIR" como advertencias (BR-U0-11)
6. Si hay errores → ProfileError con la lista completa (archivo, campo, motivo)
   Si no → Profile inmutable + lista de advertencias
```
Se reportan **todos** los errores juntos, no solo el primero, para corregir en una pasada.

**CLI:** `doc perfil validar [--para-aprobar]` imprime errores y advertencias en español; código de salida 0 si es válido. Con `--para-aprobar`, los `# POR DEFINIR` cuentan como error.

## 2. Documentos — `parse_document` / `render_document` (HU-0.4)

```
parse:  separar front matter y cuerpo → validar ficha (BR-U0-17)
        → dividir el cuerpo por "## " en secciones según títulos del catálogo
        → en la sección de reglas, dividir por "### <ID>.RNN · NIVEL" y leer sus campos (BR-U0-19)
        → extraer referencias [[...]]
render: ficha en orden de campos fijo → secciones en el orden de la plantilla → reglas en orden de ID
```
Prueba de ida y vuelta para cada documento de ejemplo (BR-U0-20).

## 3. Adaptador de GitHub — `GitHubRepository` (HU-0.7)

Usa la API REST de GitHub (sin clonar), con el token de Parameter Store.

| Operación | Comportamiento |
|---|---|
| `read`, `list` | Lee contenido de una rama (por defecto `main`) |
| `create_branch` | Crea `propuesta/…` desde `main`; error si ya existe |
| `commit` | Un commit con varios archivos (crear, modificar o borrar) vía la API de árboles de Git; valida rutas dentro de `contenido/` (BR-U0-26); aplica autor y formato de mensaje (BR-U0-22) |
| `open_pull_request` | Título y cuerpo en español (resumen, observaciones, costo) |
| `review_comments` | Comentarios por línea del PR con archivo y línea |
| `merge` | Fusión de tipo "squash" con el mensaje de aprobación (incluye `Revisado-por`) |
| `tag` | Etiqueta ligera; error si ya existe (BR-U0-24) |

Errores de GitHub (permisos, conflicto, límite de uso) se convierten en mensajes claros y no dejan cambios a medias: si falla un paso de una aprobación, la rama queda intacta y se puede reintentar.

Para pruebas existe `InMemoryRepository` con el mismo contrato.

## 4. Conversión a Word y PDF (HU-0.6)

```
render_docx(doc, draft):
  1. Markdown del documento → pasar [[ID]] a enlaces
  2. Pandoc: markdown → docx con --reference-doc = corporativa.docx
     (o corporativa-borrador.docx si draft)
  3. corporativa-borrador.docx se deriva una vez de corporativa.docx agregando
     la marca de agua "Borrador" en los encabezados (python-docx)
render_pdf(docx): LibreOffice en modo sin pantalla → PDF
```
En U0 se ejecuta localmente (`doc publicar --ejemplo`) sobre un documento de ejemplo con títulos, tablas, listas, reglas y referencias. En U3 se empaqueta en la Lambda contenedor.

## 5. Contenido inicial del perfil (HU-0.3)

Lo redacto yo a partir del doc de definición, con F1=A, F2=B, F3=A, y lo entrego como pull request para tu revisión. Al aprobarlo con tu nombre se etiqueta `marco@1.0.0` (antes deben resolverse los `# POR DEFINIR` obligatorios; los opcionales, como el glosario, pueden quedar para después marcándolos como opcionales).

## 6. Despliegue base (HU-0.2)

Se detalla en el diseño de infraestructura de U0. Funcionalmente: un comando `cdk deploy` crea presupuesto con alertas, bucket S3 privado, tabla DynamoDB, parámetro del token y rol de ejecución local con permisos mínimos.

## Cobertura

| Historia | Dónde |
|---|---|
| HU-0.1 | BR-U0-31, 32; `repo-structure.md` |
| HU-0.2 | §6 (detalle en diseño de infraestructura) |
| HU-0.3 | §5; `domain-entities.md` §1 |
| HU-0.4 | §2; BR-U0-16 a 20; plantillas en `domain-entities.md` |
| HU-0.5 | §1; BR-U0-01 a 15 |
| HU-0.6 | §4; BR-U0-27 a 30 |
| HU-0.7 | §3; BR-U0-21 a 26 |
