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
    """Generates a dynamic ReportLab PDF matrix scaling smoothly up to 100 years."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    width, height = A3

    # --- Precision Math Engine ---
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        birth_date = datetime(2000, 1, 1)

    # Hardcoded to current date anchor in 2026
    current_date = datetime(2026, 6, 26)
    
    # 1. Compute exact completed years
    age_years = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age_years -= 1
        
    # 2. Pinpoint most recent birthday
    try:
        last_birthday = birth_date.replace(year=current_date.year)
        if last_birthday > current_date:
            last_birthday = birth_date.replace(year=current_date.year - 1)
    except ValueError:
        # Edge case handler for February 29 leap year births
        last_birthday = datetime(current_date.year, 2, 28)
        if last_birthday > current_date:
            last_birthday = datetime(current_date.year - 1, 2, 28)

    # 3. Compute exact weeks elapsed since that last birthday
    days_since_birthday = (current_date - last_birthday).days
    weeks_this_year = int(days_since_birthday / 7)
    
    # 4. Sum absolute structural weeks to fill on the canvas layout
    total_weeks_lived = (age_years * 52) + weeks_this_year

    # --- AUTOSCALING GEOMETRY ENGINE ---
    # Shrinks font and structural components slightly if moving beyond 80 years to prevent page overflow
    if expected_life > 80:
        box_size = 2.4*mm
        padding = 0.8*mm
        decade_gap = 3.5*mm
    else:
        box_size = 3.0*mm         
        padding = 1.0*mm          
        decade_gap = 4.3*mm 

    start_x = 60*mm 
    gap_between_halves = 8*mm 
    
    total_grid_width = (52 * box_size) + (50 * padding) + gap_between_halves
    end_of_grid_x = start_x + total_grid_width
    
    header_y = height - 25*mm 
    grid_start_y = header_y - 25*mm 
    
    num_decade_gaps = (expected_life - 1) // 10
    total_grid_height = (expected_life * (box_size + padding)) + (num_decade_gaps * decade_gap)
    grid_end_y = grid_start_y - total_grid_height
    box_bottom = grid_end_y - 18*mm 

    # --- BACKGROUND IMAGE LAYER ---
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

    # --- BOUNDING BOX BORDER ---
    c.setLineWidth(0.6)
    c.rect(start_x - 18*mm, box_bottom, (end_of_grid_x - start_x) + 40*mm, (header_y + 8*mm - box_bottom))

    # --- GRID RENDER LOOP ---
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
        
        # Row Labels (Ages)
        if year % 5 == 0:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            c.drawRightString(start_x - 6*mm, current_y + (box_size * 0.2), str(year))

        # Column Labels (Weeks - Printed on First Row Only)
        if year == 1:
            c.setFont("Helvetica", 6)
            c.setFillColorRGB(0, 0, 0)
            for w_num in [10, 20, 30, 40, 50]:
                x_idx = w_num - 1
                off = (x_idx * (box_size + padding))
                if x_idx >= 26: off += gap_between_halves
                c.drawCentredString(start_x + off + (box_size/2), current_y + 6*mm, str(w_num))

        # Epoch Markers
        if year in epochs:
            c.saveState()
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColorRGB(0, 0, 0)
            c.translate(end_of_grid_x + 8*mm, current_y - (decade_gap / 2) - 1.5*mm)
            c.rotate(-90)
            c.drawCentredString(0, 0, epochs[year])
            c.restoreState()

        # Box Allocator
        for week in range(52):
            x_offset = (week * (box_size + padding))
            if week >= 26: x_offset += gap_between_halves
            x = start_x + x_offset
            
            if ((year - 1) * 52) + week < total_weeks_lived:
                # Lived week: Filled block
                c.setFillColorRGB(0, 0, 0)
                c.rect(x, current_y, box_size, box_size, fill=1, stroke=0)
            else:
                # Remaining week: Empty border box
                c.setStrokeColorRGB(0.2, 0.2, 0.2)
                c.setLineWidth(0.1)
                c.rect(x, current_y, box_size, box_size, fill=0, stroke=1)
        current_y -= (box_size + padding)

    # --- CANVAS HEADERS & QUOTATION LAYERS ---
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

        # 1. HTML FORM RENDERING
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
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; padding: 20px; background: #111; color: #fff; margin: 0; }
                    .card { background: #1a1a1a; padding: 30px; border-radius: 16px; max-width: 360px; margin: 20px auto; border: 1px solid #333; box-sizing: border-box; }
                    label { display: block; text-align: left; margin-bottom: 5px; color: #aaa; font-size: 14px; }
                    input { padding: 14px; font-size: 16px; width: 100%; margin-bottom: 20px; border: 1px solid #444; background: #222; color: #fff; border-radius: 8px; box-sizing: border-box; }
                    input[type="date"] { color-scheme: dark; } 
                    
                    .slider-container { margin-bottom: 25px; text-align: left; }
                    .slider-val { float: right; color: #00ffcc; font-weight: bold; font-size: 16px; }
                    input[type="range"] { -webkit-appearance: none; width: 100%; background: #333; height: 6px; border-radius: 3px; outline: none; margin-top: 8px; }
                    input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #fff; cursor: pointer; }
                    
                    button { padding: 14px; font-size: 16px; background: #fff; color: #000; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px; }
                    p { color: #888; font-size: 14px; line-height: 1.4; }

                    /* SCREEN OVERLAY VIEW FOR INTERACTIVE DOTS */
                    .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #111; z-index: 1000; flex-direction: column; overflow-y: auto; }
                    .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; background: #1a1a1a; border-bottom: 1px solid #333; position: sticky; top: 0; }
                    .close-btn { background: #333; color: white; border: 1px solid #444; padding: 8px 16px; font-size: 14px; font-weight: bold; border-radius: 6px; cursor: pointer; }
                    .download-btn { background: #00ffcc; color: #000; border: none; padding: 8px 16px; font-size: 14px; font-weight: bold; border-radius: 6px; cursor: pointer; text-decoration: none; }
                    
                    /* CSS GRID THAT AUTOMATICALLY FITS SMARTPHONE SCALINGS */
                    .grid-container { max-width: 450px; margin: 20px auto; padding: 10px; box-sizing: border-box; }
                    .life-grid { display: grid; grid-template-columns: repeat(52, 1fr); gap: 1px; background: #1a1a1a; padding: 10px; border-radius: 8px; border: 1px solid #333; }
                    .dot { aspect-ratio: 1; border-radius: 1px; background: #222; border: 1px solid rgba(255,255,255,0.05); }
                    .dot.lived { background: #00ffcc; border: none; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h2 style="letter-spacing: 2px; margin-bottom: 5px;">MEMENTO MORI</h2>
                    <p>Map your exact lifespan blueprint.</p>
                    
                    <form id="mapForm" style="margin-top: 25px;">
                        <label>Your Name</label>
                        <input type="text" id="name" placeholder="Full Name" required>
                        
                        <label>Your Birthday</label>
                        <input type="date" id="birthday" max="2026-12-31" required>
                        
                        <div class="slider-container">
                            <label>Target Lifespan: <span class="slider-val" id="valDisplay">80</span></label>
                            <input type="range" id="lifespan" min="50" max="100" value="80" oninput="document.getElementById('valDisplay').innerText = this.value">
                        </div>
                        
                        <button type="submit">Visualize My Life</button>
                    </form>
                </div>

                <div id="pdfModal" class="modal">
                    <div class="modal-header">
                        <button class="close-btn" onclick="closeModal()">✕ Back</button>
                        <span id="titleDisplay" style="font-weight: bold; letter-spacing: 1px;">MY MATRIX</span>
                        <a id="downloadLink" class="download-btn" href="#" target="_blank">Print PDF 📥</a>
                    </div>
                    
                    <div class="grid-container">
                        <p style="text-align: left; margin-bottom: 5px; color: #aaa;">Your lived weeks are highlighted below:</p>
                        <div id="htmlGrid" class="life-grid"></div>
                    </div>
                </div>

                <script>
                    document.getElementById('mapForm').addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        const name = document.getElementById('name').value;
                        const bday = document.getElementById('birthday').value;
                        const life = parseInt(document.getElementById('lifespan').value);
                        
                        // 1. Setup the High-Res PDF download link attachment button
                        const downloadUrl = `/?name=${encodeURIComponent(name)}&birthday=${bday}&lifespan=${life}`;
                        document.getElementById('downloadLink').href = downloadUrl;
                        document.getElementById('titleDisplay').innerText = name.toUpperCase();

                        // 2. Compute exact weeks lived for screen rendering logic
                        const birthDate = new Date(bday);
                        const currentDate = new Date('2026-06-26');
                        const diffTime = Math.max(0, currentDate - birthDate);
                        const totalWeeksLived = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 7));
                        const totalTargetWeeks = life * 52;

                        // 3. Build the responsive grid array dynamically in HTML
                        const gridContainer = document.getElementById('htmlGrid');
                        gridContainer.innerHTML = ''; // Reset frame
                        
                        for (let i = 0; i < totalTargetWeeks; i++) {
                            const dot = document.createElement('div');
                            dot.classList.add('dot');
                            if (i < totalWeeksLived) {
                                dot.classList.add('lived');
                            }
                            gridContainer.appendChild(dot);
                        }

                        // Display full screen UI modal
                        document.getElementById('pdfModal').style.display = 'flex';
                    });

                    function closeModal() {
                        document.getElementById('pdfModal').style.display = 'none';
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_form.encode('utf-8'))
            return

        # 2. APPLICATION/PDF STRINGS RESPONSE ENGINE
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
            self.wfile.write(f"Server Error: {str(e)}".encode('utf-8'))
        return