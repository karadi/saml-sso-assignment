# Configuration reference

## Service Provider (sample app)
| Item | Value |
|---|---|
| Entity ID / Audience | https://localhost:5443/saml/metadata |
| ACS URL (binding) | https://localhost:5443/saml/acs (HTTP-POST) |
| Single Logout URL | Not implemented (local logout only) |
| SP metadata XML | https://localhost:5443/saml/metadata |
| NameID | email, format urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress |

## Identity Provider (authentik)
| Item | Value |
|---|---|
| IdP Entity ID / Issuer | https://localhost:9443/application/saml/sample-app/metadata/ |
| SSO URL | https://localhost:9443/application/saml/sample-app/sso/binding/redirect/ (confirm in sample-app/idp/idp_metadata.xml) |
| IdP metadata | sample-app/idp/idp_metadata.xml (downloaded from the provider page) |
| Signing certificate | authentik Self-signed Certificate. Expiry: run `python3 sample-app/tools/cert_expiry.py` from the sample-app folder and Nov 7 09:24:18 2027 GMT |
| App HTTPS certificate | Generated on first start in sample-app/certs, valid 365 days, expires Nov 7 12:12:14 2027 GMT. Check: `openssl x509 -in sample-app/certs/server.crt -noout -enddate` |

## Assertion settings
| Item | Value |
|---|---|
| Signature | Assertion signed, RSA-SHA256, digest SHA-256 (response not signed) |
| Validity | authentik default window; the app validates NotBefore / NotOnOrAfter |
| Validations in the app | Signature, Issuer, Audience, Destination (ACS URL), InResponseTo (SP-initiated), time window |

## Attribute mappings
| SAML attribute | Source in authentik |
|---|---|
| email | user email |
| firstName | first word of the user's Name |
| lastName | remainder of the user's Name |
| role | group name mapped to role |

## Group to role mapping
| Group | Role |
|---|---|
| app-admin | Admin |
| app-editor | Editor |
| app-viewer | Viewer |

## Application access (bindings)
Group bindings on the application: app-admin (order 0), app-editor (10), app-viewer (20), failure result "Don't pass".
Users in none of these groups (dave) do not see the tile and cannot start a login.

## Why NameID = email
Unique per user, readable in logs and in the debug page, and the same value the IdP already stores.
Trade-off: if an email address changes, the identifier changes. A persistent identifier avoids that and is the better choice for production.
