# documentador — reglas de trabajo con AI-DLC

Este repositorio se construye con **AI-DLC (AI-Driven Development Life Cycle)**: la IA propone y ejecuta, las personas deciden en cada puerta. El insumo de partida es la definición del MVP en `aidlc-docs/inception/requirements/fuente-definicion-mvp.md` (copia del doc "Definición del MVP: plataforma de lineamientos y estándares").

Idioma de trabajo: español (documentos, preguntas, mensajes de commit). Identificadores de código en inglés salvo que se decida otra cosa.

## Fases y etapas

**INCEPTION — qué construimos y por qué**
1. Detección del workspace (siempre)
2. Ingeniería inversa (solo si hay código previo; hoy no aplica: repo vacío)
3. Análisis de requisitos (siempre; profundidad adaptativa)
4. Historias de usuario (condicional)
5. Planificación del flujo de trabajo (siempre): decide qué etapas de Construction se ejecutan
6. Diseño de aplicación (condicional): componentes, servicios, métodos
7. Generación de unidades de trabajo (condicional): descomposición en unidades construibles

**CONSTRUCTION — cómo, por unidad de trabajo**
1. Diseño funcional · 2. Requisitos no funcionales · 3. Diseño NFR · 4. Diseño de infraestructura (cada uno condicional)
5. Generación de código (siempre: primero plan con checkboxes, luego código)
6. Build y pruebas (siempre)

**OPERATIONS** — despliegue y operación (fuera del alcance inicial).

## Reglas

- **Una etapa a la vez.** Al terminar cada etapa se presenta el resultado y se espera aprobación explícita antes de seguir. Nunca se avanza por suposición.
- **Preguntas en archivo.** Las dudas se escriben en un `.md` con opciones A/B/C…, una opción "X) Otro" y una línea `[Answer]:` para responder. Si una respuesta es ambigua o contradictoria, se hace una pregunta de seguimiento antes de seguir.
- **Planes con checkboxes.** Todo plan usa `- [ ]` y se marca `- [x]` en cuanto el paso se completa, en la misma interacción.
- **Estado.** `aidlc-docs/aidlc-state.md` refleja siempre la etapa actual y lo completado.
- **Auditoría.** `aidlc-docs/audit.md` registra cada entrada del usuario (textual) y cada aprobación, con fecha. Solo se agrega al final; nunca se reescribe.
- **Separación.** Los artefactos de AI-DLC viven en `aidlc-docs/`; el código de la aplicación nunca va ahí.
- **Trazabilidad.** Cada requisito tiene ID (`RF-NN`, `RNF-NN`); historias, diseños y código lo citan.

## Estructura

```
aidlc-docs/
  aidlc-state.md
  audit.md
  inception/
    requirements/      fuente, requisitos, preguntas
    user-stories/
    application-design/
    plans/
  construction/
    <unidad>/          diseños por unidad
    build-and-test/
```
