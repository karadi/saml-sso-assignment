# SAML 2.0 SSO: dashboard, sample app and RBAC

Open-source SSO setup built with Docker Compose:

| Component | Tool | URL |
|---|---|---|
| Identity Provider + dashboard | authentik | https://localhost:9443 |
| Sample application (Service Provider) | Flask + python3-saml | https://localhost:5443 |

Why these tools: see `docs/architecture.md`.

## Prerequisites
Docker Desktop (Compose v2.20 or newer), a browser, and `openssl` in the terminal.

## 1. Start everything
```bash
./scripts/setup.sh          # creates authentik/.env and sample-app/.env with random secrets
docker compose up -d        # first build takes about 5 minutes (XML libraries compile)
docker compose ps
```
If you previously started the two parts separately, run `cd sample-app && docker compose down` once first.
Open https://localhost:9443/if/flow/initial-setup/ and set the `akadmin` password
(accept the self-signed certificate warning).

## 2. Configure authentik (about 10 minutes)
Follow `docs/onboarding-runbook.md`. For this sample app it creates: groups `app-admin`,
`app-editor`, `app-viewer`; four SAML property mappings; the provider and application; group bindings;
and the four test users. Download the provider metadata to `sample-app/idp/idp_metadata.xml`, then:
```bash
docker compose restart sample-app
```

## 3. Test users (test data only)
| User | Group | Role sent | Dashboard tile | /general | /admin |
|---|---|---|---|---|---|
| alice | app-admin | Admin | yes | allowed | allowed |
| bob | app-editor | Editor | yes | allowed (edit) | 403 |
| carol | app-viewer | Viewer | yes | allowed (read-only) | 403 |
| dave | none | none | no | denied | denied |

Passwords are set by the administrator in authentik. Use throwaway test values only.

## 4. Try it
- SP-initiated: open https://localhost:5443/ and click "Login with SSO".
- IdP-initiated: log in at https://localhost:9443/ and click the Sample App tile.
- Debug page: https://localhost:5443/profile shows NameID, email, firstName, lastName and role.
- Negative tests: `docs/test-evidence.md`.

## Repository layout
```
docker-compose.yml        one command for both parts (uses include)
authentik/compose.yml     official authentik compose file
sample-app/               Flask SAML app, Dockerfile, tools/ (replay and certificate scripts)
docs/                     architecture, runbook, configuration reference, limitations, test evidence
scripts/setup.sh          generates .env files with random secrets
```
No secrets are committed: `.env` files and generated certificates are git-ignored.

## Troubleshooting
- Browser certificate warning: expected (self-signed). Choose Advanced, then Proceed.
- `/saml/metadata` returns an error: `sample-app/idp/idp_metadata.xml` is missing or empty.
- Login fails: `docker compose logs --tail 30 sample-app` shows the SAML rejection reason.
