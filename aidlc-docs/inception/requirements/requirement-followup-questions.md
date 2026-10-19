# Preguntas de seguimiento — requisitos

Surgen de tus respuestas del 2026-10-19. Responde después de `[Answer]:` o en el chat (`S1: A, S2: B…`).

---

### S1. (Q2 sin respuesta) El plan menciona **Azure Repos** en la fase 4; el resto del doc usa **GitHub**. Con el monorepo, ¿dónde vive?
A) GitHub (este repositorio, `eduard023o7/documentador`) durante todo el MVP; el adaptador deja abierta la migración a Azure Repos después (Recomendado)
B) GitHub para construir y Azure Repos como destino corporativo dentro del MVP (fase 4)
X) Otro (explica)

[Answer]:

### S2. Así entendí tu respuesta a Q4. ¿Es correcto?

> El trabajo tiene dos momentos:
> 1. **Planificación y definiciones** (antes de redactar): tú cargas como insumo los dominios, los principios y la estructura del marco (tipos, plantillas, IDs, relaciones). Con eso los agentes proponen el **mapa**: qué documentos existen, de qué tipo, su padre y sus relaciones, como grafo. Tú lo apruebas.
> 2. **Redacción bajo demanda**: no se redacta todo el mapa de una vez. Tú eliges un documento del mapa y pides que la IA lo redacte; la IA usa el mapa para no repetir lo que ya cubre otro documento y para referenciarlo por ID.

A) Sí, es correcto
B) Casi: la planificación y las definiciones **ya existen** fuera de la plataforma (indica dónde y en qué formato) y hay que importarlas
C) Casi: la planificación también la hace la IA bajo demanda, por dominio (indica cómo)
X) Otro (explica)

[Answer]:

### S3. Si pides redactar un documento cuyo padre o dependencias aún no están aprobados, ¿qué hace la plataforma?
A) Lo permite con advertencia, y el documento queda marcado como "redactado con dependencias abiertas"; el validador lo revisa de nuevo cuando estas se aprueben (Recomendado: respeta "bajo demanda" sin perder coherencia)
B) Lo bloquea hasta que el padre esté aprobado y las dependencias en revisión (regla original del doc)
X) Otro (explica)

[Answer]:

### S4. "La aprobación final la da el revisor." ¿Quién es el revisor?
A) Una persona asignada al pedir la redacción (puede ser cualquier usuario); basta su aprobación. En el MVP, normalmente tú (Recomendado)
B) El arquitecto del dominio, configurado en el perfil del marco
C) Tú en todos los casos durante el MVP; los revisores por dominio se configuran después
X) Otro (explica)

[Answer]:

### S5. ¿Quiénes usan la plataforma en el MVP y quién arma los 30–50 casos de prueba?
A) Solo tú usas la plataforma y armas los casos; la IA te propone temas candidatos para que los clasifiques (Recomendado)
B) Tú y los otros arquitectos usan la plataforma; los casos los arma el equipo
X) Otro (explica)

[Answer]:

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

[Answer]:

### S7. Q11 a Q14 quedaron sin respuesta. ¿Tomo las recomendadas?
- Q11: propongo presupuestos iniciales configurables (tokens por ejecución y alerta mensual, p. ej. USD 100)
- Q12: sí a historias de usuario
- Q13: reglas de seguridad como bloqueantes
- Q14: código en inglés; documentación, interfaz, prompts y commits en español

A) Sí, las cuatro recomendadas
X) Otro (indica cuáles cambian)

[Answer]:
