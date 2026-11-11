# Demo outline

The demo follows the six segments in the assignment. Each segment shows the result below.

| # | Segment | What is shown | Expected result |
|---|---|---|---|
| 1 | Architecture | authentik (IdP and dashboard), Flask app with python3-saml (SP), Docker Compose; SP-initiated and IdP-initiated flows | See `docs/architecture.md` |
| 2 | Live onboarding | Register the sample app in authentik: SP values, SAML provider, attribute mappings, group bindings, IdP metadata exchange | Sample App tile appears on the dashboard for alice |
| 3 | SAML values | Decoded SAML response (SAML-tracer) beside the app's `/profile` page: issuer, destination, audience, NameID, attributes, validity window, SHA-256 signature | Values match on both sides |
| 4 | RBAC | alice, bob, carol, dave, plus direct URL access to `/admin` | Matches the access matrix in `docs/test-evidence.md` |
| 5 | Negative tests | Tampered, unsigned and expired assertions; disabled user; role change in the IdP | Assertions rejected with HTTP 403; disabled user blocked; new role applies at next login |
| 6 | Q&A | | |

## Reproducing the negative tests

The scripts are in `sample-app/tools/`: `test-tamper.sh`, `test-unsigned.sh` and `test-expired.sh`. Each replays a modified or expired assertion to the ACS URL and expects HTTP 403.

## Recordings

Screen recordings of the full matrix and the negative tests are linked in `docs/test-evidence.md`.
