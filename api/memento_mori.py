from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import io
import os

# Import your ReportLab dependencies
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm

def build_pdf_buffer(user_name, user_age):
    """Generates the exact ReportLab PDF matrix directly into memory buffer."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    width, height = A3

    # --- 1. GEOMETRY: Calibrated for year/week labels ---
    start_x = 60*mm 
    box_size = 3.0*mm         
    padding = 1.0*mm          
    gap_between_halves = 8*mm 
    decade_gap = 4.3*mm 
    total_grid_width = (52 * box_size) + (50 * padding) + gap_between_halves
    end_of_grid_x = start_x + total_grid_width
    
    header_y = height - 25*mm 
    grid_start_y = header_y - 25*mm 
    total_grid_height = (80 * (box_size + padding)) + (7 * decade_gap)
    grid_end_y = grid_start_y - total_grid_height
    box_bottom = grid_end_y - 18*mm 

    # --- 2. BACKGROUND IMAGE ---
    image_file = None
    # Look for asset file in the root directory relative to this script
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

    # --- 3. VERTICAL TITLE SPINE ---
    c.setFont("Times-Bold", 42) 
    c.saveState()
    c.translate(25*mm, height / 2 + 20*mm) 
    c.rotate(90)
    c.drawCentredString(0, 0, "M  E  M  E  N  T  O     M  O  R  I")
    c.restoreState()

    # --- 4. OUTER BOX ---
    c.setLineWidth(0.6)
    c.rect(start_x - 18*mm, box_bottom, (end_of_grid_x - start_x) + 40*mm, (header_y + 8*mm - box_bottom))

    # --- 5. THE LIFE GRID & LABELS ---
    current_y = grid_start_y
    total_weeks_lived = int(user_age * 52)
    epochs = {
        10: "SPRING: LEARNING", 
        30: "SUMMER: ACTION", 
        50: "AUTUMN: HARVEST", 
        70: "WINTER: WISDOM"
    }

    for year in range(1, 81):
        if year > 1 and (year-1) % 10 == 0: 
            current_y -= decade_gap 
        
        # YEAR LABELS (Left Side) 
        if year % 5 == 0:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            c.drawRightString(start_x - 6*mm, current_y + 0.8*mm, str(year))

        # WEEK LABELS (Top Row Only) 
        if year == 1:
            c.setFont("Helvetica", 6)
            c.setFillColorRGB(0, 0, 0)
            for w_num in [10, 20, 30, 40, 50]:
                x_idx = w_num - 1
                off = (x_idx * (box_size + padding))
                if x_idx >= 26: off += gap_between_halves
                c.drawCentredString(start_x + off + (box_size/2), current_y + 6*mm, str(w_num))

        # EPOCH LABELS (Right Side)
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

    # --- 6. HEADER & QUOTES ---
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16) 
    c.drawRightString(end_of_grid_x, header_y, user_name.upper())
    c.setFont("Helvetica", 9)
    c.drawRightString(end_of_grid_x, header_y - 6*mm, "ARCHIVAL MAP | 80 YEAR POTENTIAL")
    
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
        # Parse inputs
        query_components = parse_qs(urlparse(self.path).query)
        user_name = query_components.get("name", [None])[0]
        user_age_str = query_components.get("age", [None])[0]

        # 1. UI Form: Serve mobile responsive HTML if data parameters are empty
        if not user_name or not user_age_str:
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
                    input { padding: 14px; font-size: 16px; width: 100%; margin-bottom: 20px; border: 1px solid #444; background: #222; color: #fff; border-radius: 8px; box-sizing: border-box; }
                    button { padding: 14px; font-size: 16px; background: #fff; color: #000; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
                    p { color: #888; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h2 style="letter-spacing: 2px;">MEMENTO MORI</h2>
                    <p>Generate your custom high-resolution archival life calendar blueprint.</p>
                    <form action="/" method="get">
                        <input type="text" name="name" placeholder="Full Name" required><br>
                        <input type="number" name="age" placeholder="Current Age" min="0" max="80" required><br>
                        <button type="submit">Generate PDF Map</button>
                    </form>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_form.encode('utf-8'))
            return

        # 2. PDF Processing: Generate and stream the document directly back
        try:
            user_age = float(user_age_str)
            pdf_data = build_pdf_buffer(user_name, user_age)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/pdf')
            # Tells the phone browser to view it inside the window cleanly
            self.send_header('Content-Disposition', f'inline; filename="memento_mori_{user_name}.pdf"')
            self.end_headers()
            
            self.wfile.write(pdf_data)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server Error occurred processing PDF: {str(e)}".encode('utf-8'))
        return