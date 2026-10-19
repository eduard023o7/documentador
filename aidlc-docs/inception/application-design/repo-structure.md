# Estructura del monorepo

```
documentador/
  CLAUDE.md  README.md
  aidlc-docs/                  artefactos AI-DLC (nunca código)

  contenido/                   CONTENIDO DEL MARCO — no importa nada del código (RNF-10)
    marco/                     perfil del marco (lo edita el Admin vía PR o web)
      tipos.yaml  dominios.yaml  codificacion.yaml  niveles.yaml
      relaciones.yaml  ciclo-vida.yaml  versionado.yaml  estilo.yaml
      glosario.yaml  fuentes.yaml  validacion.yaml
      principios.md  contexto.yaml
      plantillas/              fundacional.yaml  lineamiento.yaml  estandar.yaml  catalogo-secciones.yaml
      plantilla-word/          corporativa.docx
    documentos/
      FUN/  LIN/  EST/         <ID>.md (ficha + cuerpo)
    pendientes.yaml            temas fuera del MVP

  src/documentador/            paquete Python (backend, agentes, CLI)
    core/                      C1: profile, document, graph, coherence, ids, versioning
    agents/                    C2: un módulo por agente
      prompts/                 instrucciones en español, una por agente
    flows/                     C3: mapa, documento, necesidad, revalidación
    review/                    C4
    adapters/                  C5 repository · C6 knowledge · C7 rule_index · C8 state · bedrock
    cost/                      C9
    publish/                   C10 (cliente; local o Lambda)
    evals/                     C11
    cli/                       C12 (comando `doc`)
    api/                       C13 (handlers Lambda, U4)
  docgen/                      contenedor con Pandoc + LibreOffice (C10)
  web/                         C14: React + Vite + TypeScript (U4)
  infra/                       C15: CDK en Python, un stack por capa
  tests/                       pytest: unit/ (sin red), integration/ (AWS y GitHub reales), fixtures/
  pyproject.toml
```

## Reglas

1. **Contenido aislado:** `contenido/` solo tiene Markdown, YAML y la plantilla Word. Se puede copiar a otro repositorio sin cambios.
2. **Despliegues que ignoran el contenido (RNF-12):** Amplify solo construye ante cambios en `web/`; CDK se despliega a mano. Un commit de aprobación (solo `contenido/`) no dispara nada.
3. **Ramas:** `main` es lo aprobado. Cada propuesta es una rama `propuesta/<flujo>-<id>` con su PR. El código se desarrolla en ramas propias, separado de las de contenido.
4. **Pruebas sin costo por defecto:** `tests/unit` usa adaptadores en memoria y respuestas de modelos grabadas; `tests/integration` y `doc evaluar` son los únicos que llaman a servicios reales.
