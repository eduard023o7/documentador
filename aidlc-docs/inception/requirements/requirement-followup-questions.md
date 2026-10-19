# Preguntas de seguimiento — requisitos

Surgen de tus respuestas del 2026-10-19. Responde después de `[Answer]:` o en el chat (`S1: A, S2: B…`).

---

### S1. (Q2 sin respuesta) El plan menciona **Azure Repos** en la fase 4; el resto del doc usa **GitHub**. Con el monorepo, ¿dónde vive?
A) GitHub (este repositorio, `eduard023o7/documentador`) durante todo el MVP; el adaptador deja abierta la migración a Azure Repos después (Recomendado)
B) GitHub para construir y Azure Repos como destino corporativo dentro del MVP (fase 4)
X) Otro (explica)

[Answer]: A — "Github"

### S2. Así entendí tu respuesta a Q4. ¿Es correcto?

> El trabajo tiene dos momentos:
> 1. **Planificación y definiciones** (antes de redactar): tú cargas como insumo los dominios, los principios y la estructura del marco (tipos, plantillas, IDs, relaciones). Con eso los agentes proponen el **mapa**: qué documentos existen, de qué tipo, su padre y sus relaciones, como grafo. Tú lo apruebas.
> 2. **Redacción bajo demanda**: no se redacta todo el mapa de una vez. Tú eliges un documento del mapa y pides que la IA lo redacte; la IA usa el mapa para no repetir lo que ya cubre otro documento y para referenciarlo por ID.

A) Sí, es correcto
B) Casi: la planificación y las definiciones **ya existen** fuera de la plataforma (indica dónde y en qué formato) y hay que importarlas
C) Casi: la planificación también la hace la IA bajo demanda, por dominio (indica cómo)
X) Otro (explica)

[Answer]: A (inferida de S5: "la idea es definir los dominios, lineamientos, estandares con ayuda de la IA, luego que la IA redacte, nosotros revisar, versionar y luego aprobar")

### S3. Si pides redactar un documento cuyo padre o dependencias aún no están aprobados, ¿qué hace la plataforma?
A) Lo permite con advertencia, y el documento queda marcado como "redactado con dependencias abiertas"; el validador lo revisa de nuevo cuando estas se aprueben (Recomendado: respeta "bajo demanda" sin perder coherencia)
B) Lo bloquea hasta que el padre esté aprobado y las dependencias en revisión (regla original del doc)
X) Otro (explica)

[Answer]: A — "Permitelo con advertencia. Recuerda que no se debe de romper la armonia entre documentos"

### S4. "La aprobación final la da el revisor." ¿Quién es el revisor?
A) Una persona asignada al pedir la redacción (puede ser cualquier usuario); basta su aprobación. En el MVP, normalmente tú (Recomendado)
B) El arquitecto del dominio, configurado en el perfil del marco
C) Tú en todos los casos durante el MVP; los revisores por dominio se configuran después
X) Otro (explica)

[Answer]: X — "De momento todos accederemos con un usuario admin ya que somos del mismo equipo, asi que cada uso revisará usando el mismo usuario"

### S5. ¿Quiénes usan la plataforma en el MVP y quién arma los 30–50 casos de prueba?
A) Solo tú usas la plataforma y armas los casos; la IA te propone temas candidatos para que los clasifiques (Recomendado)
B) Tú y los otros arquitectos usan la plataforma; los casos los arma el equipo
X) Otro (explica)

[Answer]: X — "No entiendo sobre los casos de prueba…" (→ ronda 2, S8)

### S6. Búsqueda web — mi recomendación

| Opción | Cómo funciona | A favor | En contra |
|---|---|---|---|
| **A) Rastreador de Bedrock Knowledge Bases sobre los sitios aprobados** | La Knowledge Base descarga e indexa solo las URLs aprobadas (igual que los PDFs) y se sincroniza periódicamente | Todo queda en AWS, un solo mecanismo de búsqueda con citas, sin proveedor extra, imposible salirse de los sitios aprobados | El contenido es tan fresco como la última sincronización; sitios muy grandes requieren acotar rutas |
| B) Tavily | API de búsqueda pensada para agentes, con filtro `include_domains` | Fácil de integrar con Strands, resultados frescos | Proveedor externo, costo por consulta, una superficie más de inyección |
| C) A + B | KB para las fuentes aprobadas; Tavily solo para que el investigador **descubra** fuentes nuevas que tú apruebas | Lo mejor de ambos | Más piezas |

A) Recomendado: empezar con A. Si en la fase 1 faltan fuentes, agregar B solo para descubrimiento.
B) Tavily
C) A + B desde el inicio
X) Otro (explica)

[Answer]: (sin respuesta → ronda 2)

### S7. Q11 a Q14 quedaron sin respuesta. ¿Tomo las recomendadas?
- Q11: propongo presupuestos iniciales configurables (tokens por ejecución y alerta mensual, p. ej. USD 100)
- Q12: sí a historias de usuario
- Q13: reglas de seguridad como bloqueantes
- Q14: código en inglés; documentación, interfaz, prompts y commits en español

A) Sí, las cuatro recomendadas
X) Otro (indica cuáles cambian)

[Answer]: X — "Dame las preguntas faltantes Q11 a Q14" (→ ronda 2)

---

# Ronda 2 (2026-10-19)

### S8. Casos de prueba: qué son y si los mantenemos
Los "casos de prueba" del doc original son una **lista de ejemplos con la respuesta correcta** (p. ej. "cifrado en reposo → lineamiento, dominio SEG, padre LIN-SEG-001"). Sirven para medir automáticamente si la IA clasifica bien: cada vez que se cambia un prompt o una regla, la IA vuelve a clasificar esos ejemplos y se compara con la respuesta correcta (de ahí el umbral del 90 %). No cambian tu flujo; solo detectan si un ajuste empeoró a la IA.

A) Sin trabajo extra: cada corrección que hagan al revisar el mapa (cambiar tipo, dominio o padre de un documento propuesto) se guarda sola como caso de prueba. La medición empieza cuando haya suficientes correcciones (Recomendado)
B) No usar casos de prueba en el MVP; la calidad la asegura solo la revisión humana (se elimina el umbral del 90 %)
C) Armar la lista a mano antes de la fase 1, como decía el doc
X) Otro (explica)

[Answer]:

### S9. Con un único usuario admin compartido, el historial dirá siempre "admin". ¿Registramos quién revisó?
A) Sí: al aprobar o rechazar se escribe el nombre de quien revisa (campo obligatorio) y queda en el commit y en el historial (Recomendado: conserva la auditoría sin crear usuarios)
B) No, basta con "admin"
X) Otro (explica)

[Answer]:

### S6 (repetida). Búsqueda en sitios web aprobados
A) Base de conocimiento de AWS que descarga e indexa solo los sitios aprobados; Tavily después, si faltan fuentes (Recomendado)
B) Tavily (buscador externo con filtro de dominios)
C) Ambos desde el inicio
X) Otro (explica)

[Answer]:

### Q11. Presupuestos de costo
A) Propongo valores iniciales configurables: tope de tokens por ejecución y alerta mensual de AWS (p. ej. USD 100) (Recomendado)
B) Tengo los valores (indica tope por ejecución y monto mensual)
X) Otro (explica)

[Answer]:

### Q12. ¿Escribimos historias de usuario antes del diseño? (frases del tipo "como admin quiero pedir la redacción de un documento para…", con criterios de aceptación que después se prueban)
A) Sí (Recomendado: hay tres flujos y seis vistas; las historias fijan qué se considera terminado)
B) No: pasar directo de requisitos a diseño
X) Otro (explica)

[Answer]:

### Q13. ¿Aplicamos reglas de seguridad como obligatorias en el diseño y el código? (mínimo privilegio en AWS, cifrado, validación de entradas, registro de auditoría, protección ante instrucciones ocultas en fuentes)
A) Sí, obligatorias: un diseño o código que no las cumpla no pasa la puerta (Recomendado: maneja contenido corporativo y lee fuentes externas)
B) Solo como recomendaciones
X) Otro (explica)

[Answer]:

### Q14. Idioma del código
A) Nombres de variables, funciones y comentarios en inglés; documentación, interfaz, prompts y commits en español (Recomendado)
B) Todo en español, incluido el código
X) Otro (explica)

[Answer]:
