# U0 Fundación — plan de diseño funcional

**Historias:** HU-0.1 a HU-0.7. **Entregables** (en `construction/u0-fundacion/functional-design/`):
- `domain-entities.md` — perfil del marco (cada archivo YAML con sus campos), plantilla, documento, regla
- `business-rules.md` — validaciones del perfil, invariantes, formato de documento y regla, convenciones de Git
- `business-logic-model.md` — carga y validación del perfil, lectura y escritura de documentos, operaciones del adaptador de GitHub, conversión a Word y PDF

## Decisiones que tomo sin preguntar

1. **Valores iniciales del perfil = los del doc de definición.** Tipos y test, IDs (`FUN-<DOM>-NNN`…), niveles DEBE/DEBERÍA/PUEDE, relaciones, ciclo de vida, versionado mayor/menor/parche, plantilla de 11 secciones, revisión anual. Lo que el doc no fija queda marcado `# POR DEFINIR` para que lo completes al revisar.
2. **Criterios de validación iniciales:** bloquean una cita inexistente, una referencia rota, un padre faltante o de tipo incorrecto, un ciclo, un ID repetido, una sección obligatoria faltante y una contradicción con el padre o una dependencia. Solo avisan el estilo, la longitud de las reglas y los términos fuera del glosario.
3. **Marca "Borrador" en Word:** se genera automáticamente una variante de la plantilla corporativa con la marca de agua en el encabezado; tú solo entregas la plantilla original.
4. **Commits con cuenta compartida:** autor "Admin documentador" y el nombre del revisor en una línea `Revisado-por: <nombre>` del mensaje, de modo que GitHub y el historial muestren quién aprobó.
5. **Aprobadores en el perfil:** el campo existe (uno por dominio) pero en el MVP vale "admin" para todos; separarlos después es solo configuración.

## Preguntas

Responde después de `[Answer]:` o en el chat (`F1: A, F2: …`).

### F1. Dominios iniciales en el perfil. Dijiste que los dominios son insumo de la planificación y que la IA ayuda a definirlos (U1).
A) Cargo como **propuesta inicial** los del doc (INF infraestructura, DAT datos, SEG seguridad, IA inteligencia artificial, AE arquitectura empresarial) con OT marcado "por decidir"; en U1 la IA los evalúa y tú decides los finales (Recomendado)
B) Dejo la lista vacía; los ingresas tú antes de U1
X) Otro (indica la lista)

[Answer]:

### F2. Principios corporativos (`principios.md`), que guían a todos los agentes.
A) Los tengo: te los paso (pégalos en el chat o súbelos al repositorio)
B) Aún no: dejo un borrador con los dos que menciona el doc (API-first, seguridad desde el diseño) más espacio para completar antes de U1 (Recomendado si no los tienes a mano)
X) Otro (explica)

[Answer]:

### F3. Sitios web aprobados como fuente (`fuentes.yaml`). Se necesitan en U1, no en U0.
A) Dejo un borrador con fuentes oficiales típicas para revisar (documentación de AWS y Azure, AWS Well-Architected, TOGAF, NIST, ISO 27001 como referencia, OWASP) con su jerarquía de autoridad (Recomendado)
B) Te paso la lista
X) Otro (explica)

[Answer]:

### F4. Plantilla Word corporativa
A) La subo al repositorio en `contenido/marco/plantilla-word/corporativa.docx` (o la adjunto en el chat)
B) Aún no la tengo a mano: construyo y pruebo la conversión con una plantilla genérica y cambiamos a la corporativa cuando la tengas (la puerta de U0 queda pendiente de ese cambio)
X) Otro (explica)

[Answer]:

## Pasos

- [ ] Recibir respuestas F1–F4
- [ ] Escribir `domain-entities.md`
- [ ] Escribir `business-rules.md`
- [ ] Escribir `business-logic-model.md`
- [ ] Verificar cobertura de HU-0.1 a HU-0.7
- [ ] Presentar para aprobación
