---
id: EST-INF-AWS-001
titulo: Landing zone en AWS
tipo: estandar
dominio: INF
tecnologia: AWS
padre: LIN-INF-001
relaciones:
- tipo: depende_de
  destino: LIN-SEG-002
alcance:
  incluye:
  - OUs
  - SCPs
  excluye:
  - redes on-premise
justificacion: Nombra un producto y fija valores verificables.
fuentes:
- titulo: AWS Well-Architected
  ubicacion: kb://aws-wa.pdf#p12
prioridad: alta
estado: en_validacion
version: 0.0.0
dependencias_abiertas: false
proxima_revision:
---

## Propósito

Definir la estructura base de cuentas en AWS.

## Alcance y aplicabilidad

Aplica a todas las cuentas del grupo.

## Documentos relacionados

- [[LIN-INF-001]]
- [[LIN-SEG-002]]

## Reglas

Reglas de la landing zone.

### EST-INF-AWS-001.R01 · DEBE

**Enunciado:** Cada entorno tiene una cuenta separada.

**Justificación:** Aísla fallas y permisos; cumple [[LIN-INF-001.R02]].

**Cómo se verifica:** La OU de cada entorno contiene solo sus cuentas.

**Fuentes:** [AWS Well-Architected, p. 12](kb://aws-wa.pdf#p12)

### EST-INF-AWS-001.R02 · DEBERÍA

**Enunciado:** Las cuentas usan SCPs heredadas de su OU.

**Justificación:** Evita configuraciones manuales
diferentes por cuenta.

**Cómo se verifica:** No hay SCPs asignadas directamente a cuentas.

**Fuentes:** Documentación de AWS Organizations.

## Especificación técnica

| OU | Uso |
|---|---|
| Prod | Producción |

## Excepciones

Se solicitan al arquitecto de infraestructura.

## Cumplimiento y verificación

Revisión trimestral de la estructura de OUs.

## Referencias

AWS Control Tower.

## Control de cambios

| Versión | Fecha | Motivo |
|---|---|---|
