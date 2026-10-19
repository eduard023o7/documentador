# Plan de ejecución (planificación del flujo de trabajo)

**Base:** requisitos v3 y 47 historias aprobados el 2026-10-19.

## 1. Evaluación

| Aspecto | Evaluación |
|---|---|
| Tipo | Greenfield, monorepo |
| Alcance del cambio | Sistema completo: 8 agentes, 3 flujos, API, web, generación de Word/PDF, infraestructura AWS |
| Riesgo | **Medio-alto.** El mayor riesgo es la calidad de la clasificación del mapa; el segundo, el costo de los modelos frente a un presupuesto de USD 10 |
| Supuestos técnicos a verificar antes de construir | (1) el rastreador web de Bedrock Knowledge Bases funciona con S3 Vectors; (2) modelos Claude habilitados en Bedrock us-east-1 en tu cuenta; (3) Strands Agents y AgentCore Runtime disponibles en us-east-1; (4) Pandoc + LibreOffice caben en una Lambda contenedor |
| Estrategia | Construir por unidades en el orden de las fases, cada una con su puerta de salida; primero la calidad de los agentes, la web al final |

## 2. Etapas de INCEPTION que faltan

| Etapa | ¿Se ejecuta? | Motivo |
|---|---|---|
| Diseño de aplicación | **Sí** | Hay que fijar una vez, para todas las unidades: componentes, contrato de cada agente, modelo de datos (ficha, regla, relación, ejecución, observación, paquete), API y estructura del monorepo |
| Generación de unidades de trabajo | **Sí** | Formaliza las unidades (abajo), sus dependencias y qué historias van en cada una |

## 3. Unidades de trabajo propuestas

Una unidad por épica, salvo el piloto, que no es construcción.

| Unidad | Historias | Depende de | Puerta de salida |
|---|---|---|---|
| **U0 Fundación** | HU-0.1 a 0.7 | — | Perfil y plantillas aprobados; despliegue base con alertas; Word/PDF probado |
| **U1 Mapa** | HU-1.1 a 1.11 | U0 | Mapa piloto de infraestructura aprobado; evaluación de casos funcionando |
| **U2 Redacción** | HU-2.1 a 2.7 | U1 | Primeros documentos de infraestructura aprobados |
| **U3 Necesidades, versionado y publicación** | HU-3.1 a 3.8 | U2 | Paquete aplicado sin romper el mapa; Word y PDF publicados |
| **U4 Web** | HU-4.1 a 4.11 | U1–U3 | Un integrante opera los flujos sin ayuda |
| *Piloto (no es unidad)* | HU-5.1 a 5.3 | U4 | Piloto aprobado por el equipo. Se ejecuta como uso real + build y pruebas finales |

## 4. Etapas de CONSTRUCTION por unidad

✔ se ejecuta · — se omite (motivo en la nota)

| Etapa | U0 | U1 | U2 | U3 | U4 |
|---|---|---|---|---|---|
| Diseño funcional | ✔ esquema del perfil, plantillas, contrato del adaptador | ✔ test de clasificación, reglas de coherencia, armado del grafo | ✔ formato de regla, detección de redundancia, revalidación | ✔ paquete atómico, cálculo de versión, publicación | ✔ pantallas y flujo de navegación |
| Requisitos no funcionales | ✔ **una sola vez para todo el MVP**: costo, seguridad mínima, trazas | — hereda U0 | — hereda U0 | — hereda U0 | — hereda U0 |
| Diseño NFR | ✔ patrones base: tope de tokens, permisos mínimos, logs | ✔ aislamiento de fuentes (anti-inyección), elección de modelo por agente | — reutiliza U1 | — reutiliza U1 | ✔ sesión Cognito y validación de entradas |
| Diseño de infraestructura | ✔ CDK base, presupuesto, Parameter Store | ✔ AgentCore, Bedrock, Knowledge Base con S3 Vectors, DynamoDB | — sin recursos nuevos | ✔ Lambda contenedor Pandoc/LibreOffice, S3 de versiones | ✔ Amplify, Cognito, API Gateway |
| Generación de código | ✔ | ✔ | ✔ | ✔ | ✔ |
| Build y pruebas | ✔ | ✔ incluye evaluación con casos | ✔ | ✔ | ✔ + pruebas de punta a punta |

**Etapas que se omiten:** ingeniería inversa (no hay código previo) y OPERATIONS (fuera del alcance inicial; el despliegue con un comando ya cubre el MVP).

## 5. Secuencia

```
INCEPTION   Requisitos ✔ → Historias ✔ → Plan de ejecución (ahora) → Diseño de aplicación → Unidades
CONSTRUCTION
  U0 Fundación   diseño funcional → NFR → diseño NFR → infraestructura → código → pruebas
  U1 Mapa        diseño funcional → diseño NFR → infraestructura → código → pruebas (+ evaluación)
  U2 Redacción   diseño funcional → código → pruebas
  U3 Necesidades diseño funcional → infraestructura → código → pruebas
  U4 Web         diseño funcional → diseño NFR → infraestructura → código → pruebas e2e
  Piloto         uso real con el equipo → ajustes → aprobación
```

Cada flecha es una puerta: se presenta el resultado y se espera tu aprobación.

## 6. Control de costo durante la construcción

- Las pruebas automáticas usan respuestas grabadas de los modelos; solo las pruebas de integración y la evaluación de casos llaman a Bedrock.
- Las pruebas reales usan el modelo barato salvo redactor y validador.
- Antes de U1 se mide el costo de una ejecución del flujo de mapa sobre un dominio pequeño y se ajustan los topes.

## 7. Pasos

- [x] Evaluar alcance, riesgo y supuestos
- [x] Decidir etapas de Inception restantes
- [x] Proponer unidades y etapas de Construction por unidad
- [x] Aprobación del plan (2026-10-19)
