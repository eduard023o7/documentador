# Preguntas de verificación de requisitos

Responde cada pregunta escribiendo la letra (o tu texto) después de `[Answer]:`. Si ninguna opción calza, usa la opción **X** y explica. Las preguntas cubren solo vacíos e inconsistencias del insumo; lo que el doc ya define se tomó como requisito en `requirements.md`.

Puedes responder aquí mismo en el archivo o en el chat (por ejemplo: `Q1: A, Q2: B…`).

---

## Repositorios y alcance

### Q1. ¿Qué rol cumple este repositorio `documentador`?
A) Es el repositorio de **código** (lo que el doc llama `plataforma-lineamientos`). El contenido del marco irá en otro repositorio aparte (Recomendado: respeta la separación del doc)
B) Monorepo: código y contenido del marco juntos en `documentador`, en carpetas separadas
C) Es solo el repositorio de planificación AI-DLC; el código irá en otros repositorios
X) Otro (explica)

[Answer]: B — "Mono repo"

### Q2. El plan de fases menciona **Azure Repos** en la fase 4, pero el resto del doc usa **GitHub**. ¿Cuál es el destino del contenido del marco?
A) GitHub en el MVP; el adaptador deja abierta la puerta a Azure Repos después (Recomendado)
B) GitHub para desarrollar y Azure Repos como destino corporativo en la fase 4 (el adaptador debe soportar ambos en el MVP)
C) Azure Repos desde el inicio
X) Otro (explica)

[Answer]: (sin respuesta → seguimiento S1)

### Q3. ¿Qué cubre este ciclo de AI-DLC?
A) Todo el MVP: Inception completo ahora (requisitos, historias, diseño, unidades = fases 1 a 5) y Construction unidad por unidad, empezando por la fase 1 (Recomendado)
B) Solo hasta la fase 1 (agentes del mapa); el resto se planifica después
C) Solo la fase 0 (preparación técnica y perfil del marco)
X) Otro (explica)

[Answer]: A — "todo el MVP"

### Q4. La fase 0 es sobre todo definición del equipo (perfil del marco y casos de prueba). ¿Cómo la abordamos?
A) La IA redacta un **borrador del perfil del marco** (YAML/plantillas, siguiendo el doc) y una **lista candidata de temas** para los casos de prueba; el equipo los corrige y aprueba (Recomendado)
B) El equipo entrega el perfil y los casos ya escritos; la IA solo los valida y les da formato
C) Se parte con el perfil mínimo del doc y los casos de prueba se construyen durante la fase 1
X) Otro (explica)

[Answer]: X — "La IA redacta bajo demanda, previo a eso se hizo planificación y definiciones (dominios, principios, estructura, etc). Evitar redundancia entre documentos y que entre ellos se puedan referenciar, teniendo claro un mapa de relaciones tipo grafo. Si no esta claro dime" (→ seguimiento S2, S3)

## Decisiones pendientes del doc

### Q5. ¿Quién da la aprobación final de un documento?
A) El arquitecto del dominio; los fundacionales y los cambios mayores requieren además al arquitecto empresarial (configurable por dominio en el perfil) (Recomendado)
B) Solo el arquitecto del dominio
C) El equipo completo (los cinco arquitectos)
X) Otro (explica)

[Answer]: X — "La aprobación final la da el revisor" (→ seguimiento S4)

### Q6. Dominios iniciales. El doc sugiere `INF, DAT, SEG, IA, AE, OT`. ¿OT es un dominio propio?
A) Sí, esos seis dominios, con OT como dominio propio
B) Cinco dominios (INF, DAT, SEG, IA, AE); OT es subdominio o tecnología dentro de INF
C) Aún no está decidido; el taxonomista propone y el equipo decide en la fase 1 (Recomendado para no bloquear)
X) Otro (explica)

[Answer]: C — "OT puede ser un dominio, pero aún se definirá, los dominios son parte del input y planificación"

### Q7. Casos de prueba y umbral de calidad
A) Aún no existen; se construyen en la fase 0 (30–50 temas) y el umbral es 90 % de coincidencia (Recomendado)
B) Ya existen o hay material para armarlos (indica dónde); umbral 90 %
C) Otro umbral u otra métrica (indica cuál, p. ej. coincidencia separada para tipo, dominio y padre)
X) Otro (explica)

[Answer]: Umbral 90 % aceptado — "Umbral ok" (quién arma los casos → seguimiento S5)

### Q8. ¿Quién es dueño de los documentos fundacionales?
A) El arquitecto empresarial (sugerencia del doc) (Recomendado)
B) Cada fundacional tiene dueño según su tema (p. ej. clasificación de la información → seguridad)
X) Otro (explica)

[Answer]: X — "Yo seré el dueño de todo el MVP"

### Q9. Proveedor de la API de búsqueda web (limitada a sitios aprobados)
A) Tavily
B) Brave Search API
C) Exa
D) Sin búsqueda web en el MVP: solo PDFs subidos y páginas aprobadas descargadas a la Knowledge Base (Recomendado para empezar: menos superficie de inyección y costo)
X) Otro (explica)

[Answer]: X — "no sé que me sugieres" (→ recomendación en seguimiento S6)

## Entorno y operación

### Q10. ¿Qué está disponible hoy?
Marca todo lo que aplique (p. ej. `A, C`).
A) Cuenta AWS piloto con acceso a modelos Claude en Bedrock (us-east-1) habilitado
B) Plantilla Word corporativa con estilos definidos
C) Lista de sitios web aprobados como fuente
D) Contrato de Gartner revisado
E) Ninguno todavía

[Answer]: A, B — "cuenta AWS, plantilla"

### Q11. Presupuestos de costo
A) Propongo valores iniciales y quedan configurables: tope de tokens por ejecución y alerta mensual (p. ej. USD 100) (Recomendado)
B) Tengo los valores (indícalos: por ejecución y mensual)
X) Otro (explica)

[Answer]: (sin respuesta → seguimiento S7)

## Metodología

### Q12. ¿Generamos historias de usuario (etapa condicional de AI-DLC)?
A) Sí: dos personas (administrador del marco y arquitecto) más historias por flujo y vista, con criterios de aceptación (Recomendado: hay varios actores y vistas)
B) No: pasar directo de requisitos a diseño de aplicación
X) Otro (explica)

[Answer]: (sin respuesta → seguimiento S7)

### Q13. ¿Aplicamos las reglas de seguridad de AI-DLC como restricciones bloqueantes en diseño y código (mínimo privilegio, cifrado, validación de entradas, registro de auditoría, etc.)?
A) Sí, como bloqueantes (Recomendado: la solución manejará contenido corporativo y procesa fuentes externas)
B) No, solo como recomendaciones
X) Otro (explica)

[Answer]: (sin respuesta → seguimiento S7)

### Q14. Idioma del código
A) Identificadores y comentarios de código en inglés; documentación, interfaz, prompts y commits en español (Recomendado)
B) Todo en español, incluido el código
X) Otro (explica)

[Answer]: (sin respuesta → seguimiento S7)
