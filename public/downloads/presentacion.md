---
marp: true
theme: uncover
class: invert
paginate: true
header: '**Zero Trust Architecture** · UNNE — Ingeniería del SW 2 · 2026'
footer: 'Ariel Antinori | ariel.antinori@comunidad.unne.edu.ar'
size: 16:9
style: |
  section {
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: #0a1628;
    color: #e2eaf4;
    padding: 40px 60px;
  }
  section.lead { text-align: center; background: linear-gradient(135deg,#0a1628 60%,#0d2547); }
  section.lead h1 { font-size: 1.9em; margin-bottom: 0.2em; }
  section.stats { background: #071020; }
  h1 { color: #5bc8f5; font-size: 1.5em; letter-spacing: -0.02em; }
  h2 { color: #7dd3fc; font-size: 1.25em; border-bottom: 2px solid #1e4a7a; padding-bottom: 10px; margin-bottom: 0.6em; }
  h3 { color: #93c5fd; font-size: 1em; margin-top: 0.5em; }
  strong { color: #fbbf24; }
  em { color: #6ee7b7; }
  a { color: #38bdf8; }
  code { background: #0f2035; color: #7dd3fc; padding: 2px 7px; border-radius: 4px; font-size: 0.85em; }
  pre { background: #0f2035; border: 1px solid #1e4a7a; border-radius: 8px; padding: 16px; font-size: 0.75em; }
  blockquote {
    border-left: 4px solid #3b82f6; background: rgba(59,130,246,0.1);
    padding: 12px 18px; margin: 1em 0; border-radius: 0 6px 6px 0;
    font-style: italic; color: #bfdbfe;
  }
  table { width: 100%; border-collapse: collapse; font-size: 0.82em; margin-top: 0.5em; }
  th { background: #0f2a4a; color: #7dd3fc; padding: 9px 12px; text-align: left; border-bottom: 2px solid #1e4a7a; }
  td { padding: 7px 12px; border-bottom: 1px solid #0f2035; }
  tr:nth-child(even) td { background: rgba(255,255,255,0.03); }
  ul, ol { text-align: left; padding-left: 1.4em; }
  li { margin-bottom: 0.3em; line-height: 1.5; }
  footer { color: #334155; font-size: 0.52em; }
  header { color: #334155; font-size: 0.52em; }
  .badge { display: inline-block; background: #1e40af; color: #bfdbfe; border-radius: 20px; padding: 3px 12px; font-size: 0.8em; margin: 2px; }
  .chip { display: inline-block; background: #064e3b; color: #6ee7b7; border-radius: 4px; padding: 2px 8px; font-size: 0.78em; font-family: monospace; }
---

<!-- _class: lead -->

# Arquitectura de Confianza Cero
## *Zero Trust Architecture (ZTA)*

Diseño de software bajo la premisa de **red comprometida**  
Autenticación y autorización granular en microservicios

---

**Ariel Antinori**  
Universidad Nacional del Nordeste — Ingeniería del SW 2  
Junio 2026

---

## Agenda

1. El problema: seguridad perimetral y sus fallas
2. ¿Qué es Zero Trust Architecture?
3. Evolución histórica (1994–2025)
4. Principios fundamentales — NIST SP 800-207
5. Componentes lógicos: PEP, PDP, PA
6. Implementación en microservicios
7. Tecnologías: SPIFFE/SPIRE · mTLS · OAuth 2.0 · OPA · Istio
8. Microsegmentación y gestión de secretos
9. DevSecOps y monitoreo continuo
10. Desafíos, adopción industrial y tendencias

---

## El Modelo *Castle-and-Moat* 🏰

> *"Todo tráfico interno a la red corporativa es inherentemente confiable"*

### La premisa rota

- 🔓 Un atacante que traspasa el perímetro obtiene **acceso irrestricto**
- ➡️ Movimiento lateral **sin obstáculos** hacia servicios críticos
- 🌐 VPN como **único** control de acceso
- 🔍 Tráfico inter-servicio sin cifrar, sin autenticar, sin autorizar
- 👥 Amenazas internas con acceso amplio e irrestricto

**Conclusión:** cuando falla el perímetro, **falla todo el sistema**.

---

## La Realidad de las Arquitecturas Modernas

En entornos cloud-nativos la frontera *"interno = confiable"* **no existe**.

| Problema | Consecuencia en seguridad |
|----------|--------------------------|
| Decenas/cientos de microservicios | Superficie de ataque masiva |
| Tráfico este-oeste sin inspección | Credenciales en texto plano |
| IPs efímeras en Kubernetes | Identidades de red no confiables |
| Pods creados y destruidos | Autenticación imposible por IP |
| Amenazas internas | Acceso amplio e irrestricto |

---

<!-- _class: stats -->

## La Amenaza en Números

| Indicador | Dato | Fuente |
|-----------|------|--------|
| Aumento de brechas en APIs (2024) | **+321%** | Markaicode, 2025 |
| Causa principal — incidentes API | Autorización inadecuada **(68%)** | Markaicode, 2025 |
| Organizaciones con incidentes en K8s | **89%** en el último año | Groundcover, 2026 |
| Costo promedio global de una brecha | **USD 4,44 millones** | IBM, 2025 |

<br>

> Hallazgo de producción: tráfico de **pago y credenciales de usuarios**  
> fluyendo en texto plano entre servicios del mismo clúster — DZone, 2025

---

## ¿Qué es Zero Trust Architecture?

> *"Ninguna entidad — usuario, dispositivo, servicio o segmento de red —  
> debe recibir confianza implícita por su ubicación."*  
> — NIST SP 800-207

### Premisa central

**Nunca confiar. Siempre verificar.**

Cada solicitud de acceso debe ser:

1. 🔐 **Verificada** → identidad explícita comprobada
2. 🎯 **Autorizada** → mínimo privilegio, por sesión
3. 👁️ **Monitoreada** → de forma continua y permanente

---

## Evolución Histórica

| Año | Hito |
|-----|------|
| **1994** | Marsh: bases filosóficas de confianza computacional |
| **2003** | Jericho Forum: *de-perimeterización* |
| **2010** | Kindervag (Forrester): acuña *"Zero Trust"* formalmente |
| **2014** | Google BeyondCorp publicado — validación a escala industrial |
| **2020** | NIST SP 800-207 — marco normativo global |
| **2021** | EO 14028 — mandato federal EE.UU. para todas las agencias |
| **2023** | NIST SP 800-207A — aplicaciones cloud-nativas y multi-nube |
| **2025** | ETSI TS 104 102 — estándar europeo (ZT-Kipling) |

---

## Los 7 Principios — NIST SP 800-207

| Principio | Definición |
|-----------|-----------|
| **Nunca confiar, siempre verificar** | Sin confianza implícita por ubicación |
| **Mínimo privilegio** | Acceso acotado al tiempo y sesión mínimos |
| **Asumir la brecha** | Diseñar para contener el radio de daño |
| **Verificación continua** | Autenticación permanente, no solo al inicio |
| **Acceso por sesión** | Política dinámica por solicitud individual |
| **Recursos como externos** | Sin distinción entre red interna y externa |
| **Identidades consistentes** | Humanas *y* no humanas (workloads, pipelines) |

---

## Componentes del Modelo NIST: PEP · PDP · PA

```
  Cliente / Servicio A
        │
        ▼
  ┌───────────┐    ¿Permitir esta solicitud?    ┌─────────────┐
  │    PEP    │ ──────────────────────────────▶ │     PDP     │
  │  (Envoy)  │                                 │    (OPA)    │
  │  Proxy    │ ◀──── Decisión: Allow/Deny ──── │   Rego      │
  └─────┬─────┘                                 └──────┬──────┘
        │                                              │
        ▼                                        ┌─────┴──────┐
  Servicio destino                               │     PA     │
                                                 │ (Políticas)│
                                                 └────────────┘
```

- **PEP** *(Policy Enforcement Point)*: Envoy — intercepta todo el tráfico
- **PDP** *(Policy Decision Point)*: OPA — evalúa y decide
- **PA** *(Policy Administrator)*: gestiona el ciclo de vida de las políticas

---

## Identidad como Nuevo Perímetro

**La identidad reemplaza a la ubicación de red** como base del control de acceso.

### Dos dimensiones complementarias

**Identidad humana** → usuarios finales y administradores  
Protocolos: *OAuth 2.0* y *OpenID Connect (OIDC)*

**Identidad de carga de trabajo** (*workload identity*) → microservicios,  
funciones serverless, jobs CI/CD, agentes de IA  
Estándar: *SPIFFE / SPIRE*

> En Kubernetes, una dirección IP que perteneció a un servicio legítimo  
> puede **reasignarse en segundos** a otro pod.

---

## SPIFFE y SPIRE — Identidad de Workload

**SPIFFE**: *Secure Production Identity Framework For Everyone*  
**SPIRE**: implementación de referencia (CNCF)

### Flujo de atestación:

```
1. Workload/Pod se inicia
      ↓
2. SPIRE realiza ATESTACIÓN (verifica imagen, nombre, namespace…)
      ↓
3. Emite SVID (SPIFFE Verifiable Identity Document)
      → Certificado X.509  ·  TTL ≈ 1 hora  ·  Renovación automática
      ↓
4. El SVID se usa para mTLS y autenticación ante Vault
```

✅ Sin credenciales estáticas · Sin rotación manual · Rastro auditable

---

## mTLS — Autenticación Mutua

### TLS estándar vs. Mutual TLS

| Aspecto | TLS estándar | **mTLS** |
|---------|-------------|---------|
| ¿Quién se autentica? | Solo el servidor | **Ambas partes** |
| Tráfico cifrado | Norte-Sur | **Norte-Sur + Este-Oeste** |
| Gestión de certificados | Manual | **Automática (service mesh)** |
| Overhead | — | **< 2 ms** con conexiones persistentes |

mTLS garantiza que **cada servicio verifica criptográficamente**  
la identidad del servicio que lo invoca, antes de procesar la solicitud.

---

## OAuth 2.0 y OpenID Connect

Para la dimensión de **identidad humana** en microservicios:

**OAuth 2.0** → framework de *autorización*  
→ Tokens JWT emitidos por el Identity Provider (IdP)  
→ Acceso limitado sin exponer credenciales directamente

**OpenID Connect (OIDC)** → capa de *identidad* sobre OAuth 2.0  
→ SSO (*Single Sign-On*) entre servicios  
→ Claims de identidad propagados por JWT  
→ OIDC Federation 1.0: federación multi-dominio automatizada

### Arquitectura de producción moderna:
```
API Gateway → OAuth2/OIDC → JWT → mTLS interno (SPIFFE/SPIRE)
```

---

## Open Policy Agent — OPA

Motor de políticas de **código abierto**, propósito general.  
Desacopla la lógica de autorización del código de aplicación.

```rego
# Política Rego: autorizar solo lectores a rutas /api/docs/
package authz.microservices

default allow = false

allow {
    input.method == "GET"
    input.user.roles[_] == "reader"
    startswith(input.path, "/api/docs/")
}
```

✅ Políticas **externas** al servicio — consistencia y auditabilidad  
✅ Actualizables **sin redesplegar** los microservicios  
✅ **Versionables y testeables** como código fuente (*Policy-as-Code*)  
✅ Integración nativa con Envoy (*External Authorization Filter*)

---

## Service Mesh: Istio y Envoy

**Istio** → service mesh más adoptado en Kubernetes  
**Envoy** → proxy *sidecar* junto a cada pod (PEP universal)

### Envoy intercepta **todo** el tráfico del servicio:

| Capacidad Envoy | Función Zero Trust |
|-----------------|-------------------|
| mTLS automático | Cifrado y auth. entre todos los servicios |
| Validación SVID | Verifica identidad SPIFFE del caller |
| External AuthZ | Delega decisión a OPA por solicitud |
| Telemetría | Métricas, logs, trazas distribuidas |

> *"Mover las preocupaciones de seguridad fuera de la aplicación  
> y hacia el mesh"* — Tetrate, 2023

---

## Microsegmentación

**Objetivo:** contener el **movimiento lateral** tras cualquier brecha.

> Analogía: puertas cortafuegos en un edificio — si una zona  
> es comprometida, la amenaza no puede propagarse libremente.

### En Kubernetes con Network Policies:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-default
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
  # Sin reglas → deniega TODO por defecto
```

**Postura correcta:** *deny all* por defecto → permitir explícitamente solo lo necesario.

`mTLS + NetworkPolicy = autenticación + segmentación`

---

## Gestión de Secretos Efímeros

**Problema frecuente:** secretos hardcodeados en código fuente,  
imágenes de contenedor o variables de entorno sin protección.

### Flujo Zero Trust con HashiCorp Vault:

```
① Pod inicia → recibe SVID de SPIRE automáticamente
         ↓
② SVID se usa como credencial para autenticarse ante Vault
         ↓
③ Vault emite credenciales dinámicas con TTL corto (ej: 15 min)
         ↓
④ Pod accede al recurso (BD, API externa) con esas credenciales
         ↓
⑤ Credenciales expiran → se renuevan automáticamente
```

**Resultado:** en ningún punto existen **credenciales estáticas** en el sistema.

---

## DevSecOps + Zero Trust

> *"Cada transferencia en el flujo debe probar identidad,  
> delimitar permisos y llevar evidencia hacia adelante"*  
> — Cloudaware, 2026

| Fase | Control Zero Trust |
|------|--------------------|
| **Desarrollo** | SAST · escaneo de secretos · commits firmados |
| **Build (CI)** | Escaneo de imágenes de contenedor · firma con Cosign |
| **Deploy (CD)** | Admission controllers · verificación de firmas |
| **Runtime** | mTLS · Network Policies · OPA · rotación de secretos |

La seguridad **no es una fase terminal** — es un **atributo transversal**.

---

## Monitoreo Continuo y Observabilidad

El principio de *verificación continua* requiere **monitoreo permanente**.

| Componente | Función |
|-----------|---------|
| **Telemetría Envoy/Istio** | Métricas, logs y trazas de cada solicitud inter-servicio |
| **UEBA** | Anomalías comportamentales: un servicio accediendo recursos inusuales |
| **SIEM** | Correlación de eventos de múltiples fuentes |
| **Telemetría IdP** | Logins anómalos, rotación inusual de tokens |
| **Telemetría SPIRE** | Auditoría de cada SVID emitido — trazabilidad completa |

> *"No se puede asegurar lo que no se puede ver"*  
> — Developers.dev, 2026

---

## Desafíos de Implementación

| Desafío | Descripción |
|---------|-------------|
| **Complejidad de integración** | SPIRE + IdP + service mesh + OPA + Vault + observabilidad |
| **Overhead de rendimiento** | mTLS + JWT en cada req. (< 2 ms con Envoy) |
| **Costos de migración** | Hardware, licencias, personal especializado |
| **Errores de configuración** | *Deny all by default* requiere mapeo previo exhaustivo |
| **Auditoría incompleta** | 50% de impl. descuidan trazabilidad *(PMC, 2025)* |
| **Fricción organizacional** | ZTA como obstáculo percibido a la velocidad |

> Revisión sistemática de 74 artículos (2016–2025): la auditoría y  
> la orquestación permanecen **poco desarrolladas** en la mayoría de impl.

---

## Casos de Referencia Industrial

### Google BeyondCorp
Eliminó la VPN corporativa. Acceso basado en **identidad del usuario y postura del dispositivo**. Todos los empleados trabajan de forma segura desde cualquier red.

### Microsoft Zero Trust
*Zero Trust Deployment Center*: guías completas para identidades, dispositivos, aplicaciones, datos, infraestructura y redes.

### Amazon EKS + Istio + OPA
Implementación reproducible y documentada en AWS Open Source Blog (2025): Zero Trust en Kubernetes con Istio y OPA como External Authorization.

---

## Tendencias Emergentes

| Tendencia | Estado actual |
|-----------|--------------|
| **Agentes de IA como workloads** | SPIFFE/SPIRE directamente aplicable a agentes LLM |
| **IA para detección adaptativa** | Anomalías + actualización automática de políticas |
| **Multi-cloud y federación** | SPIFFE Federation + IETF WIMSE (estándar emergente) |
| **Policy-as-Code maduro** | OPA/Rego en CI/CD con linters (Regal) |
| **Criptografía post-cuántica** | NIST estandariza algoritmos QC-resistentes para mTLS/PKI |

---

<!-- _class: lead -->

## Conclusiones

---

**ZTA no es paranoia — es respuesta racional al entorno moderno**

✅ La confianza implícita por ubicación de red **ya no es viable**

✅ La **identidad** — humana y de workload — es el nuevo perímetro

✅ La seguridad es **transversal y sistémica**, no una capa final

✅ Cada componente asume que la **capa anterior puede estar comprometida**

✅ El camino es **incremental**: mapear → identificar → mTLS → OPA → monitorear

<br>

> *El costo promedio de una brecha (USD 4,44M) supera  
> ampliamente el costo de implementar ZTA correctamente.*

---

## Hoja de Ruta — Implementación Incremental

```
Paso 1 ── Mapear todas las comunicaciones inter-servicio existentes
    ↓
Paso 2 ── Identidad verificable por workload (SPIFFE/SPIRE)
    ↓
Paso 3 ── mTLS + Network Policies (microsegmentación)
    ↓
Paso 4 ── Externalizar autorización → OPA (Policy-as-Code)
    ↓
Paso 5 ── Monitoreo continuo y telemetría (Istio + SIEM)
    ↓
Paso 6 ── Gestión de secretos efímeros (Vault)
    ↓
Paso 7 ── Integrar controles en pipeline CI/CD (DevSecOps)
```

---

<!-- _class: lead -->

# ¿Preguntas?

---

**Ariel Antinori**  
[ariel.antinori@comunidad.unne.edu.ar](mailto:ariel.antinori@comunidad.unne.edu.ar)  
Universidad Nacional del Nordeste — Ingeniería del SW 2

**Recursos clave:**  
- NIST SP 800-207 → https://doi.org/10.6028/NIST.SP.800-207  
- NIST SP 800-207A → https://csrc.nist.gov/pubs/sp/800/207/a/final  
- arXiv 2511.04925 → https://arxiv.org/abs/2511.04925  
- SPIFFE/SPIRE → https://spiffe.io  
- Open Policy Agent → https://www.openpolicyagent.org  
- Istio → https://istio.io
