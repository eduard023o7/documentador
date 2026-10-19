# U0 · Reglas de negocio

Cada regla tiene ID `BR-U0-NN` para trazarla en código y pruebas.

## Perfil del marco (HU-0.3, HU-0.5)

| ID | Regla | Si no se cumple |
|---|---|---|
| BR-U0-01 | Todos los archivos del perfil existen y tienen `version_esquema` soportada | Error: archivo faltante o versión no soportada |
| BR-U0-02 | Cada archivo cumple su esquema (campos obligatorios, tipos, valores permitidos) | Error con archivo, campo y motivo |
| BR-U0-03 | Códigos de tipo y de dominio son únicos, en mayúsculas, de 2 a 6 caracteres | Error |
| BR-U0-04 | `padre_permitido` de cada tipo es `dominio` o la clave de otro tipo existente; no hay ciclos entre tipos | Error |
| BR-U0-05 | Cada resultado del test de clasificación es una clave de tipo o `fuera_mvp` | Error |
| BR-U0-06 | Los patrones de `codificacion.yaml` usan solo las variables `{dominio}`, `{tecnologia}`, `{n}`, `{documento}` y generan IDs únicos por tipo | Error |
| BR-U0-07 | `transiciones` solo usa estados declarados; `aprobado` es alcanzable desde `propuesto` | Error |
| BR-U0-08 | Cada plantilla referencia secciones del catálogo; las secciones opcionales por dominio solo vienen del catálogo | Error |
| BR-U0-09 | La plantilla de un tipo con `requiere_tecnologia: true` incluye `especificacion` como obligatoria | Error |
| BR-U0-10 | Cada criterio de `validacion.yaml` tiene severidad `bloqueante`, `advertencia` o `info` | Error |
| BR-U0-11 | Los valores `# POR DEFINIR` se permiten en un perfil en borrador; impiden etiquetar `marco@x.y.z` como aprobado | Advertencia en borrador; error al aprobar |

## Invariantes no configurables (RF-10)

No existen como campos del perfil; el núcleo los aplica siempre. Si el perfil intenta declararlos (p. ej. `padres_multiples: true`), se rechaza.

| ID | Invariante |
|---|---|
| BR-U0-12 | Cada documento tiene exactamente un padre |
| BR-U0-13 | Los IDs de documento y de regla son únicos en todo el mapa y nunca se reutilizan, ni siquiera tras quedar obsoletos |
| BR-U0-14 | Cada tema vive en un solo documento (lo verifica la coherencia en U1/U2; en U0 solo se declara) |
| BR-U0-15 | Nada se fusiona a `main` en `contenido/` sin una aprobación con nombre de revisor |

## Documento y regla (HU-0.4)

| ID | Regla |
|---|---|
| BR-U0-16 | El archivo se llama `<ID>.md` y está en la carpeta del código de su tipo |
| BR-U0-17 | El front matter cumple el esquema de ficha; `tecnologia` solo existe si el tipo la requiere |
| BR-U0-18 | Un documento `propuesto` puede tener el cuerpo vacío; desde `en_validacion` debe tener todas las secciones obligatorias en el orden de la plantilla |
| BR-U0-19 | Cada regla tiene encabezado `### <ID>.RNN · <NIVEL>` con nivel declarado, y los campos Enunciado, Justificación, Cómo se verifica y Fuentes |
| BR-U0-20 | Leer y volver a escribir un documento sin cambios produce exactamente el mismo texto (ida y vuelta estable, para que Git no muestre cambios falsos) |

## Repositorio y Git (HU-0.7)

| ID | Regla |
|---|---|
| BR-U0-21 | Ramas de propuesta: `propuesta/<flujo>-<id>` (flujo: mapa, documento, necesidad, perfil) |
| BR-U0-22 | Commits de la plataforma: autor "Admin documentador"; mensaje en español con resumen, motivo y, si es aprobación, línea `Revisado-por: <nombre>` |
| BR-U0-23 | Una aprobación sin nombre de revisor no se procesa |
| BR-U0-24 | Etiquetas: `<ID>@x.y.z`, `mapa@x.y.z`, `marco@x.y.z`; una etiqueta existente nunca se mueve |
| BR-U0-25 | El token de GitHub solo se lee de Parameter Store (o de una variable de entorno en desarrollo local) y nunca se escribe en logs |
| BR-U0-26 | El adaptador solo escribe dentro de `contenido/`; cualquier otra ruta se rechaza |

## Conversión a Word y PDF (HU-0.6)

| ID | Regla |
|---|---|
| BR-U0-27 | Word se genera desde Markdown con la plantilla corporativa como documento de referencia de estilos |
| BR-U0-28 | Todo documento no aprobado lleva marca de agua "Borrador" en cada página |
| BR-U0-29 | PDF se genera desde el Word, nunca directo desde Markdown, para que ambos se vean igual |
| BR-U0-30 | Las referencias `[[ID]]` se convierten en enlaces en Word y PDF (en U0 se prueba con enlaces a la ruta del documento; en U3 apuntan a la versión publicada) |

## Estructura del monorepo (HU-0.1)

| ID | Regla |
|---|---|
| BR-U0-31 | `contenido/` no contiene código ejecutable (solo `.md`, `.yaml`, `.docx`) |
| BR-U0-32 | Un cambio solo en `contenido/` no dispara construcción ni despliegue |
