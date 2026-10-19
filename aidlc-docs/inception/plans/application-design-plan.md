# Plan de diseño de aplicación

**Base:** requisitos v3, historias y plan de ejecución aprobados el 2026-10-19.
**Entregables** (en `inception/application-design/`):
- `components.md` — componentes y responsabilidades
- `component-methods.md` — interfaz de cada componente (firmas, entradas y salidas; la lógica detallada va en el diseño funcional de cada unidad)
- `services.md` — orquestación de los tres flujos
- `component-dependency.md` — dependencias y flujo de datos
- `data-model.md` — ficha, regla, relación, ejecución, observación, paquete, caso de prueba
- `repo-structure.md` — estructura del monorepo

## Decisiones que tomo sin preguntar (dímelo si alguna no te parece)

1. **Reglas de coherencia en código, no en la IA.** Padre único, IDs únicos, ciclos, referencias rotas y solapes explícitos se comprueban con código determinista (barato, exacto, repetible). La IA solo revisa lo que requiere criterio: contradicciones de significado, redundancia, las cinco miradas.
2. **Un núcleo compartido.** El grafo del mapa, el perfil del marco y las reglas de coherencia son una librería Python única que usan los agentes, la API y la línea de comandos. Así la web y los agentes nunca discrepan.
3. **Redundancia con embeddings.** Cada regla aprobada se guarda como vector en un índice de S3 Vectors; antes de proponer una regla se buscan las más parecidas. Costo casi nulo.
4. **Los agentes que leen fuentes no escriben.** Investigador y contraste solo devuelven texto; solo el núcleo, tras la aprobación humana, escribe en el repositorio.

## Preguntas

Responde después de `[Answer]:` o en el chat (`D1: A, D2: A…`).

### D1. ¿Dónde corren los flujos de agentes en las fases 1 a 3 (sin web)?
A) **En tu equipo**, con un comando: los agentes llaman a Bedrock desde tu máquina; se pasan a AgentCore Runtime en U4, cuando llega la web. Más simple de depurar y sin infraestructura de ejecución hasta que haga falta (Recomendado)
B) En AgentCore Runtime desde U1; el comando local solo los dispara
X) Otro (explica)

[Answer]:

### D2. ¿Cómo se revisa y aprueba en las fases 1 a 3, antes de la web?
A) **Pull request en GitHub**: cada propuesta (mapa, borrador, paquete) llega como PR; revisas los cambios, comentas por línea y apruebas con un comando que registra tu nombre y fusiona. GitHub te da gratis la vista de diferencias y los comentarios (Recomendado)
B) Archivo de revisión en Markdown: editas un archivo con "aceptar/rechazar" por regla y ejecutas un comando
X) Otro (explica)

[Answer]:

### D3. ¿Dónde vive el estado de trabajo (ejecuciones, observaciones, aprobaciones, casos de prueba)?
A) **DynamoDB** desde U1 (bajo demanda, centavos al mes); lo mismo que usará la web (Recomendado)
B) Archivos JSON en el repositorio hasta U4, y DynamoDB después
X) Otro (explica)

[Answer]:

## Pasos

- [ ] Recibir respuestas a D1–D3
- [ ] Escribir `components.md`
- [ ] Escribir `component-methods.md`
- [ ] Escribir `services.md`
- [ ] Escribir `component-dependency.md`
- [ ] Escribir `data-model.md`
- [ ] Escribir `repo-structure.md`
- [ ] Verificar que cada historia tiene un componente responsable
- [ ] Presentar para aprobación
