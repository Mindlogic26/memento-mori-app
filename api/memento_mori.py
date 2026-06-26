from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime
import io
import os

# Import ReportLab dependencies
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm

def build_pdf_buffer(user_name, birth_date_str, expected_life):
    """Generates a dynamic ReportLab PDF matrix scaling up to 100 years."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    width, height = A3

    # --- Precision Math Engine ---
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        birth_date = datetime(2000, 1, 1)

    current_date = datetime(2026, 6, 26)
    
    # 1. Age in completed years
    age_years = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age_years -= 1
        
    # 2. Most recent birthday
    try:
        last_birthday = birth_date.replace(year=current_date.year)
        if last_birthday > current_date:
            last_birthday = birth_date.replace(year=current_date.year - 1)
    except ValueError:
        last_birthday = datetime(current_date.year, 2, 28)
        if last_birthday > current_date:
            last_birthday = datetime(current_date.year - 1, 2, 28)

    # 3. Weeks lived since last birthday
    days_since_birthday = (current_date - last_birthday).days
    weeks_this_year = int(days_since_birthday / 7)
    
    # 4. Total absolute weeks to fill
    total_weeks_lived = (age_years * 52) + weeks_this_year

    # --- DYNAMIC GEOMETRY CONFIGURATION ---
    start_x = 60*mm 
    box_size = 3.0*mm         
    padding = 1.0*mm          
    gap_between_halves = 8*mm 
    decade_gap = 4.3*mm 
    
    total_grid_width = (52 * box_size) + (50 * padding) + gap_between_halves
    end_of_grid_x = start_x + total_grid_width
    
    header_y = height - 25*mm 
    grid_start_y = header_y - 25*mm 
    
    # Calculate variable grid height based on the user's input choice
    num_decade_gaps = (expected_life - 1) // 10
    total_grid_height = (expected_life * (box_size + padding)) + (num_decade_gaps * decade_gap)
    grid_end_y = grid_start_y - total_grid_height
    box_bottom = grid_end_y - 18*mm 

    # --- BACKGROUND IMAGE ---
    image_file = None
    for name in ["skull.png", "Skull.png", "skull.jpg", "Skull.jpg"]:
        if os.path.exists(name):
            image_file = name
            break

    if image_file:
        c.saveState()
        c.setFillAlpha(0.35) 
        img_w, img_h = 270*mm, 350*mm 
        c.drawImage(image_file, (width - img_w)/2 + 20*mm, box_bottom - 2*mm, 
                    width=img_w, height=img_h, mask='auto')
        c.restoreState()

    # --- VERTICAL TITLE SPINE ---
    c.setFont("Times-Bold", 42) 
    c.saveState()
    c.translate(25*mm, height / 2 + 20*mm) 
    c.rotate(90)
    c.drawCentredString(0, 0, "M  E  M  E  N  T  O     M  O  R  I")
    c.restoreState()

    # --- OUTER BOX ---
    c.setLineWidth(0.6)
    c.rect(start_x - 18*mm, box_bottom, (end_of_grid_x - start_x) + 40*mm, (header_y + 8*mm - box_bottom))

    # --- DYNAMIC LIFE GRID & LABELS ---
    current_y = grid_start_y
    epochs = {
        10: "SPRING: LEARNING", 
        30: "SUMMER: ACTION", 
        50: "AUTUMN: HARVEST", 
        70: "WINTER: WISDOM",
        90: "LATE WINTER: REFLECTION"
    }

    for year in range(1, expected_life + 1):
        if year > 1 and (year-1) % 10 == 0: 
            current_y -= decade_gap 
        
        if year % 5 == 0:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            c.drawRightString(start_x - 6*mm, current_y + 0.8*mm, str(year))

        if year == 1:
            c.setFont("Helvetica", 6)
            c.setFillColorRGB(0, 0, 0)
            for w_num in [10, 20, 30, 40, 50]:
                x_idx = w_num - 1
                off = (x_idx * (box_size + padding))
                if x_idx >= 26: off += gap_between_halves
                c.drawCentredString(start_x + off + (box_size/2), current_y + 6*mm, str(w_num))

        if year in epochs:
            c.saveState()
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColorRGB(0, 0, 0)
            c.translate(end_of_grid_x + 8*mm, current_y - (decade_gap / 2) - 1.5*mm)
            c.rotate(-90)
            c.drawCentredString(0, 0, epochs[year])
            c.restoreState()

        for week in range(52):
            x_offset = (week * (box_size + padding))
            if week >= 26: x_offset += gap_between_halves
            x = start_x + x_offset
            
            if ((year - 1) * 52) + week < total_weeks_lived:
                c.setFillColorRGB(0, 0, 0)
                c.rect(x, current_y, box_size, box_size, fill=1, stroke=0)
            else:
                c.setStrokeColorRGB(0.2, 0.2, 0.2)
                c.setLineWidth(0.1)
                c.rect(x, current_y, box_size, box_size, fill=0, stroke=1)
        current_y -= (box_size + padding)

    # --- HEADER & QUOTES ---
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16) 
    c.drawRightString(end_of_grid_x, header_y, user_name.upper())
    c.setFont("Helvetica", 9)
    c.drawRightString(end_of_grid_x, header_y - 6*mm, f"ARCHIVAL MAP | {expected_life} YEAR POTENTIAL")
    
    c.setFont("Times-Italic", 11)
    c.drawString(start_x, box_bottom + 8*mm, '"It is not that we have a short time to live,')
    c.drawString(start_x, box_bottom + 4*mm, 'but that we waste a lot of it." - Seneca')
    c.drawRightString(end_of_grid_x, box_bottom + 8*mm, '"Very little is needed to make a happy life;')
    c.drawRightString(end_of_grid_x, box_bottom + 4*mm, 'it is all within yourself." - Marcus Aurelius')

    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        user_name = query_components.get("name", [None])[0]
        birth_date = query_components.get("birthday", [None])[0]
        expected_life_str = query_components.get("lifespan", [None])[0]

        # 1. Updated UI Form with Mobile Sliders
        if not user_name or not birth_date or not expected_life_str:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_form = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; padding: 40px 20px; background: #111; color: #fff; }
                    .card { background: #1a1a1a; padding: 30px; border-radius: 16px; max-width: 360px; margin: 40px auto; border: 1px solid #333; }
                    label { display: block; text-align: left; margin-bottom: 5px; color: #aaa; font-size: 14px; }
                    input { padding: 14px; font-size: 16px; width: 100%; margin-bottom: 20px; border: 1px solid #444; background: #222; color: #fff; border-radius: 8px; box-sizing: border-box; }
                    input[type="date"] { color-scheme: dark; } 
                    
                    /* Range Slider CSS */
                    .slider-container { margin-bottom: 25px; text-align: left; }
                    .slider-val { float: right; color: #00ffcc; font-weight: bold; font-size: 16px; }
                    input[type="range"] { -webkit-appearance: none; width: 100%; background: #333; height: 6px; border-radius: 3px; outline: none; margin-top: 8px; }
                    input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #fff; cursor: pointer; }
                    
                    button { padding: 14px; font-size: 16px; background: #fff; color: #000; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px; }
                    p { color: #888; font-size: 14px; line-height: 1.4; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h2 style="letter-spacing: 2px; margin-bottom: 5px;">MEMENTO MORI</h2>
                    <p>Map your exact lifespan blueprint.</p>
                    <form action="/" method="get" style="margin-top: 25px;">
                        <label>Your Name</label>
                        <input type="text" name="name" placeholder="Full Name" required>
                        
                        <label>Your Birthday</label>
                        <input type="date" name="birthday" max="2026-12-31" required>
                        
                        <div class="slider-container">
                            <label>Target Lifespan: <span class="slider-val" id="valDisplay">80</span></label>
                            <input type="range" name="lifespan" min="50" max="100" value="80" id="lifeSlider" oninput="document.getElementById('valDisplay').innerText = this.value">
                        </div>
                        
                        <button type="submit">Generate Custom Map</button>
                    </form>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_form.encode('utf-8'))
            return

        # 2. Process custom data parameters
        try:
            expected_life = int(expected_life_str)
            pdf_data = build_pdf_buffer(user_name, birth_date, expected_life)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/pdf')
            self.send_header('Content-Disposition', f'inline; filename="memento_mori_{user_name}.pdf"')
            self.end_headers()
            
            self.wfile.write(pdf_data)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server Error occurred processing dynamic PDF: {str(e)}".encode('utf-8'))
        return