# Interfaces de los componentes

Firmas en Python (identificadores en inglés, Q14). Solo contratos: la lógica detallada se define en el diseño funcional de cada unidad. Los tipos (`Ficha`, `Rule`, `Observation`…) siguen `data-model.md`.

## C1 Núcleo del marco — paquete `documentador.core`

```python
# profile.py
def load_profile(path: Path) -> Profile
    # Valida esquema e invariantes no configurables; lanza ProfileError(archivo, campo, motivo).

# document.py
def parse_document(text: str, profile: Profile) -> Document          # ficha + secciones + reglas
def render_document(doc: Document, profile: Profile) -> str
def extract_references(doc: Document) -> list[Reference]             # IDs citados en el texto

# graph.py
class MapGraph:
    @classmethod
    def from_documents(cls, docs: Iterable[Document]) -> "MapGraph"
    def parent(self, doc_id: str) -> str | None
    def dependents(self, doc_id: str, transitive: bool = False) -> set[str]
    def dependencies(self, doc_id: str) -> set[str]
    def by_level(self) -> dict[str, dict[str, list[str]]]               # dominio -> nivel -> IDs
    def impact(self, doc_id: str) -> int
    def with_changes(self, changes: list[DocumentChange]) -> "MapGraph"  # grafo hipotético (paquetes)

# coherence.py
def check_map(graph: MapGraph, profile: Profile) -> list[Observation]
    # padre único y tipo de padre correcto, IDs únicos y bien formados, ciclos en depende_de,
    # destinos de relaciones existentes, precedencia, alcances con temas explícitamente repetidos
def check_document(doc: Document, graph: MapGraph, profile: Profile) -> list[Observation]
    # secciones obligatorias, formato de reglas, referencias existentes y no obsoletas,
    # reglas con IDs únicos, dependencias abiertas
def can_approve(observations: list[Observation]) -> bool                 # sin bloqueantes abiertos

# ids.py
def next_document_id(graph: MapGraph, doc_type: str, domain: str, tech: str | None, profile: Profile) -> str
def next_rule_id(doc: Document) -> str

# versioning.py
def diff_rules(old: Document, new: Document) -> RuleDiff                # agregadas, eliminadas, modificadas
def bump(old_version: str, diff: RuleDiff, profile: Profile) -> str     # mayor / menor / parche
```

## C2 Agentes — paquete `documentador.agents`

Cada agente es una función que arma un agente Strands con sus instrucciones y herramientas y devuelve una salida tipada (Pydantic). Todas reciben `RunContext` (ejecución, presupuesto, modelo).

```python
def research(ctx, target: ResearchTarget) -> ResearchResult              # temas + fuentes
def evaluate_domains(ctx, proposal: DomainProposal) -> DomainAssessment
def propose_map(ctx, topics: ResearchResult, graph: MapGraph) -> MapProposal
def classify_topic(ctx, topic: str, graph: MapGraph) -> Classification   # usada por el evaluador
def draft_document(ctx, ficha: Ficha, inputs: DraftInputs) -> Draft
def revise_rules(ctx, draft: Draft, rejections: list[RuleRejection]) -> Draft
def review(ctx, subject: MapProposal | Draft, findings: list[Observation]) -> list[Observation]
def contrast(ctx, subject: MapProposal | Draft) -> ContrastReport
def intake(ctx, text: str, answers: list[str] = []) -> NeedResult        # estructurada o preguntas
def classify_need(ctx, need: Need, graph: MapGraph) -> NeedClassification
def analyze_impact(ctx, change: Need | ProfileChange, graph: MapGraph) -> ChangePackage
```

## C3 Orquestador — `documentador.flows`

```python
def run_map_flow(domain: str | None, *, budget: Budget) -> RunId          # investigación → taxonomía → validación → contraste → PR
def run_document_flow(doc_id: str, *, accept_open_deps: bool, budget: Budget) -> RunId
def run_rework(run_id: RunId) -> RunId                                    # vuelve con rechazos/observaciones
def run_need_flow(text: str, *, budget: Budget) -> RunId                  # puede pausar en "esperando aclaración"
def answer_need(need_id: str, answers: list[str]) -> RunId
def run_revalidation(doc_ids: list[str]) -> RunId                         # sin IA salvo el validador
```

## C4 Revisión y aprobación — `documentador.review`

```python
def open_review(run_id: RunId) -> PullRequestRef                          # rama + commit + PR con resumen
def collect_feedback(pr: PullRequestRef) -> Feedback                      # rechazos por regla y comentarios del PR
def approve(pr: PullRequestRef, reviewer: str, reason: str) -> ApprovalResult
    # exige reviewer no vacío; recalcula coherencia; si hay bloqueantes, rechaza;
    # fusiona, crea etiquetas, actualiza estados, captura casos de prueba, marca dependientes
def reject(pr: PullRequestRef, reviewer: str, reason: str) -> None
```

## C5 Repositorio — `documentador.adapters.repository`

```python
class ContentRepository(Protocol):
    def read(self, path: str, ref: str = "main") -> str
    def list_files(self, prefix: str, ref: str = "main") -> list[str]
    def create_branch(self, name: str, base: str = "main") -> None
    def commit(self, branch: str, files: dict[str, str | None], message: str, author: Author) -> str
    def open_pull_request(self, branch: str, title: str, body: str) -> PullRequestRef
    def review_comments(self, pr: PullRequestRef) -> list[LineComment]
    def merge(self, pr: PullRequestRef, message: str) -> str
    def tag(self, name: str, commit: str) -> None
class GitHubRepository(ContentRepository): ...
```

## C6 Base de conocimiento — `documentador.adapters.knowledge`

```python
def ingest_file(path: Path, collection: Literal["conocimiento", "existentes"], origin: str) -> SourceId
def sync_sites() -> SyncReport
def search(query: str, collection: str, k: int = 8) -> list[Passage]      # texto + cita (archivo/página o URL)
def citation_exists(citation: Citation) -> bool
```

## C7 Índice de reglas — `documentador.adapters.rule_index`

```python
def upsert_rules(doc: Document) -> None                                   # al aprobar
def remove_rules(doc_id: str) -> None                                     # al dejar obsoleto
def similar_rules(text: str, k: int = 5, exclude_doc: str | None = None) -> list[SimilarRule]  # con puntaje
```

## C8 Estado — `documentador.adapters.state`

```python
def start_run(flow: str, target: str, budget: Budget) -> RunId
def record_step(run_id, step: StepRecord) -> None
def finish_run(run_id, status: str) -> None
def add_observations(run_id, obs: list[Observation]) -> None
def record_approval(doc_id: str, approval: Approval) -> None
def mark_revalidation(doc_ids: list[str], cause: str) -> None
def save_test_case(case: TestCase) -> None
def list_test_cases() -> list[TestCase]
```

## C9 Control de costo — `documentador.cost`

```python
def model_for(agent: str) -> ModelId                                      # desde Parameter Store
class Budget:
    def charge(self, input_tokens: int, output_tokens: int, model: ModelId) -> None   # lanza BudgetExceeded
    @property
    def spent_usd(self) -> float
```

## C10 Publicador — `documentador.publish` (+ contenedor `docgen`)

```python
def render_docx(doc: Document, version: str, draft: bool) -> bytes       # Pandoc + plantilla + marca + enlaces
def render_pdf(docx: bytes) -> bytes                                      # LibreOffice
def publish(doc_id: str, version: str) -> PublishedFiles                  # guarda en S3 publicaciones/
```

## C11 Evaluador — `documentador.evals`

```python
def evaluate(min_cases: int = 30, threshold: float = 0.90) -> EvaluationResult   # por tipo, dominio, padre
```

## C12 CLI — comando `doc`

| Comando | Llama a |
|---|---|
| `doc perfil validar` | C1 `load_profile` |
| `doc insumos cargar <archivo>` · `doc fuentes subir <pdf> --origen <x>` · `doc fuentes sincronizar` | C5, C6 |
| `doc dominios evaluar` | C3 → C2 `evaluate_domains` |
| `doc mapa generar [--dominio INF]` | C3 `run_map_flow` |
| `doc redactar <ID> [--aceptar-dependencias-abiertas]` | C3 `run_document_flow` |
| `doc necesidad "<texto>"` · `doc necesidad responder <id>` | C3 |
| `doc revisar <PR>` | C4 `collect_feedback` → C3 `run_rework` |
| `doc aprobar <PR> --revisor "<nombre>" --motivo "<texto>"` · `doc rechazar …` | C4 |
| `doc evaluar` | C11 |
| `doc ejecuciones [<id>]` | C8 (pasos, costo) |
| `doc publicar <ID>` | C10 |

## C13 API (U4)

Rutas REST equivalentes a la CLI (`/perfil`, `/insumos`, `/fuentes`, `/mapa`, `/documentos/{id}`, `/documentos/{id}/versiones`, `/ejecuciones`, `/revisiones`, `/necesidades`, `/calidad`), todas con sesión Cognito. Los flujos largos se disparan en AgentCore y la web consulta su avance.
