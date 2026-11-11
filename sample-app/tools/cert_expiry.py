"""Prints subject and expiry of the IdP signing certificate found in idp/idp_metadata.xml."""
import re, subprocess, sys
xml = open("idp/idp_metadata.xml", encoding="utf-8").read()
certs = re.findall(r"<ds:X509Certificate>(.*?)</ds:X509Certificate>", xml, re.S)
if not certs:
    sys.exit("No certificate found in idp/idp_metadata.xml")
pem = "-----BEGIN CERTIFICATE-----\n" + "".join(certs[0].split()) + "\n-----END CERTIFICATE-----\n"
out = subprocess.run(["openssl", "x509", "-noout", "-subject", "-enddate"],
                     input=pem, text=True, capture_output=True)
print(out.stdout or out.stderr)
