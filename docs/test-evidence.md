# Test evidence
Save screenshots in `docs/evidence/` using the file names below.

## RBAC matrix
| User | Dashboard tile | /general | /admin | Screenshot files |
|---|---|---|---|---|
| alice | yes | allowed | allowed | alice-dashboard.png, alice-general.png, alice-admin.png, alice-profile.png |
| bob | yes | allowed (edit button) | 403 | bob-dashboard.png, bob-general.png, bob-admin-403.png |
| carol | yes | allowed (read-only) | 403 | carol-dashboard.png, carol-general.png, carol-admin-403.png |
| dave | no tile | denied | denied | dave-dashboard-empty.png, dave-general-403.png, dave-admin-403.png |

## Negative tests
| Test | Method | Result observed | Screenshot |
|---|---|---|---|
| Tampered assertion | Role edited from Viewer to Admin in a captured response, replayed with `tools/replay.py tamper` | HTTP 403, log: Signature validation failed. SAML Response rejected | tamper-403.png |
| Expired assertion | Captured response replayed after the validity window with `tools/replay.py replay` | HTTP 403, log: Could not validate timestamp: expired | expired-403.png |
| Disabled user | bob set inactive in authentik | Login refused | disabled-bob.png |
| Role change | carol moved from app-viewer to app-editor | Role Editor after next login | role-change-carol.png |

## Notes
A response replayed within its validity window is accepted (no replay cache); see docs/limitations.md.

## Recordings
Screen recordings are too large for the repository and are shared separately:
https://drive.google.com/drive/folders/15OWkLsbwV3ptZ5bn4Kdtcmr7dtneRi5Q?usp=sharing

| File | Content |
|---|---|
| 1-rbac-matrix.mov | alice, bob, carol, dave, SP-initiated and IdP-initiated login |
| 2-assertion-tests.mov | tampered, unsigned and expired assertions |
| 3-idp-changes.mov | disabled user and role change |

## Recordings

The screen recordings are about 1 GB in total, so they are hosted on Google Drive instead of git:

https://drive.google.com/drive/folders/15OWkLsbwV3ptZ5bn4Kdtcmr7dtneRi5Q?usp=sharing

| File | Covers |
|---|---|
| 1-rbac-matrix.mov | alice, bob, carol and dave against the access matrix, including direct admin URL access |
| 2-assertion-tests.mov | Assertion validation: tampered and expired assertions |
| 3-idp-changes.mov | IdP-side changes: disabled user and role change taking effect on next login |

## Recordings

The screen recordings are about 1 GB in total, so they are hosted on Google Drive instead of git:

https://drive.google.com/drive/folders/15OWkLsbwV3ptZ5bn4Kdtcmr7dtneRi5Q?usp=sharing

| File | Covers |
|---|---|
| 1-rbac-matrix.mov | alice, bob, carol and dave against the access matrix, including direct admin URL access |
| 2-assertion-tests.mov | Assertion validation: tampered and expired assertions |
| 3-idp-changes.mov | IdP-side changes: disabled user and role change taking effect on next login |
