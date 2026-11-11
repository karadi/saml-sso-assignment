import os
from functools import wraps, lru_cache

from flask import Flask, request, session, redirect, url_for, render_template_string
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from onelogin.saml2.settings import OneLogin_Saml2_Settings

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Which role names may use which page. The user -> role assignment itself
# comes from the SAML assertion (IdP groups), never from this code.
ADMIN_ROLES = {"Admin"}
GENERAL_ROLES = {"Admin", "Editor", "Viewer"}
EDIT_ROLES = {"Admin", "Editor"}


@lru_cache(maxsize=1)
def saml_settings():
    base = os.environ.get("SP_BASE_URL", "https://localhost:5443").rstrip("/")
    meta_file = os.environ.get("IDP_METADATA_FILE", "/idp/idp_metadata.xml")
    with open(meta_file, "r", encoding="utf-8") as f:
        idp = OneLogin_Saml2_IdPMetadataParser.parse(f.read())
    return {
        "strict": True,
        "debug": False,
        "sp": {
            "entityId": f"{base}/saml/metadata",
            "assertionConsumerService": {
                "url": f"{base}/saml/acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        },
        "idp": idp["idp"],
        "security": {
            "authnRequestsSigned": False,
            "wantAssertionsSigned": True,   # unsigned assertions are rejected
            "wantMessagesSigned": False,    # authentik signs the assertion by default
            "wantNameId": True,
            "wantAttributeStatement": True,
            "rejectDeprecatedAlgorithm": True,
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
            "requestedAuthnContext": False,
        },
    }


def prepare_request():
    return {
        "https": "on",
        "http_host": request.host,
        "script_name": request.path,
        "get_data": request.args.copy(),
        "post_data": request.form.copy(),
    }


def init_auth():
    return OneLogin_Saml2_Auth(prepare_request(), saml_settings())


def logged_in():
    return "nameid" in session


def has_role(allowed):
    return any(r in allowed for r in session.get("roles", []))


def require_roles(allowed):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not logged_in():
                return redirect(url_for("saml_login"))
            if not has_role(allowed):
                return page("Access denied", "403 Forbidden",
                            f"Your role(s) {session.get('roles') or ['none']} "
                            f"do not allow access to this page."), 403
            return view(*args, **kwargs)
        return wrapper
    return decorator


TEMPLATE = """
<!doctype html><html><head><meta charset="utf-8"><title>{{ title }}</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 16px;color:#222}
 nav a{margin-right:14px} .box{border:1px solid #ccc;border-radius:8px;padding:16px;margin:16px 0}
 table{border-collapse:collapse;width:100%} td,th{border:1px solid #ddd;padding:6px 10px;text-align:left}
 .err{color:#b00020} .btn{padding:8px 14px;background:#2a5bd7;color:#fff;border-radius:6px;text-decoration:none}
 button{padding:8px 14px}
</style></head><body>
<nav>
 <a href="/">Home</a>
 {% if user %}<a href="/general">General</a><a href="/admin">Admin</a><a href="/profile">Profile</a>
 <a href="/logout">Logout ({{ user }})</a>{% endif %}
</nav><hr>
<h1>{{ heading }}</h1>
{% if msg %}<p class="{{ 'err' if status == 403 else '' }}">{{ msg }}</p>{% endif %}
{% if kind == 'home' %}
  {% if user %}<p>Logged in as <b>{{ user }}</b>. Roles: <b>{{ roles or 'none' }}</b></p>
  {% else %}<p><a class="btn" href="/saml/login">Login with SSO</a></p>{% endif %}
{% elif kind == 'general' %}
  <div class="box"><p>General page: visible to Admin, Editor and Viewer.</p>
  {% if can_edit %}<p><button>Edit content</button> (Editor/Admin only)</p>
  {% else %}<p>Read-only view.</p>{% endif %}</div>
{% elif kind == 'admin' %}
  <div class="box"><p>Admin page: only the Admin role can see this.</p></div>
{% elif kind == 'profile' %}
  <table><tr><th>Field</th><th>Value</th></tr>
  <tr><td>NameID</td><td>{{ nameid }}</td></tr>
  <tr><td>NameID format</td><td>{{ nameid_format }}</td></tr>
  {% for k in ['email','firstName','lastName','role'] %}
  <tr><td>{{ k }}</td><td>{{ attrs.get(k, []) | join(', ') }}</td></tr>{% endfor %}
  <tr><td>Session index</td><td>{{ session_index }}</td></tr></table>
  <h3>All attributes received</h3><pre>{{ attrs }}</pre>
{% endif %}
</body></html>
"""


def page(heading, msg=None, status=200, kind="msg", title=None, **extra):
    return render_template_string(
        TEMPLATE, title=title or heading, heading=heading, msg=msg, status=status,
        kind=kind, user=session.get("email") or session.get("nameid"),
        roles=session.get("roles", []), **extra)


@app.get("/")
def home():
    return page("SAML Sample Application", kind="home")


@app.get("/general")
@require_roles(GENERAL_ROLES)
def general():
    return page("General page", kind="general", can_edit=has_role(EDIT_ROLES))


@app.get("/admin")
@require_roles(ADMIN_ROLES)
def admin():
    return page("Admin page", kind="admin")


@app.get("/profile")
def profile():
    if not logged_in():
        return redirect(url_for("saml_login"))
    return page("SAML profile (debug)", kind="profile",
                nameid=session["nameid"], nameid_format=session.get("nameid_format"),
                attrs=session.get("attrs", {}), session_index=session.get("session_index"))


# ---- SAML endpoints -------------------------------------------------------
@app.get("/saml/login")
def saml_login():
    auth = init_auth()
    url = auth.login(return_to=url_for("home", _external=True))
    session["authn_request_id"] = auth.get_last_request_id()
    return redirect(url)


@app.post("/saml/acs")
def saml_acs():
    auth = init_auth()
    # SP-initiated: checks InResponseTo. IdP-initiated: request id is None.
    auth.process_response(request_id=session.pop("authn_request_id", None))
    errors = auth.get_errors()
    if errors or not auth.is_authenticated():
        reason = auth.get_last_error_reason() or ""
        app.logger.warning("SAML login rejected: %s %s", errors, reason)
        return page("Login failed", f"SAML response rejected: {', '.join(errors)} {reason}",
                    status=403), 403
    attrs = auth.get_attributes()
    session.clear()
    session["nameid"] = auth.get_nameid()
    session["nameid_format"] = auth.get_nameid_format()
    session["session_index"] = auth.get_session_index()
    session["attrs"] = attrs
    session["email"] = (attrs.get("email") or [auth.get_nameid()])[0]
    session["roles"] = attrs.get("role", [])
    return redirect(url_for("home"))


@app.get("/saml/metadata")
def saml_metadata():
    settings = OneLogin_Saml2_Settings(saml_settings(), sp_validation_only=True)
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    if errors:
        return ", ".join(errors), 500
    return metadata, 200, {"Content-Type": "text/xml"}


@app.get("/logout")
def logout():
    # Local logout only (no SLO). The IdP session stays active - documented limitation.
    session.clear()
    return redirect(url_for("home"))
