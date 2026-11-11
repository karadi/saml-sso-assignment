# Demo script (30 to 40 minutes)

Passwords for alice, bob, carol, dave are the test values you set in authentik. The akadmin password must be saved somewhere you can reach.

## Before the demo (15 minutes earlier)
- [ ] Docker Desktop running; `docker ps` shows authentik server, worker, postgresql and sample-app
- [ ] authentik admin login works (`https://localhost:9443/if/admin/`)
- [ ] Starting state: alice in app-admin, bob in app-editor, carol in app-viewer, dave in no group; all four users Active
- [ ] SAML-tracer installed and allowed in incognito
- [ ] `sample-app/tools/` contains replay.py, unsigned.py, test-tamper.sh, test-unsigned.sh, test-expired.sh, expired_response.txt
- [ ] expired_response.txt is at least 15 minutes old (it is, if it comes from your earlier test)
- [ ] Do Not Disturb on, bookmarks bar hidden (Cmd+Shift+B), Gmail and chat tabs closed, Terminal font enlarged
- [ ] Two Terminal tabs: one in `~/saml-sso-assignment/sample-app`, one spare
- [ ] Backup plan: the recordings in Google Drive (link in docs/test-evidence.md)

## Segment 1: Architecture walkthrough (5 min)
Open docs/architecture.md (diagrams) or a printed copy.
1. Three parts: authentik (IdP and dashboard), Flask app with python3-saml (SP), Docker Compose to run it all.
2. Why authentik: open source, official compose file, native SAML provider, groups and policy bindings, MFA available. Its application library is the dashboard, filtered by group, so no custom portal to maintain.
3. Walk through the SP-initiated sequence: app redirects to IdP with an AuthnRequest, user logs in, IdP checks the group binding, IdP posts a signed assertion to the ACS URL, app validates it and creates a session.
4. IdP-initiated: the dashboard tile makes the IdP post the assertion without a request, so there is no InResponseTo.
5. Roles: group becomes the `role` attribute (app-admin to Admin and so on). The app only decides which role may open which page.

## Segment 2: Live onboarding (10 min)
Preparation (before the demo): in authentik delete the Sample App application and its provider, keep users, groups and the four SSO property mappings. Move `sample-app/idp/idp_metadata.xml` aside.

Say: "I will onboard the application the way the runbook describes."
1. Collect the values from the app owner. Show the SP metadata: open `https://localhost:5443/saml/metadata` and point at Entity ID and ACS URL.
2. authentik admin, Applications, Applications, Create.
3. Name `Sample App`, slug `sample-app`. Provider type SAML.
4. Provider settings: authorization flow default-provider-authorization-implicit-consent; ACS URL `https://localhost:5443/saml/acs`; Audience `https://localhost:5443/saml/metadata`.
5. Advanced protocol settings: Signing Certificate authentik Self-signed Certificate; Sign assertion on; Sign response off; Service Provider Binding Post; NameID Property Mapping authentik default SAML Mapping: Email; Property Mappings only the four SSO ones.
6. Bindings: bind app-admin (order 0), app-editor (10), app-viewer (20), failure result Don't pass.
7. Submit. Applications, Providers, open the provider, Metadata, Download. Move the file to `sample-app/idp/idp_metadata.xml`.
8. Terminal: `cd ~/saml-sso-assignment/sample-app && docker compose restart sample-app`
9. Check the tile: log in as alice at `https://localhost:9443/` and show the Sample App tile.

Time yourself in rehearsal. If you are running late, skip explaining the property mappings (they already exist) and say they are reused across applications.

## Segment 3: SAML value verification (5 min)
1. Incognito window, open SAML-tracer, go to `https://localhost:5443/`, click Login with SSO, log in as alice.
2. In SAML-tracer select the POST to /saml/acs, open the SAML tab. Walk through:
   - Issuer: the authentik provider URL; the app compares it with the IdP metadata.
   - Destination: the ACS URL; wrong destination is rejected.
   - InResponseTo: matches the AuthnRequest ID (SP-initiated only).
   - Audience: the app Entity ID; stops other apps from accepting this assertion.
   - NameID: alice's email; stable, readable identifier.
   - Attributes: email, firstName, lastName, role.
   - NotBefore and NotOnOrAfter: validity window.
   - Signature: RSA-SHA256, digest SHA-256, checked with the IdP certificate from the metadata.
3. Open `https://localhost:5443/profile` and show the same values on the app side.

## Segment 4: RBAC walkthrough (10 min)
Close the incognito window between users (this clears the app and IdP sessions).
- alice: login at the app (SP-initiated), /profile, /general allowed, /admin allowed. New tab: dashboard tile (IdP-initiated).
- bob: dashboard tile, /general with Edit button, /admin returns 403. Type `https://localhost:5443/admin` directly to show direct URL access is blocked.
- carol: /general read-only, /admin 403.
- dave: dashboard shows No Applications available. Open `https://localhost:5443/general`: authentik denies him. Say: "The IdP blocks him with the group binding; even if he got through, the empty role would give a 403 in the app."

Point out: the 403 comes from the server, not from hidden buttons, and roles come from the assertion, not from code.

## Segment 5: Negative tests (5 min)
1. Tampered: incognito, DevTools Network tab with Keep log, log in as carol, filter `acs`, right-click the row, Copy, Copy as cURL. In Terminal (within 2 minutes): `./tools/test-tamper.sh`. Expect HTTP 403 and "Signature validation failed".
2. Unsigned: `./tools/test-unsigned.sh`. Expect HTTP 403.
3. Expired: `./tools/test-expired.sh`. Expect HTTP 403 and "Could not validate timestamp: expired".
4. Disabled user: authentik, Directory, Users, edit bob, turn Is active off, try to log in as bob in a fresh incognito window (refused). Turn Is active back on.
5. Role change: move carol from app-viewer to app-editor, log in as carol, /profile shows Editor. Move her back.

If the tamper test fails because more than 2 minutes passed, repeat the login and capture. If time is short, show bob disabled and the expired replay, and point to the recordings for the rest.

## Segment 6: Q&A (5 min)
Likely questions and short answers:
- Why sign the assertion and not the response? authentik signs the assertion by default; the assertion carries the identity, and the app requires it signed. Signing both is stricter and an option.
- What if the app did not check the signature? Anyone could edit the role in the browser POST and become Admin. The tamper test shows the check works.
- What is the audience check for? It binds the assertion to one application, so a token issued for another app cannot be replayed here.
- Why email as NameID? Unique and readable. A persistent identifier is better in production because emails change.
- Can a captured response be replayed? Inside its validity window, yes: there is no replay cache. Mitigation: short lifetime, HTTPS; production fix: store used assertion IDs.
- What is different about IdP-initiated login? No request, so no InResponseTo to match; the other checks still run. It is more exposed to login CSRF, so some teams disable it.
- Logout? Local only. The IdP session stays active. Fix: Single Logout.
- Certificate rotation? Metadata is a static file now; rotation means re-downloading it. Production: publish old and new certificates, load metadata from the URL.
- What if a user is in two groups? Two role values are sent and the app allows access if any role is allowed.
- Role change for a logged-in user? Applies at next login; SCIM or short sessions would shorten the gap.
- How would you add MFA for Admin only? An authentik policy bound to the application or flow that requires an MFA stage for members of app-admin.
- How would a second application be onboarded? docs/onboarding-runbook.md: collect values, create group and provider, bind groups, give the app the IdP metadata, run the checklist.
- What would you do for production? HA and database backups, real certificates, SLO, replay cache, MFA, central logging, secrets manager, SCIM.

## If something breaks
- App shows an error after login: `docker compose logs --tail 30 sample-app` shows the rejection reason.
- Metadata error: `idp/idp_metadata.xml` is missing or empty; re-download it and `docker compose restart sample-app`.
- A user keeps an old session: close all incognito windows.
- Time is running out: skip repeating steps and show the recordings (link in docs/test-evidence.md).
