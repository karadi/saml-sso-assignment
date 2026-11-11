# Known limitations and production-hardening notes
| Area | Current state | Production recommendation |
|---|---|---|
| Logout | Local logout only; the authentik session stays active, so the dashboard still works after app logout | Implement Single Logout (SLO) and set short IdP session lifetimes |
| Certificate rotation | IdP metadata is a static file; rotating the authentik signing certificate needs a manual re-download and restart | Publish both old and new certificates during rotation, load metadata from the URL on a schedule |
| Self-signed certificates | Browser warnings | Use an internal CA or a public CA |
| Replay | No store of used assertion IDs; a captured response can be replayed inside its validity window | Add a replay cache, keep short lifetimes |
| Role changes | Applied at next login only; an active session keeps the old role | SCIM provisioning, shorter app sessions |
| High availability | Single instance of each service and one database | Multiple replicas, managed PostgreSQL, load balancer |
| Backup | No backup of the authentik database or configuration | Scheduled database backups, configuration exported as code (blueprints) |
| Audit logging | authentik keeps events; the app logs only to the container output | Central log collection with retention and alerts |
| MFA | Not enforced | Enforce MFA at the IdP, at least for the Admin role |
| Secrets | Local .env files, git-ignored | Secrets manager |
| Test users | Simple test passwords | Real users from a directory, strong password policy |
| Dependencies | Docker images and Python packages pinned loosely | Pin versions, scan images, patch regularly |

## Assumptions

- The IdP is authentik, run locally with Docker Compose; the sample app is a Flask app using python3-saml.
- NameID is the user's email address, because it is unique per user and readable in logs. A persistent identifier would be better for production.
- Roles are carried in the `role` attribute and come from authentik group membership (app-admin, app-editor, app-viewer). Users in no group get no role and no access.
- Self-signed certificates are acceptable for this local demo, as the assignment allows.
- Test users (alice, bob, carol, dave) use simple demo passwords and no real company data.
- Local logout is acceptable; Single Logout is a bonus and is not implemented.
- The recordings are hosted outside git because of their size (about 1 GB).
