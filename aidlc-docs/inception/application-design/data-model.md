# Modelo de datos

Dos lugares: el **contenido** (Markdown y YAML en GitHub, fuente de verdad) y el **estado de trabajo** (DynamoDB, operativo).

## 1. Contenido (GitHub)

### Documento — `contenido/documentos/<TIPO>/<ID>.md`

Metadatos al inicio (front matter YAML) = la ficha. El cuerpo sigue la plantilla del tipo. Un documento "propuesto" tiene ficha y cuerpo vacío.

```yaml
---
id: EST-INF-AWS-001
titulo: Landing zone en AWS
tipo: estandar                # fundacional | lineamiento | estandar (del perfil)
dominio: INF                  # código de un dominio aprobado
tecnologia: AWS               # solo estándares
padre: LIN-INF-001
relaciones:
  - {tipo: depende_de, destino: LIN-SEG-002}
  - {tipo: complementa, destino: EST-INF-AWS-002}
alcance:
  incluye: [OUs, SCPs, cuentas por entorno]
  excluye: [redes on-premise]
justificacion: Nombra un producto y fija valores verificables.
fuentes:
  - {titulo: AWS Well-Architected, ubicacion: "kb://aws-wa.pdf#p12"}
prioridad: alta               # alta | media | baja
estado: propuesto             # ciclo de vida del perfil
version: 0.0.0
redactado_con: {perfil: marco@1.0.0, plantilla: estandar@1.0.0}
dependencias_abiertas: false
proxima_revision: null
---
## Propósito
...
## Reglas
### EST-INF-AWS-001.R01 · DEBE
**Enunciado:** ...
**Justificación:** ...
**Cómo se verifica:** ...
**Fuentes:** ...
```

**Valores calculados (no se guardan, los calcula el núcleo):** impacto (nº de dependientes), nivel, enlaces de referencias.

### Regla (dentro del cuerpo)
| Campo | Formato |
|---|---|
| id | `<ID>.RNN` |
| nivel | DEBE / DEBERÍA / PUEDE (del perfil) |
| enunciado, justificación, verificación | texto |
| fuentes | lista de citas |
| referencias | IDs de documentos o reglas mencionados en el texto (`[[LIN-SEG-002.R03]]`) |

### Relación
`{origen, tipo, destino}` con tipo del perfil (`deriva_de` implícita por `padre`, `depende_de`, `complementa`, `reemplaza`).

### Perfil del marco — `contenido/marco/`
Un YAML por bloque (tipos y test, dominios, codificación, niveles, relaciones, ciclo de vida, versionado, estilo, glosario, fuentes, validación), `principios.md`, `contexto.yaml` (insumo de arquitectura), `plantillas/<tipo>.yaml`, `plantilla-word/corporativa.docx`. Versión del perfil: etiqueta `marco@x.y.z`.

### Pendientes fuera del MVP — `contenido/pendientes.yaml`
Temas que el test deja fuera (guías, procedimientos, catálogos), con motivo.

### Etiquetas de versión
`<ID>@x.y.z` por documento, `mapa@x.y.z` por mapa, `marco@x.y.z` por perfil.

## 2. Estado de trabajo (DynamoDB, una tabla)

Tabla única bajo demanda, clave `PK` + `SK`, un índice secundario `GSI1` para listar por estado.

| Entidad | PK | SK | Atributos principales | GSI1 |
|---|---|---|---|---|
| Ejecución | `RUN#<id>` | `META` | flujo, objetivo, estado (en curso, en revisión, detenida, terminada), costo, tokens, tope, PR, inicio, fin | `RUNS#<estado>` / fecha |
| Paso | `RUN#<id>` | `STEP#<n>` | agente, modelo, tokens, costo, duración, resumen, salida (o ruta en S3 si es grande) | — |
| Observación | `RUN#<id>` | `OBS#<n>` | origen (núcleo/validador/contraste), severidad (bloqueante/advertencia/info), documento, regla, mensaje, sugerencia, estado (abierta/resuelta) | `OBS#abierta` / documento |
| Aprobación | `DOC#<ID>` | `APR#<fecha>` | decisión, revisor (nombre), motivo, versión, commit, PR | — |
| Marca de revalidación | `DOC#<ID>` | `REVALIDAR` | causa (documento que cambió), fecha | `REVALIDAR` / fecha |
| Necesidad | `NEED#<id>` | `META` | texto, estructura, aclaraciones, clasificación, paquete | `NEEDS#<estado>` / fecha |
| Paquete | `PKG#<id>` | `META` | necesidad, rama, PR, documentos afectados, estado | `PKGS#<estado>` / fecha |
| Caso de prueba | `CASE#<id>` | `META` | tema, respuesta correcta (tipo, dominio, padre), origen (corrección de qué ejecución), fecha | — |
| Evaluación | `EVAL#<id>` | `META` | perfil/prompt evaluados, coincidencia total y por campo, nº de casos, aprobada | — |

## 3. Otros almacenes

| Almacén | Contenido |
|---|---|
| S3 `fuentes/` | PDFs subidos, documentos existentes, páginas descargadas de sitios aprobados |
| Bedrock KB + S3 Vectors | Índice de fuentes (colección de conocimiento y colección de existentes) |
| S3 Vectors `reglas` | Un vector por regla aprobada: id, documento, dominio, nivel, texto |
| S3 `publicaciones/<ID>/<version>/` | Word y PDF de cada versión |
| Parameter Store | Token de GitHub (SecureString), topes de costo, modelos por agente |
