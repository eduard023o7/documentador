"""Schemas of the framework profile files under `contenido/marco/` (see domain-entities.md)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1
CODE_PATTERN = r"^[A-Z0-9]{2,6}$"
SEMVER_PATTERN = r"^\d+\.\d+\.\d+$"

Severity = Literal["bloqueante", "advertencia", "info"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _File(_Model):
    version_esquema: Literal[1]


# tipos.yaml
class DocType(_Model):
    codigo: str = Field(pattern=CODE_PATTERN)
    clave: str
    nombre: str
    nivel: int = Field(ge=1)
    padre_permitido: str
    requiere_tecnologia: bool = False
    descripcion: str


class ClassificationStep(_Model):
    pregunta: str
    resultado: str


class TypesFile(_File):
    tipos: list[DocType] = Field(min_length=1)
    test_clasificacion: list[ClassificationStep] = Field(min_length=1)


# dominios.yaml
class Domain(_Model):
    codigo: str = Field(pattern=CODE_PATTERN)
    nombre: str
    estado: Literal["propuesto", "aprobado", "descartado", "por_decidir"]
    aprobador: str = "admin"
    mirada: str = ""
    subdominios: list[str] = []
    secciones_opcionales: list[str] = []


class DomainsFile(_File):
    dominios: list[Domain] = []


# codificacion.yaml
class TechnologyRule(_Model):
    patron: str


class CodingFile(_File):
    documento: dict[str, str]
    regla: str
    tecnologia: TechnologyRule


# niveles.yaml
class ObligationLevel(_Model):
    clave: str
    significado: str


class LevelsFile(_File):
    niveles: list[ObligationLevel] = Field(min_length=1)


# relaciones.yaml
class RelationType(_Model):
    clave: str
    significado: str
    implicita: bool = False
    aciclica: bool = False


class RelationsFile(_File):
    relaciones: list[RelationType] = Field(min_length=1)
    precedencia: list[str] = Field(min_length=1)


# ciclo-vida.yaml
class LifecycleFile(_File):
    estados: list[str] = Field(min_length=2)
    transiciones: dict[str, list[str]]
    revision_periodica_meses: int = Field(ge=1)
    aprobaciones_requeridas: int = Field(ge=1)


# versionado.yaml
class VersionRules(_Model):
    mayor: str
    menor: str
    parche: str


class VersioningFile(_File):
    reglas: VersionRules
    version_inicial: str = Field(pattern=SEMVER_PATTERN)


# estilo.yaml
class StyleFile(_File):
    tono: str
    persona: str
    regla_max_oraciones: int = Field(ge=1)
    formato_fecha: str
    idioma: str


# glosario.yaml
class GlossaryTerm(_Model):
    termino: str
    definicion: str
    prohibidos: list[str] = []


class GlossaryFile(_File):
    terminos: list[GlossaryTerm] = []


# fuentes.yaml
class Site(_Model):
    nombre: str
    url: str = Field(pattern=r"^https://")
    tipo: str
    rutas: list[str] = []


class SourcesFile(_File):
    jerarquia: list[str] = Field(min_length=1)
    sitios: list[Site] = []
    origenes: list[str] = Field(min_length=1)


# validacion.yaml
class Criterion(_Model):
    clave: str
    severidad: Severity


class ValidationFile(_File):
    criterios: list[Criterion] = Field(min_length=1)
    miradas: list[str] = []


# contexto.yaml
class ContextFile(_File):
    empresas: list[str] = []
    entorno_ot_it: str = ""
    tecnologias_por_dominio: dict[str, list[str]] = {}
    diagrama: str = ""


# plantillas/catalogo-secciones.yaml
class Section(_Model):
    clave: str
    titulo: str
    instrucciones: str = ""
    generada: bool = False
    contiene_reglas: bool = False
    opcional: bool = False


class SectionCatalog(_File):
    secciones: list[Section] = Field(min_length=1)


# plantillas/<tipo>.yaml
class TemplateSection(_Model):
    clave: str
    obligatoria: bool


class Template(_File):
    tipo: str
    version: str = Field(pattern=SEMVER_PATTERN)
    secciones: list[TemplateSection] = Field(min_length=1)


class Profile(_Model):
    """The whole validated profile. Immutable."""

    tipos: TypesFile
    dominios: DomainsFile
    codificacion: CodingFile
    niveles: LevelsFile
    relaciones: RelationsFile
    ciclo_vida: LifecycleFile
    versionado: VersioningFile
    estilo: StyleFile
    glosario: GlossaryFile
    fuentes: SourcesFile
    validacion: ValidationFile
    contexto: ContextFile
    catalogo: SectionCatalog
    plantillas: dict[str, Template]
    principios: str

    def doc_type(self, key: str) -> DocType:
        for doc_type in self.tipos.tipos:
            if doc_type.clave == key:
                return doc_type
        raise KeyError(key)

    def doc_type_by_code(self, code: str) -> DocType:
        for doc_type in self.tipos.tipos:
            if doc_type.codigo == code:
                return doc_type
        raise KeyError(code)

    def domain_codes(self) -> set[str]:
        return {d.codigo for d in self.dominios.dominios if d.estado != "descartado"}

    def level_keys(self) -> list[str]:
        return [level.clave for level in self.niveles.niveles]

    def section(self, key: str) -> Section:
        for section in self.catalogo.secciones:
            if section.clave == key:
                return section
        raise KeyError(key)

    def severity(self, criterion: str) -> Severity:
        for item in self.validacion.criterios:
            if item.clave == criterion:
                return item.severidad
        raise KeyError(criterion)
