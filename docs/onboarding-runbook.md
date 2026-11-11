# Onboarding runbook: adding the next application

## A. Information to collect from the application owner
| Item | Example |
|---|---|
| Application name and owner contact | Sample App, owner name |
| SP Entity ID / Audience URI | https://app2.example.test/saml/metadata |
| ACS URL and binding | https://app2.example.test/saml/acs, HTTP-POST |
| Single Logout URL (if any) | optional |
| SP metadata XML or URL | preferred over typing values by hand |
| NameID format the app expects | email or persistent |
| Required attributes (exact names) | email, firstName, lastName, role |
| Roles the app understands | Admin, Editor, Viewer |
| Who should get which role | list of users or groups |
| Signing requirements | assertion signed, SHA-256; does the app also require signed responses |
| SP-initiated login supported | yes/no and start URL |
| HTTPS certificate of the app | trusted by browsers? |

## B. Steps in authentik (admin interface, https://localhost:9443/if/admin/)
1. **Groups**: Directory, Groups, New Group. Create one group per role (for example `app2-admin`). Add users.
2. **Property mappings** (once only): Customization, Property Mappings, New, SAML Provider Property Mapping.
   Reuse `SSO email`, `SSO firstName`, `SSO lastName`. For a new role set, copy `SSO role` and change the group-to-role table in its expression.
3. **Application and provider**: Applications, Applications, Create. Set name and slug, type SAML Provider, then:
   - Authorization flow: default-provider-authorization-implicit-consent
   - ACS URL and Audience from section A
   - Advanced protocol settings: Signing Certificate = authentik Self-signed Certificate; Sign assertion on; Sign response off;
     Service Provider Binding = Post; NameID Property Mapping = authentik default SAML Mapping: Email;
     Property Mappings = only the four SSO mappings.
4. **Bindings**: open the application, Policy / Group / User Bindings tab, bind each role group (Failure result: Don't pass).
5. **IdP metadata**: Applications, Providers, open the provider, Metadata, Download. Give the file (or the metadata URL) to the app owner.
6. **Configure the app** with the IdP Entity ID, SSO URL and signing certificate (from the metadata). Require signed assertions.

## C. Verification checklist
- [ ] SP-initiated login works
- [ ] IdP-initiated login from the dashboard tile works
- [ ] Debug/profile page shows NameID, email, firstName, lastName, role
- [ ] Each role reaches only its pages; restricted URLs return 403 when opened directly
- [ ] A user with no role sees no tile and is denied
- [ ] Disabled user is blocked
- [ ] Role change in authentik applies on next login
- [ ] Tampered and expired assertions are rejected
- [ ] Values recorded in docs/config-reference.md and certificate expiry noted
