# Architecture

## Components and tool choice
| Component | Choice | Justification |
|---|---|---|
| IdP | authentik | Open source, official Docker Compose, native SAML provider, groups, policy bindings, MFA available |
| Dashboard | authentik application library | Shows only applications the user is entitled to (group bindings) and starts IdP-initiated login from a tile; no custom code to maintain |
| Sample app (SP) | Flask + python3-saml | Small codebase, strict validation of signature, audience, issuer, destination and time window |

## Architecture diagram
```mermaid
flowchart LR
  U[Browser] -->|1. open app / tile| D[authentik dashboard]
  U -->|SP-initiated start| A[Flask sample app :5443]
  D --- I[authentik IdP :9443]
  I -->|signed SAML assertion via browser POST| A
  I --- DB[(PostgreSQL)]
  G[Groups app-admin / app-editor / app-viewer] --> I
```

## SP-initiated login
```mermaid
sequenceDiagram
  participant B as Browser
  participant A as App (SP)
  participant I as authentik (IdP)
  B->>A: GET /saml/login
  A-->>B: 302 to IdP SSO URL with AuthnRequest
  B->>I: AuthnRequest (HTTP-Redirect)
  I->>B: Login form (first time only)
  B->>I: Credentials
  I->>I: Check application group binding
  I-->>B: Auto-POST form with signed SAMLResponse
  B->>A: POST /saml/acs
  A->>A: Validate signature, issuer, audience, destination, InResponseTo, time window
  A-->>B: Session created, redirect to /
```

## IdP-initiated login
```mermaid
sequenceDiagram
  participant B as Browser
  participant I as authentik (IdP)
  participant A as App (SP)
  B->>I: Login to dashboard
  I-->>B: Tiles filtered by group
  B->>I: Click Sample App tile
  I-->>B: Auto-POST form with signed SAMLResponse (no InResponseTo)
  B->>A: POST /saml/acs
  A->>A: Same validation (no request ID to match)
  A-->>B: Session created, redirect to /
```

## RBAC
The IdP maps groups to the `role` attribute (app-admin to Admin, app-editor to Editor, app-viewer to Viewer).
The app copies `role` from the assertion into its session and checks it on the server for every request:
`/general` needs Admin, Editor or Viewer; `/admin` needs Admin. Hiding buttons is not relied on; direct URL access returns 403.
