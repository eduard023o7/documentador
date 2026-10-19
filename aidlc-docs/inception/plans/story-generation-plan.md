# Plan de generación de historias de usuario

**Insumo:** `inception/requirements/requirements.md` v3 (aprobada el 2026-10-19).
**Entregables:** `inception/user-stories/personas.md` y `inception/user-stories/stories.md`.

## Preguntas

Responde después de `[Answer]:` o en el chat (`H1: A, H2: A…`).

### H1. ¿Cómo agrupamos las historias?
A) Por **épica = fase del plan** (0 marco, 1 mapa, 2 redacción, 3 necesidades y versionado, 4 web, 5 piloto); así cada épica coincide con una puerta de salida y luego con una unidad de construcción (Recomendado)
B) Por flujo de trabajo (mapa, documento, nueva necesidad) más una épica de vistas y otra de configuración
C) Por pantalla de la web
X) Otro (explica)

[Answer]:

### H2. Personas. Hay un solo usuario admin compartido, pero cumple papeles distintos. ¿Cómo las modelamos?
A) Una sola cuenta con tres "sombreros": **Administrador del marco** (define el perfil y los insumos), **Arquitecto solicitante** (pide mapas, redacciones y cambios) y **Revisor** (revisa, versiona y aprueba). Ayuda a que las historias digan quién hace qué y deja listo separar usuarios después (Recomendado)
B) Una sola persona: "Admin"
X) Otro (explica)

[Answer]:

### H3. Formato de los criterios de aceptación
A) Dado / Cuando / Entonces, verificables y citando los requisitos (RF/RNF) (Recomendado: se convierten directo en pruebas)
B) Lista simple de condiciones
X) Otro (explica)

[Answer]:

### H4. Tamaño de las historias
A) Cada historia se construye y prueba en 1–2 días; las grandes se parten (Recomendado para una persona con IA)
B) Historias grandes, una por capacidad (menos historias, más criterios)
X) Otro (explica)

[Answer]:

## Pasos

- [ ] Recibir respuestas a H1–H4
- [ ] Escribir `personas.md`
- [ ] Escribir `stories.md`: épicas, historias "Como… quiero… para…", criterios de aceptación, prioridad y requisitos que cubre
- [ ] Verificar cobertura: cada RF y RNF aparece en al menos una historia (tabla de trazabilidad)
- [ ] Verificar INVEST: independientes, negociables, valiosas, estimables, pequeñas y comprobables
- [ ] Presentar para aprobación
