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
