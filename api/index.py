import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Force Python to find modules in our project subdirectories on Vercel environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.calculator import calculate_life_metrics
from modules.layouts import render_80_year_pdf
from modules.verified import verify_license

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = urlparse(self.path)
        query = parse_qs(url_path.query)
        
        # Pull parameters dynamically
        action = query.get("action", [None])[0]
        name = query.get("name", [None])[0]
        birthday = query.get("birthday", [None])[0]
        license_key = query.get("license", [None])[0]
        artwork = query.get("artwork", ["skull"])[0]

        # 1. API Endpoint: Returns raw JSON calculations for your live interactive frontend stats cards
        if action == "metrics":
            metrics = calculate_life_metrics(birthday) if birthday else {}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            import json
            self.wfile.write(json.dumps(metrics).encode('utf-8'))
            return

        # 2. API Endpoint: Generates and serves the locked high-res PDF print file
        elif action == "download":
            if not verify_license(license_key):
                self.send_response(403)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write("Access Denied: Invalid or Expired Gumroad License.".encode('utf-8'))
                return
                
            metrics = calculate_life_metrics(birthday)
            pdf_data = render_80_year_pdf(name, metrics["weeks_spent"], artwork_style=artwork)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', f'attachment; filename="memento_mori_{name}.pdf"')
            self.end_headers()
            self.wfile.write(pdf_data)
            return

        # 3. Default Path: Render the HTML frontend form user interface template
        else:
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'interface.html')
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                html_content = "<h1>Template File Missing.</h1>"
                
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            return