# Historias de usuario — MVP plataforma de lineamientos y estándares

**Base:** requisitos v3 (aprobados el 2026-10-19). Decisiones: épicas por fase (H1), persona única **Admin** (H2), criterios Dado/Cuando/Entonces (H3), historias de 1–2 días (H4).

**Prioridad:** **M** imprescindible para la puerta de salida de la fase · **S** importante, puede moverse a la fase siguiente.

En las fases 1 a 3 todavía no hay web: el Admin opera los flujos con un comando y revisa en archivos Markdown. La fase 4 lleva esas mismas operaciones a la web.

---

## Épica 0 — Marco documental configurable y base técnica

**Puerta de salida:** perfil del marco y plantillas aprobados; despliegue base funcionando con alertas de costo; conversión a Word probada con la plantilla corporativa.

### HU-0.1 Estructura del monorepo · M
Como Admin quiero que el código y el contenido del marco vivan en carpetas separadas del mismo repositorio para poder mover el contenido a otro repositorio sin tocar la aplicación.
**Requisitos:** RNF-10, RNF-12, RF-35

- **Dado** el repositorio, **cuando** se revisa la carpeta de contenido, **entonces** contiene solo `marco/` y `documentos/` y ningún archivo de código.
- **Dado** un commit que solo cambia archivos de contenido, **cuando** llega a GitHub, **entonces** no se reconstruye ni se redespliega la aplicación.
- **Dado** el repositorio recién clonado, **cuando** se lee el README, **entonces** explica qué va en cada carpeta.

### HU-0.2 Despliegue base con control de costo · M
Como Admin quiero desplegar la infraestructura base con un solo comando y alertas de presupuesto para probar sin gastar más de USD 10.
**Requisitos:** RNF-01, RNF-02, RNF-04, RNF-13, RNF-14

- **Dado** una cuenta AWS con credenciales, **cuando** ejecuto el comando de despliegue, **entonces** se crean los recursos en us-east-1 sin pasos manuales.
- **Dado** el despliegue, **cuando** reviso la cuenta, **entonces** existe un presupuesto de USD 10 con alertas al 50 %, 80 % y 100 %.
- **Dado** el despliegue, **cuando** reviso los recursos, **entonces** no hay recursos de costo fijo (NAT Gateway, OpenSearch Serverless, llaves KMS propias) y los buckets S3 no son públicos.
- **Dado** cada función creada, **cuando** reviso sus permisos, **entonces** solo tiene los que necesita.

### HU-0.3 Perfil del marco inicial · M
Como Admin quiero redactar con ayuda de la IA el perfil inicial del marco (tipos y test de clasificación, codificación, niveles, relaciones, ciclo de vida, versionado, estilo, glosario, criterios de validación y principios) para que las reglas del juego estén escritas antes de generar el mapa.
**Requisitos:** RF-08, RF-01, RF-05, RF-15, RF-16, RNF-08

- **Dado** el doc de definición del MVP, **cuando** pido el borrador del perfil, **entonces** la IA genera los archivos del perfil en `marco/` con los valores del doc y marca lo que falta definir.
- **Dado** el borrador, **cuando** lo reviso y apruebo con mi nombre, **entonces** queda en GitHub con versión `marco@1.0.0`.
- **Dado** el perfil aprobado, **cuando** se lee el archivo de tipos, **entonces** contiene el test de clasificación en orden y el criterio para dejar temas fuera del MVP.

### HU-0.4 Plantillas por tipo de documento · M
Como Admin quiero una plantilla por tipo de documento con sus secciones, orden, obligatoriedad e instrucciones de redacción para que todos los documentos se lean igual.
**Requisitos:** RF-12, RF-13, RF-08

- **Dado** el perfil, **cuando** abro la plantilla de estándar, **entonces** incluye "Especificación técnica" como obligatoria; la de lineamiento no la incluye.
- **Dado** cualquier plantilla, **cuando** la reviso, **entonces** define el formato de regla: ID `<ID>.RNN`, nivel, enunciado, justificación, cómo se verifica y fuentes.
- **Dado** un dominio, **cuando** activa una sección opcional, **entonces** solo puede elegirla del catálogo cerrado.

### HU-0.5 Validación del perfil y de las invariantes · M
Como Admin quiero que el sistema rechace un perfil mal formado o que intente cambiar las invariantes para no romper el marco por error.
**Requisitos:** RF-08, RF-10

- **Dado** un perfil con un campo obligatorio faltante o un valor inválido, **cuando** se carga, **entonces** se rechaza indicando archivo, campo y motivo.
- **Dado** un perfil que intenta permitir varios padres o IDs repetidos, **cuando** se carga, **entonces** se rechaza porque esas invariantes no son configurables.

### HU-0.6 Prueba de conversión con la plantilla corporativa · M
Como Admin quiero convertir un Markdown de ejemplo a Word con la plantilla corporativa y luego a PDF para confirmar que la plantilla sirve antes de automatizar.
**Requisitos:** RF-17

- **Dado** la plantilla Word corporativa y un Markdown de ejemplo con títulos, tablas y listas, **cuando** se convierte, **entonces** el Word usa los estilos corporativos sin ajustes manuales.
- **Dado** un documento no aprobado, **cuando** se convierte, **entonces** lleva marca de agua "Borrador".
- **Dado** el Word generado, **cuando** se convierte a PDF, **entonces** conserva formato, portada, encabezado y pie.

### HU-0.7 Adaptador del repositorio de contenido · M
Como Admin quiero que la plataforma lea y escriba el contenido a través de un adaptador de GitHub para poder cambiar de cuenta o de proveedor solo con configuración.
**Requisitos:** RF-35, RF-36, RNF-06

- **Dado** el adaptador configurado, **cuando** la plataforma guarda un cambio aprobado, **entonces** se crea un commit con autor, fecha, motivo y nombre del revisor.
- **Dado** un paquete de cambios, **cuando** se crea, **entonces** el adaptador abre una rama; al aprobarse, la fusiona y crea las etiquetas de versión.
- **Dado** el token de GitHub, **cuando** se revisa dónde está guardado, **entonces** está en Parameter Store cifrado y no aparece en código ni en logs.
- **Dado** otra cuenta de GitHub, **cuando** cambio la configuración, **entonces** la plataforma funciona sin cambios de código.

---

## Épica 1 — Agentes del mapa

**Puerta de salida:** mapa piloto del dominio de infraestructura aprobado; coincidencia con los casos de prueba ≥ 90 % (cuando haya al menos 30 casos).

### HU-1.1 Cargar principios y contexto de arquitectura · M
Como Admin quiero registrar los principios corporativos y el contexto de arquitectura (dominios propuestos, tecnologías por dominio, empresas del grupo, entorno OT/IT y el diagrama del framework) para que los agentes trabajen sobre nuestra realidad.
**Requisitos:** RF-24, RF-03

- **Dado** el formato de insumos, **cuando** cargo principios y contexto, **entonces** quedan guardados y versionados.
- **Dado** el contexto sin dominios propuestos, **cuando** intento generar el mapa, **entonces** el sistema lo impide y explica qué falta.
- **Dado** el contexto, **cuando** se revisa, **entonces** ningún dominio está fijado en el código; todos vienen del insumo.

### HU-1.2 Cargar fuentes de conocimiento · M
Como Admin quiero subir PDFs y registrar los sitios web aprobados en una base de conocimiento barata para que los agentes citen fuentes reales.
**Requisitos:** RF-24, RF-27, RNF-05, RNF-07, RNF-13

- **Dado** un PDF subido, **cuando** se indexa, **entonces** una búsqueda devuelve fragmentos con el nombre del archivo y la página de origen.
- **Dado** la lista de sitios aprobados, **cuando** se sincroniza, **entonces** solo se indexan páginas de esos sitios.
- **Dado** la base de conocimiento, **cuando** se revisa su configuración, **entonces** usa S3 Vectors como almacén.
- **Dado** un archivo marcado como Gartner, **cuando** intento cargarlo sin la revisión del contrato registrada, **entonces** el sistema lo rechaza.

### HU-1.3 Evaluación de dominios por la IA · M
Como Admin quiero que un agente evalúe los dominios que propusimos y sugiera ajustes con su justificación para decidir los dominios finales con más información.
**Requisitos:** RF-03, RF-23, RNF-09

- **Dado** los dominios propuestos, **cuando** ejecuto la evaluación, **entonces** recibo, por dominio, si lo mantiene, divide, fusiona o renombra, con justificación y fuentes.
- **Dado** las sugerencias, **cuando** las apruebo o ajusto con mi nombre, **entonces** los dominios aprobados quedan en el perfil con su código para IDs.
- **Dado** que no apruebo, **cuando** reviso el perfil, **entonces** los dominios no cambiaron.

### HU-1.4 Investigación por dominio · M
Como Admin quiero que el investigador averigüe qué debe cubrir un dominio y reúna fuentes citables para que el mapa no dependa de la memoria de la IA.
**Requisitos:** RF-18, RF-26, RNF-05

- **Dado** un dominio aprobado, **cuando** ejecuto la investigación, **entonces** obtengo una lista de temas, cada uno con al menos una fuente de la base de conocimiento.
- **Dado** una fuente que contiene instrucciones dirigidas a la IA, **cuando** el investigador la lee, **entonces** la trata como texto y no las ejecuta.
- **Dado** el investigador, **cuando** se revisan sus permisos, **entonces** no puede escribir en el mapa.

### HU-1.5 Propuesta de mapa · M
Como Admin quiero que el taxonomista proponga los documentos de un dominio con su ficha completa para definir fundacionales, lineamientos y estándares con ayuda de la IA.
**Requisitos:** RF-01, RF-02, RF-04, RF-05, RF-38, RF-40, RF-23

- **Dado** los temas investigados, **cuando** ejecuto el taxonomista, **entonces** cada documento propuesto tiene ficha completa: ID, título, tipo, dominio, padre, relaciones, frontera de alcance, justificación según el test, fuentes, impacto, prioridad y estado "propuesto".
- **Dado** un tema que describe pasos de ejecución o cambia más de una vez al año, **cuando** se clasifica, **entonces** queda como pendiente fuera del MVP y no como documento.
- **Dado** un tema que ya cubre otro documento del mapa, **cuando** se clasifica, **entonces** el taxonomista propone referenciarlo en vez de crear otro documento.
- **Dado** la propuesta, **cuando** se guarda, **entonces** cada documento es un archivo Markdown con ficha y sin cuerpo.

### HU-1.6 Validación del mapa · M
Como Admin quiero que el validador revise el mapa propuesto contra las reglas de coherencia para no aprobar un mapa con contradicciones.
**Requisitos:** RF-06, RF-10, RF-26, RF-41

- **Dado** un mapa con un estándar sin lineamiento padre, IDs repetidos o un ciclo en `depende_de`, **cuando** se valida, **entonces** el informe lo marca como bloqueante.
- **Dado** dos documentos con fronteras de alcance solapadas, **cuando** se valida, **entonces** el informe propone cuál define el tema y cuál lo referencia.
- **Dado** una fuente citada que no existe, **cuando** se valida, **entonces** el informe lo marca como bloqueante.
- **Dado** el informe, **cuando** lo leo, **entonces** cada observación tiene severidad, documento afectado y motivo.

### HU-1.7 Contraste con documentos existentes · S
Como Admin quiero comparar el mapa validado con los documentos que ya tenemos para ver coincidencias, omisiones y temas nuevos sin que contaminen la propuesta.
**Requisitos:** RF-24, RF-25

- **Dado** documentos existentes subidos, **cuando** se genera el mapa, **entonces** el taxonomista no los usa.
- **Dado** el mapa validado, **cuando** ejecuto el contraste, **entonces** recibo coincidencias, temas que los existentes cubren y el mapa omitió, y temas nuevos.
- **Dado** el contraste, **cuando** termina, **entonces** el mapa no cambió; las diferencias solo se incorporan si las apruebo.

### HU-1.8 Revisión y aprobación del mapa · M
Como Admin quiero aprobar, corregir o rechazar el mapa propuesto, firmando con mi nombre, para que nada entre al mapa sin revisión humana.
**Requisitos:** RF-21, RF-23, RF-42, RF-16, RF-35, RF-41

- **Dado** un mapa con observaciones bloqueantes, **cuando** intento aprobarlo, **entonces** el sistema lo impide y muestra cuáles son.
- **Dado** un mapa sin bloqueantes, **cuando** lo apruebo con mi nombre, **entonces** se guarda en GitHub con versión `mapa@x.y.z` y mi nombre en el commit.
- **Dado** que pido ajustes con observaciones, **cuando** confirmo, **entonces** el flujo vuelve al taxonomista con esas observaciones.
- **Dado** que intento aprobar sin escribir mi nombre, **cuando** confirmo, **entonces** el sistema lo rechaza.

### HU-1.9 Casos de prueba automáticos y evaluación · M
Como Admin quiero que mis correcciones al mapa se guarden solas como casos de prueba y se midan en cada cambio de prompts o reglas para saber si la IA mejora o empeora.
**Requisitos:** RF-37, RNF-11

- **Dado** que corrijo el tipo, dominio o padre de un documento propuesto, **cuando** apruebo, **entonces** se guarda un caso con el tema y la respuesta correcta.
- **Dado** un cambio en prompts o en el perfil, **cuando** ejecuto la evaluación, **entonces** la IA reclasifica todos los casos y obtengo el porcentaje de coincidencia por tipo, dominio y padre.
- **Dado** al menos 30 casos y una coincidencia menor a 90 %, **cuando** termina la evaluación, **entonces** se marca como no aprobada.
- **Dado** menos de 30 casos, **cuando** termina, **entonces** se informa el resultado sin aplicar el umbral.

### HU-1.10 Tope de costo y trazas por ejecución · M
Como Admin quiero que cada ejecución tenga un tope de tokens y deje registro de sus pasos y su costo para no gastar de más y poder depurar.
**Requisitos:** RNF-03, RNF-04, RNF-13

- **Dado** una ejecución que supera su tope de tokens, **cuando** ocurre, **entonces** se detiene, conserva lo hecho y avisa.
- **Dado** una ejecución terminada, **cuando** la consulto, **entonces** veo cada paso, el agente, el modelo usado, los tokens y el costo estimado.
- **Dado** una tarea simple (admisión, clasificación de prueba), **cuando** se ejecuta, **entonces** usa el modelo barato; redactor y validador usan el más capaz.

### HU-1.11 Reevaluación del mapa al cambiar las reglas · S
Como Admin quiero que, si cambio el test, el esquema de IDs, los tipos de relación o los criterios de validación, el validador revise todo el mapa para que siga cumpliendo las nuevas reglas.
**Requisitos:** RF-07

- **Dado** un cambio aprobado en alguna de esas partes del perfil, **cuando** se aprueba, **entonces** se ejecuta la validación de todo el mapa.
- **Dado** el resultado, **cuando** hay incumplimientos, **entonces** aparecen como observaciones por documento.

---

## Épica 2 — Agentes de redacción

**Puerta de salida:** primeros documentos piloto de infraestructura aprobados.

### HU-2.1 Pedir la redacción de un documento · M
Como Admin quiero elegir un documento del mapa aprobado y pedir que la IA lo redacte para avanzar bajo demanda, según nuestras prioridades.
**Requisitos:** RF-14, RF-15

- **Dado** un documento en estado "propuesto" con padre aprobado, **cuando** pido su redacción, **entonces** pasa a "en redacción" y se inicia el flujo de documento.
- **Dado** un documento cuyo padre o dependencias no están aprobados, **cuando** pido su redacción, **entonces** el sistema advierte cuáles están abiertos y, si confirmo, lo redacta marcado "con dependencias abiertas".
- **Dado** un documento ya en redacción, **cuando** pido otra vez su redacción, **entonces** el sistema lo impide.

### HU-2.2 Fuentes para cada regla · M
Como Admin quiero que el investigador reúna fuentes específicas para el documento antes de redactar para que cada regla esté sustentada.
**Requisitos:** RF-19, RF-26

- **Dado** un documento a redactar, **cuando** corre el investigador, **entonces** entrega temas y fuentes citables de la base de conocimiento para ese documento.
- **Dado** una fuente que no se puede verificar, **cuando** se entrega, **entonces** no se incluye.

### HU-2.3 Borrador con la plantilla y reglas con ID · M
Como Admin quiero que el redactor escriba el documento con la plantilla de su tipo y reglas con ID, referenciando otros documentos en vez de copiarlos, para obtener documentos uniformes y sin redundancia.
**Requisitos:** RF-11, RF-12, RF-13, RF-38, RF-39, RNF-08

- **Dado** un documento y su plantilla, **cuando** el redactor termina, **entonces** el borrador tiene todas las secciones obligatorias en el orden de la plantilla.
- **Dado** el borrador, **cuando** reviso sus reglas, **entonces** cada una tiene ID `<ID>.RNN`, nivel, enunciado, justificación, cómo se verifica y fuentes.
- **Dado** un tema que ya define otro documento, **cuando** el redactor lo necesita, **entonces** escribe una referencia a su ID y no repite el contenido.
- **Dado** el borrador, **cuando** se guarda, **entonces** registra la versión del perfil y de la plantilla usadas.

### HU-2.4 Validación del documento · M
Como Admin quiero que el validador revise cada borrador (plantilla, coherencia con padre y dependencias, citas reales, redundancia y las cinco miradas) para revisar solo borradores que ya pasaron un control.
**Requisitos:** RF-19, RF-26, RF-38, RF-39, RF-41

- **Dado** un borrador con una regla que contradice a su padre o relaja una regla del dominio dueño, **cuando** se valida, **entonces** se marca como bloqueante.
- **Dado** una regla con el mismo significado que otra existente, **cuando** se valida, **entonces** se marca y se propone reemplazarla por una referencia a su ID.
- **Dado** una referencia a un documento o regla inexistente u obsoleta, **cuando** se valida, **entonces** se marca como bloqueante.
- **Dado** el borrador, **cuando** se valida, **entonces** el informe incluye observaciones desde las miradas de datos, IA, infraestructura, seguridad y arquitectura empresarial.

### HU-2.5 Contraste del documento · S
Como Admin quiero comparar el borrador validado con los documentos existentes sobre el mismo tema para detectar algo importante que se haya omitido.
**Requisitos:** RF-19, RF-25

- **Dado** un borrador validado y documentos existentes, **cuando** corre el contraste, **entonces** recibo coincidencias y diferencias sin que el borrador cambie.

### HU-2.6 Revisión por regla y aprobación del documento · M
Como Admin quiero aceptar, rechazar o comentar cada regla y aprobar el documento firmando con mi nombre para revisar rápido y con precisión.
**Requisitos:** RF-15, RF-21, RF-23, RF-41, RF-42

- **Dado** un borrador en revisión, **cuando** rechazo dos reglas con comentarios, **entonces** solo esas dos vuelven al redactor y el resto se conserva.
- **Dado** un borrador sin bloqueantes y todas sus reglas aceptadas, **cuando** lo apruebo con mi nombre, **entonces** pasa a "aprobado", se versiona y queda mi nombre en el historial.
- **Dado** un borrador con bloqueantes o con dependencias abiertas sin revalidar, **cuando** intento aprobarlo, **entonces** el sistema lo impide y explica por qué.

### HU-2.7 Revalidación de dependientes · M
Como Admin quiero que, cuando un documento cambia de estado o de versión, sus dependientes se marquen para revalidación para mantener la armonía entre documentos.
**Requisitos:** RF-14, RF-41

- **Dado** un documento aprobado con dependientes, **cuando** se aprueba una versión nueva, **entonces** sus dependientes quedan marcados "por revalidar".
- **Dado** un documento "con dependencias abiertas", **cuando** esas dependencias se aprueban, **entonces** el validador lo revisa de nuevo y la marca se quita si no hay conflictos.

---

## Épica 3 — Nuevas necesidades, versionado y publicación

**Puerta de salida:** un paquete de cambios aplicado sin romper reglas del mapa; Word y PDF publicados con la plantilla corporativa.

### HU-3.1 Registrar una necesidad nueva · M
Como Admin quiero registrar una necesidad (un tema nuevo o un cambio) y que la IA me pida aclaraciones si está incompleta para que se procese bien desde el inicio.
**Requisitos:** RF-20

- **Dado** una necesidad incompleta, **cuando** la registro, **entonces** el agente de admisión pregunta lo que falta antes de seguir.
- **Dado** una necesidad completa, **cuando** se procesa, **entonces** queda estructurada (qué, por qué, dominio probable, urgencia).

### HU-3.2 Clasificar la necesidad · M
Como Admin quiero que el taxonomista diga si la necesidad es un documento nuevo, una ampliación o ya está cubierta para no crear documentos redundantes.
**Requisitos:** RF-20, RF-38

- **Dado** una necesidad ya cubierta por un documento aprobado, **cuando** se clasifica, **entonces** se informa cuál la cubre y no se propone documento nuevo.
- **Dado** una necesidad nueva, **cuando** se clasifica, **entonces** se propone su ficha con tipo, dominio, padre y justificación.

### HU-3.3 Paquete de cambios con análisis de impacto · M
Como Admin quiero que el analista de impacto arme un paquete con todos los documentos que cambian y cómo para aprobar el cambio completo de una vez.
**Requisitos:** RF-20, RF-22, RF-35

- **Dado** una necesidad clasificada, **cuando** corre el analista, **entonces** el paquete lista cada documento afectado, el cambio propuesto y el tipo de versión resultante.
- **Dado** el paquete, **cuando** se crea, **entonces** queda en su propia rama sin tocar el contenido aprobado.

### HU-3.4 Aprobación atómica del paquete · M
Como Admin quiero que el paquete se valide con todo aplicado y se publique completo o no se publique para que el mapa nunca quede a medias.
**Requisitos:** RF-22, RF-41, RF-42

- **Dado** un paquete, **cuando** se valida, **entonces** el validador revisa el mapa como quedaría con el paquete aplicado.
- **Dado** un paquete aprobado con mi nombre, **cuando** se aplica, **entonces** se dispara la redacción de los documentos afectados y nada se publica hasta que todos estén aprobados.
- **Dado** que un documento del paquete falla, **cuando** termina el proceso, **entonces** no se publica ninguno y el mapa aprobado queda igual.

### HU-3.5 Versionado semántico e historial · M
Como Admin quiero que cada aprobación proponga la versión correcta (mayor, menor o parche) y registre autor, fecha, motivo y paquete para auditar qué cambió y por qué.
**Requisitos:** RF-16, RF-35, RF-42

- **Dado** un cambio que elimina o modifica una regla DEBE, **cuando** se aprueba, **entonces** se propone versión mayor; si agrega reglas o cambia DEBERÍA/PUEDE, menor; si solo mejora la redacción, parche.
- **Dado** una versión aprobada, **cuando** se publica, **entonces** se crea la etiqueta `<ID>@x.y.z` y, si cambió el mapa, `mapa@x.y.z`.
- **Dado** el historial de un documento, **cuando** lo consulto, **entonces** cada versión muestra autor, revisor, fecha, motivo y paquete.

### HU-3.6 Publicación en Word y PDF · M
Como Admin quiero que cada versión se publique en Word con la plantilla corporativa y en PDF, con enlaces en las referencias, para entregar documentos listos para usar.
**Requisitos:** RF-17, RF-39

- **Dado** una versión aprobada, **cuando** el publicador termina, **entonces** existen su Word y su PDF guardados por versión.
- **Dado** un borrador, **cuando** se genera su Word, **entonces** lleva marca de agua "Borrador".
- **Dado** un documento con referencias a otros IDs, **cuando** se abre el Word o el PDF, **entonces** las referencias son enlaces.

### HU-3.7 Cambio del perfil del marco con migración · S
Como Admin quiero que un cambio en el perfil (por ejemplo, una plantilla) se apruebe como un documento y genere un paquete de migración para los documentos afectados.
**Requisitos:** RF-07, RF-09, RF-11

- **Dado** un cambio en una plantilla, **cuando** lo apruebo, **entonces** el analista lista los documentos redactados con la versión anterior.
- **Dado** esa lista, **cuando** la confirmo, **entonces** el redactor propone la migración como paquete de cambios.

### HU-3.8 Revisión anual y obsolescencia · S
Como Admin quiero saber qué documentos aprobados tienen la revisión anual vencida y poder marcar uno como obsoleto o reemplazado para mantener el mapa vigente.
**Requisitos:** RF-15, RF-06

- **Dado** un documento aprobado hace más de un año sin revisión, **cuando** consulto los vencidos, **entonces** aparece en la lista.
- **Dado** un documento nuevo que reemplaza a otro, **cuando** se aprueba con la relación `reemplaza`, **entonces** el anterior pasa a "obsoleto" y sus referencias se marcan para revalidar.

---

## Épica 4 — Interfaz web

**Puerta de salida:** un integrante del equipo opera los flujos desde la web sin ayuda.

### HU-4.1 Inicio de sesión · M
Como Admin quiero entrar con usuario y contraseña para que solo el equipo acceda a la plataforma.
**Requisitos:** RF-34, RNF-14

- **Dado** el usuario admin, **cuando** ingreso credenciales válidas, **entonces** entro a la plataforma.
- **Dado** una llamada a la API sin sesión válida, **cuando** llega, **entonces** se rechaza.
- **Dado** el diseño, **cuando** se revisa, **entonces** los permisos están asociados a un rol (hoy, admin) para poder agregar usuarios y roles después.

### HU-4.2 Insumos y fuentes desde la web · M
Como Admin quiero cargar principios, contexto, PDFs, sitios aprobados y documentos existentes desde formularios para no depender de archivos ni comandos.
**Requisitos:** RF-24, RNF-09, RNF-14

- **Dado** el formulario de contexto, **cuando** lo completo y guardo, **entonces** queda versionado igual que en la fase 1.
- **Dado** un archivo con formato no permitido o demasiado grande, **cuando** lo subo, **entonces** se rechaza con un mensaje claro.

### HU-4.3 Lanzar flujos y seguir su avance · M
Como Admin quiero lanzar los flujos de mapa, documento y nueva necesidad desde la web y ver en qué paso van para saber cuándo revisar.
**Requisitos:** RF-18, RF-19, RF-20, RNF-03, RNF-09

- **Dado** un flujo lanzado, **cuando** lo consulto, **entonces** veo el agente en curso, los pasos terminados y el costo acumulado.
- **Dado** un flujo detenido por tope de costo o error, **cuando** lo consulto, **entonces** veo el motivo en lenguaje claro.

### HU-4.4 Vista de grafo · M
Como Admin quiero ver el mapa como grafo, con filtros y resaltado de dependientes, para entender cómo se relacionan los documentos.
**Requisitos:** RF-28, RF-40

- **Dado** el mapa aprobado, **cuando** abro el grafo, **entonces** cada documento es un nodo con forma según su tipo y color según su estado, y cada relación es una arista con estilo según su tipo.
- **Dado** el grafo, **cuando** filtro por dominio, tipo o estado, **entonces** solo se muestran los nodos que cumplen el filtro.
- **Dado** un nodo, **cuando** lo selecciono, **entonces** se resaltan sus dependientes.

### HU-4.5 Vista por niveles · M
Como Admin quiero ver la matriz de dominios por nivel con cada documento y su estado para saber de un vistazo qué tenemos y qué falta.
**Requisitos:** RF-29, RF-02

- **Dado** el mapa, **cuando** abro la vista, **entonces** veo filas por dominio y columnas fundacional, lineamiento y estándar, con cada documento y su estado.

### HU-4.6 Vista de cobertura · S
Como Admin quiero ver documentos por estado y dominio, revisiones vencidas y observaciones abiertas para seguir el avance del programa.
**Requisitos:** RF-30

- **Dado** el mapa, **cuando** abro la cobertura, **entonces** veo el conteo por estado y dominio, la lista de revisiones vencidas y las observaciones abiertas.

### HU-4.7 Ficha e historial · M
Como Admin quiero ver la ficha de un documento, sus versiones y las diferencias regla por regla, y descargar Word y PDF de cada versión, para auditar los cambios.
**Requisitos:** RF-31, RF-39

- **Dado** un documento con varias versiones, **cuando** comparo dos, **entonces** veo las reglas agregadas, eliminadas y modificadas.
- **Dado** una versión, **cuando** pido sus archivos, **entonces** descargo su Word y su PDF.
- **Dado** una referencia en la ficha o el cuerpo, **cuando** la selecciono, **entonces** navego al documento referenciado.

### HU-4.8 Bandeja y revisión por regla en la web · M
Como Admin quiero una bandeja con borradores, mapas y paquetes pendientes, y revisar cada regla con sus fuentes y observaciones, para aprobar sin tocar Git.
**Requisitos:** RF-32, RF-21, RF-35, RF-42, RNF-09

- **Dado** pendientes de revisión, **cuando** abro la bandeja, **entonces** los veo ordenados por antigüedad con su tipo.
- **Dado** una regla, **cuando** la abro, **entonces** veo sus fuentes, la justificación de la IA y las observaciones del validador, y puedo aceptarla, rechazarla o comentarla.
- **Dado** que apruebo con mi nombre, **cuando** confirmo, **entonces** se hace el commit por detrás y nunca veo comandos de Git.

### HU-4.9 Revisión del mapa propuesto en la web · M
Como Admin quiero revisar el mapa propuesto en la web y corregir tipo, dominio o padre de cada documento para definir el mapa con la IA de forma cómoda.
**Requisitos:** RF-23, RF-37, RF-42, RNF-09

- **Dado** un mapa propuesto, **cuando** lo abro, **entonces** veo cada documento con su ficha y la justificación del taxonomista.
- **Dado** que corrijo un documento, **cuando** apruebo con mi nombre, **entonces** la corrección se guarda también como caso de prueba.

### HU-4.10 Editor del perfil del marco · S
Como Admin quiero editar el perfil del marco desde la web para ajustar las reglas del juego sin tocar archivos.
**Requisitos:** RF-08, RF-09, RF-10

- **Dado** el editor, **cuando** cambio una plantilla y guardo, **entonces** el cambio queda pendiente de aprobación como cualquier documento.
- **Dado** el editor, **cuando** intento cambiar una invariante, **entonces** la opción no está disponible.

### HU-4.11 Calidad de los agentes y costos · S
Como Admin quiero ver la calidad de los agentes y el costo por ejecución para saber cuándo ajustar prompts o reglas.
**Requisitos:** RF-33, RF-37, RNF-04

- **Dado** ejecuciones y revisiones registradas, **cuando** abro la vista, **entonces** veo borradores aprobados sin cambios, observaciones más frecuentes por tipo, coincidencia con los casos de prueba y costo por ejecución y acumulado del mes.

---

## Épica 5 — Piloto con el equipo

**Puerta de salida:** piloto aprobado por el equipo.

### HU-5.1 Dominio de infraestructura completo · M
Como Admin quiero completar el mapa y los documentos de infraestructura, con sus dependencias en otros dominios, para probar la plataforma en un caso real.
**Requisitos:** RF-14, RF-41, RNF-04

- **Dado** el mapa de infraestructura aprobado, **cuando** termina el piloto, **entonces** todos sus documentos de prioridad alta están aprobados y sin observaciones bloqueantes.
- **Dado** el piloto, **cuando** se revisa el costo, **entonces** no superó el presupuesto definido.

### HU-5.2 Ajustes y extensión a otros dominios · S
Como Admin quiero aplicar lo aprendido en el piloto y generar el mapa de los demás dominios para extender el marco al resto del equipo.
**Requisitos:** RF-03, RF-37

- **Dado** las observaciones del piloto, **cuando** se ajustan prompts o perfil, **entonces** la evaluación con los casos de prueba se mantiene ≥ 90 %.
- **Dado** un nuevo dominio aprobado, **cuando** genero su mapa, **entonces** se integra con el de infraestructura sin conflictos bloqueantes.

### HU-5.3 Guía breve de uso · S
Como Admin quiero una guía corta de cómo usar la plataforma para que cualquier integrante del equipo la opere sin ayuda.
**Requisitos:** RNF-09

- **Dado** la guía, **cuando** un integrante que no participó en la construcción la sigue, **entonces** completa el flujo de redacción y aprobación de un documento.

---

## Trazabilidad requisitos → historias

| Requisito | Historias |
|---|---|
| RF-01 | HU-0.3, HU-1.5 |
| RF-02 | HU-1.5, HU-4.5 |
| RF-03 | HU-1.1, HU-1.3, HU-5.2 |
| RF-04 | HU-1.5 |
| RF-05 | HU-0.3, HU-1.5 |
| RF-06 | HU-1.6, HU-3.8 |
| RF-07 | HU-1.11, HU-3.7 |
| RF-08 | HU-0.3, HU-0.4, HU-0.5, HU-4.10 |
| RF-09 | HU-3.7, HU-4.10 |
| RF-10 | HU-0.5, HU-1.6, HU-4.10 |
| RF-11 | HU-2.3, HU-3.7 |
| RF-12 | HU-0.4, HU-2.3 |
| RF-13 | HU-0.4, HU-2.3 |
| RF-14 | HU-2.1, HU-2.7, HU-5.1 |
| RF-15 | HU-0.3, HU-2.1, HU-2.6, HU-3.8 |
| RF-16 | HU-0.3, HU-1.8, HU-3.5 |
| RF-17 | HU-0.6, HU-3.6 |
| RF-18 | HU-1.4, HU-4.3 |
| RF-19 | HU-2.2, HU-2.4, HU-2.5, HU-4.3 |
| RF-20 | HU-3.1, HU-3.2, HU-3.3, HU-4.3 |
| RF-21 | HU-1.8, HU-2.6, HU-4.8 |
| RF-22 | HU-3.3, HU-3.4 |
| RF-23 | HU-1.3, HU-1.5, HU-1.8, HU-2.6, HU-4.9 |
| RF-24 | HU-1.1, HU-1.2, HU-1.7, HU-4.2 |
| RF-25 | HU-1.7, HU-2.5 |
| RF-26 | HU-1.4, HU-1.6, HU-2.2, HU-2.4 |
| RF-27 | HU-1.2 |
| RF-28 | HU-4.4 |
| RF-29 | HU-4.5 |
| RF-30 | HU-4.6 |
| RF-31 | HU-4.7 |
| RF-32 | HU-4.8 |
| RF-33 | HU-4.11 |
| RF-34 | HU-4.1 |
| RF-35 | HU-0.1, HU-0.7, HU-1.8, HU-3.3, HU-3.5, HU-4.8 |
| RF-36 | HU-0.7 |
| RF-37 | HU-1.9, HU-4.9, HU-4.11, HU-5.2 |
| RF-38 | HU-1.5, HU-2.3, HU-2.4, HU-3.2 |
| RF-39 | HU-2.3, HU-2.4, HU-3.6, HU-4.7 |
| RF-40 | HU-1.5, HU-4.4 |
| RF-41 | HU-1.6, HU-1.8, HU-2.4, HU-2.6, HU-2.7, HU-3.4, HU-5.1 |
| RF-42 | HU-1.8, HU-2.6, HU-3.4, HU-3.5, HU-4.8, HU-4.9 |
| RNF-01 | HU-0.2 |
| RNF-02 | HU-0.2 |
| RNF-03 | HU-1.10, HU-4.3 |
| RNF-04 | HU-0.2, HU-1.10, HU-4.11, HU-5.1 |
| RNF-05 | HU-1.2, HU-1.4 |
| RNF-06 | HU-0.7 |
| RNF-07 | HU-1.2 |
| RNF-08 | HU-0.3, HU-2.3 |
| RNF-09 | HU-1.3, HU-4.2, HU-4.3, HU-4.8, HU-4.9, HU-5.3 |
| RNF-10 | HU-0.1 |
| RNF-11 | HU-1.9 |
| RNF-12 | HU-0.1 |
| RNF-13 | HU-0.2, HU-1.2, HU-1.10 |
| RNF-14 | HU-0.2, HU-4.1, HU-4.2 |

## Revisión INVEST

- **Independientes:** dentro de cada épica, las historias dependen solo de las de épicas anteriores; el orden entre épicas sigue las puertas de salida.
- **Pequeñas (1–2 días):** se cumple en las épicas 0 a 4. Las de la épica 5 son actividades de piloto con el equipo, no desarrollo; su duración depende de la revisión humana.
- **Comprobables:** todos los criterios son Dado/Cuando/Entonces y citan sus requisitos; cada requisito RF y RNF está cubierto por al menos una historia (tabla anterior).
- **Totales:** 47 historias (37 M, 10 S) en 6 épicas.
