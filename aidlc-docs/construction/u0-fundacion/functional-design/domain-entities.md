# U0 · Entidades del dominio

Formato de cada archivo de `contenido/marco/` y de los documentos. Respuestas aplicadas: F1=A (dominios del doc como propuesta), F2=B (borrador de principios), F3=A (borrador de fuentes).

Convenciones: YAML en UTF-8; claves en español sin tildes (`snake_case`); textos visibles con tildes. Todo archivo del perfil tiene `version_esquema: 1`.

## 1. Perfil del marco

### `tipos.yaml` — tipos de documento y test de clasificación (RF-01, RF-02)
```yaml
version_esquema: 1
tipos:
  - codigo: FUN                     # usado en IDs y carpetas
    clave: fundacional
    nombre: Fundacional
    nivel: 1                        # 0 = principios (no son documentos)
    padre_permitido: dominio        # dominio | <clave de otro tipo>
    requiere_tecnologia: false
    descripcion: Clasificaciones y criterios que usan todos los dominios.
  - {codigo: LIN, clave: lineamiento, nombre: Lineamiento, nivel: 2, padre_permitido: dominio, requiere_tecnologia: false, descripcion: Qué se exige y por qué.}
  - {codigo: EST, clave: estandar, nombre: Estándar, nivel: 3, padre_permitido: lineamiento, requiere_tecnologia: true, descripcion: Cómo se cumple con una tecnología concreta.}
test_clasificacion:                 # se aplica en orden; la primera respuesta "sí" decide
  - pregunta: ¿Lo usan como criterio común varios dominios y no exige nada por sí mismo?
    resultado: fundacional
  - pregunta: ¿Seguiría siendo válido si mañana cambiamos de proveedor o tecnología?
    resultado: lineamiento
  - pregunta: ¿Nombra un producto o fija valores comprobables con una herramienta?
    resultado: estandar
  - pregunta: ¿Describe pasos de ejecución o cambia más de una vez al año?
    resultado: fuera_mvp
```

### `dominios.yaml` (RF-03)
```yaml
version_esquema: 1
dominios:
  - codigo: INF
    nombre: Infraestructura
    estado: propuesto               # propuesto | aprobado | descartado
    aprobador: admin                # en el MVP, admin para todos
    mirada: Disponibilidad, escalabilidad, operación y costo de la plataforma.
    subdominios: []
    secciones_opcionales: []        # claves del catálogo de secciones
  # DAT, SEG, IA, AE en estado propuesto; OT en estado "por_decidir"
```

### `codificacion.yaml` (RF-05)
```yaml
version_esquema: 1
documento:
  fundacional: "FUN-{dominio}-{n:03d}"
  lineamiento: "LIN-{dominio}-{n:03d}"
  estandar: "EST-{dominio}-{tecnologia}-{n:03d}"
regla: "{documento}.R{n:02d}"
tecnologia: {patron: "^[A-Z0-9]{2,6}$"}     # p. ej. AWS, AZ, K8S
```

### `niveles.yaml`
```yaml
version_esquema: 1
niveles:
  - {clave: DEBE, significado: Obligatorio. Su incumplimiento requiere una excepción aprobada.}
  - {clave: DEBERÍA, significado: Recomendado. Apartarse requiere justificarlo en el diseño.}
  - {clave: PUEDE, significado: Opcional. Práctica aceptada.}
```

### `relaciones.yaml` (RF-06)
```yaml
version_esquema: 1
relaciones:
  - {clave: deriva_de, significado: Es el padre del documento, implicita: true}   # se expresa con el campo padre
  - {clave: depende_de, significado: Usa algo definido en otro documento, aciclica: true}
  - {clave: complementa, significado: Cubre un tema vecino}
  - {clave: reemplaza, significado: Sustituye a un documento anterior, que pasa a obsoleto}
precedencia: [principio, fundacional, lineamiento, estandar]
```

### `ciclo-vida.yaml` (RF-15)
```yaml
version_esquema: 1
estados: [propuesto, en_redaccion, en_validacion, en_revision, aprobado, obsoleto]
transiciones:
  propuesto: [en_redaccion, obsoleto]
  en_redaccion: [en_validacion]
  en_validacion: [en_redaccion, en_revision]
  en_revision: [en_redaccion, aprobado]
  aprobado: [en_redaccion, obsoleto]       # una nueva versión vuelve a redacción
  obsoleto: []
revision_periodica_meses: 12
aprobaciones_requeridas: 1
```

### `versionado.yaml` (RF-16)
```yaml
version_esquema: 1
reglas:
  mayor: Cambia o elimina una regla DEBE.
  menor: Agrega reglas o cambia reglas DEBERÍA o PUEDE.
  parche: Mejora la redacción sin cambiar el significado.
version_inicial: 1.0.0                      # al primer aprobado
```

### `estilo.yaml`
```yaml
version_esquema: 1
tono: impersonal
persona: tercera
regla_max_oraciones: 2
formato_fecha: AAAA-MM-DD
idioma: es
```

### `glosario.yaml`
```yaml
version_esquema: 1
terminos:
  - {termino: landing zone, definicion: "# POR DEFINIR", prohibidos: [zona de aterrizaje]}
```

### `fuentes.yaml` (RF-26, RF-27, F3)
```yaml
version_esquema: 1
jerarquia: [documentacion_oficial, marco_referencia, articulo_tecnico]
sitios:
  - {nombre: AWS Documentation, url: https://docs.aws.amazon.com/, tipo: documentacion_oficial, rutas: ["/wellarchitected/", "/controltower/"]}
  # Azure (learn.microsoft.com), TOGAF, NIST CSRC, OWASP, ISO 27001 (solo referencia)
origenes: [gartner, proveedor, marco_publico, interno]   # para registrar el origen de cada fuente (RNF-07)
```

### `validacion.yaml` (decisión 2 del plan)
```yaml
version_esquema: 1
criterios:
  - {clave: cita_inexistente, severidad: bloqueante}
  - {clave: referencia_rota, severidad: bloqueante}
  - {clave: padre_faltante_o_invalido, severidad: bloqueante}
  - {clave: ciclo_depende_de, severidad: bloqueante}
  - {clave: id_repetido_o_invalido, severidad: bloqueante}
  - {clave: seccion_obligatoria_faltante, severidad: bloqueante}
  - {clave: contradiccion_padre_o_dependencia, severidad: bloqueante}
  - {clave: relaja_regla_dominio_dueno, severidad: bloqueante}
  - {clave: tema_duplicado, severidad: bloqueante}
  - {clave: regla_redundante, severidad: advertencia}
  - {clave: estilo_irregular, severidad: advertencia}
  - {clave: regla_demasiado_larga, severidad: advertencia}
  - {clave: termino_fuera_de_glosario, severidad: advertencia}
  - {clave: dependencias_abiertas, severidad: advertencia}
miradas: [datos, ia, infraestructura, seguridad, arquitectura_empresarial]
```

### `principios.md` (F2) y `contexto.yaml` (HU-1.1)
`principios.md`: lista numerada; cada principio con título, enunciado y razón. Borrador inicial: API-first y seguridad desde el diseño, más `# POR DEFINIR`.
`contexto.yaml`: empresas del grupo, entorno OT/IT, tecnologías por dominio, referencia al diagrama del framework. En U0 queda con la estructura y valores `# POR DEFINIR`.

### `plantillas/<tipo>.yaml` y `plantillas/catalogo-secciones.yaml` (RF-12)
```yaml
# catalogo-secciones.yaml
version_esquema: 1
secciones:
  - {clave: proposito, titulo: Propósito, instrucciones: Una o dos frases sobre para qué existe el documento.}
  - {clave: alcance, titulo: Alcance y aplicabilidad, instrucciones: Qué incluye y qué excluye explícitamente.}
  - {clave: relacionados, titulo: Documentos relacionados, generada: true}      # se arma desde la ficha
  - {clave: definiciones, titulo: Definiciones}
  - {clave: reglas, titulo: Reglas, contiene_reglas: true}
  - {clave: especificacion, titulo: Especificación técnica}
  - {clave: excepciones, titulo: Excepciones}
  - {clave: cumplimiento, titulo: Cumplimiento y verificación}
  - {clave: referencias, titulo: Referencias, generada: true}
  - {clave: control_cambios, titulo: Control de cambios, generada: true}
  - {clave: mapeo_iso27001, titulo: Mapeo a controles ISO 27001, opcional: true}  # ejemplo de sección por dominio

# estandar.yaml
version_esquema: 1
tipo: estandar
version: 1.0.0
secciones:                       # orden = orden en el documento
  - {clave: proposito, obligatoria: true}
  - {clave: alcance, obligatoria: true}
  - {clave: relacionados, obligatoria: true}
  - {clave: definiciones, obligatoria: false}
  - {clave: reglas, obligatoria: true}
  - {clave: especificacion, obligatoria: true}
  - {clave: excepciones, obligatoria: true}
  - {clave: cumplimiento, obligatoria: true}
  - {clave: referencias, obligatoria: true}
  - {clave: control_cambios, obligatoria: true}
```
`fundacional.yaml` y `lineamiento.yaml` iguales sin `especificacion`.

## 2. Documento (`contenido/documentos/<CODIGO_TIPO>/<ID>.md`)
Ficha en front matter según `inception/application-design/data-model.md` §1. Cuerpo: un `## <título de sección>` por sección de la plantilla, en orden. Las secciones `generada: true` las escribe el núcleo al publicar, no el redactor.

## 3. Regla (dentro de la sección Reglas)
```markdown
### LIN-SEG-002.R03 · DEBE
**Enunciado:** Los datos confidenciales se cifran en reposo.
**Justificación:** …
**Cómo se verifica:** …
**Fuentes:** [NIST SP 800-111, p. 4](kb://nist-800-111.pdf#p4)
```
Las referencias a otros documentos o reglas se escriben `[[LIN-SEG-001]]` o `[[LIN-SEG-001.R02]]`.

## 4. Pendientes fuera del MVP (`contenido/pendientes.yaml`)
```yaml
version_esquema: 1
pendientes:
  - {tema: Procedimiento de alta de cuentas AWS, motivo: Describe pasos de ejecución, propuesto_en: RUN#…, fecha: 2026-…}
```
