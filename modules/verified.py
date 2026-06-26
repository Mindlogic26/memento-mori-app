import urllib.request
import urllib.parse
import json

GUMROAD_PRODUCT_PERMALINK = "YOUR_PRODUCT_PERMALINK" # Update this with your live link string

def verify_license(license_key):
    """Validates the customer's purchase token directly against Gumroad's security servers."""
    if not license_key or len(license_key.strip()) < 5:
        return False
        
    url = "https://api.gumroad.com/v2/licenses/verify"
    data = urllib.parse.urlencode({
        "product_permalink": GUMROAD_PRODUCT_PERMALINK,
        "license_key": license_key.strip()
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            # True if key is valid and hasn't been abused across multiple machines
            return res_data.get("success", False) and res_data.get("uses", 0) <= 10
    except Exception:
        return False