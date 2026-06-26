import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm

def render_80_year_pdf(user_name, total_weeks_lived, artwork_style="skull"):
    """Draws a meticulously balanced, uncompromised 80-year archival map on an A3 canvas."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    width, height = A3

    # Fixed geometry configs optimized for A3 framing safety
    expected_life = 80
    box_size = 2.8*mm          
    padding = 0.9*mm          
    decade_gap = 4.0*mm 
    start_x = 54*mm
    header_y = height - 32*mm  
    grid_start_y = header_y - 20*mm
    
    num_decade_gaps = (expected_life - 1) // 10
    total_grid_height = (expected_life * (box_size + padding)) + (num_decade_gaps * decade_gap)
    grid_end_y = grid_start_y - total_grid_height
    box_bottom = grid_end_y - 18*mm
    
    gap_between_halves = 8*mm
    total_grid_width = (52 * box_size) + (50 * padding) + gap_between_halves
    end_of_grid_x = start_x + total_grid_width

    # --- THE MODULAR BACKGROUND SELECTION ---
    if artwork_style == "skull":
        image_file = None
        for name in ["skull.png", "Skull.png", "skull.jpg", "Skull.jpg"]:
            if os.path.exists(name): image_file = name; break
            
        if image_file:
            c.saveState()
            c.setFillAlpha(0.24) 
            c.drawImage(image_file, (width - 260*mm)/2 + 12*mm, 196*mm - (336*mm / 2), 
                        width=260*mm, height=336*mm, mask='auto')
            c.restoreState()
            
    elif artwork_style == "hourglass":
        # Future Expansion Area: Write custom ReportLab paths to draw a minimalist vectors geometric hourglass
        pass

    # --- VERTICAL TITLE SPINE ---
    c.setFont("Times-Bold", 42) 
    c.saveState()
    c.translate(22*mm, 196*mm)
    c.rotate(90)
    c.drawCentredString(0, 0, "M  E  M  E  N  T  O     M  O  R  I")
    c.restoreState()

    # --- OUTER BOUNDING BOX ---
    c.setLineWidth(0.6)
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(start_x - 16*mm, box_bottom, (end_of_grid_x - start_x) + 40*mm, (header_y + 8*mm - box_bottom), fill=0, stroke=1)

    # --- MATRIX GRID DRAW ENGINE ---
    current_y = grid_start_y
    epochs = {10: "SPRING: LEARNING", 30: "SUMMER: ACTION", 50: "AUTUMN: HARVEST", 70: "WINTER: WISDOM"}

    for year in range(1, expected_life + 1):
        if year > 1 and (year-1) % 10 == 0: 
            current_y -= decade_gap 
        
        if year % 5 == 0:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            c.drawRightString(start_x - 6*mm, current_y + (box_size * 0.15), str(year))

        if year == 1:
            c.setFont("Helvetica", 6)
            c.setFillColorRGB(0, 0, 0)
            for w_num in [10, 20, 30, 40, 50]:
                x_idx = w_num - 1
                off = (x_idx * (box_size + padding))
                if x_idx >= 26: off += gap_between_halves
                c.drawCentredString(start_x + off + (box_size/2), current_y + 5*mm, str(w_num))

        if year in epochs:
            c.saveState()
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColorRGB(0, 0, 0)
            c.translate(end_of_grid_x + 8*mm, current_y - (box_size / 2))
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

    # --- CANVAS TYPOGRAPHY LAYERS ---
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16) 
    c.drawRightString(end_of_grid_x, header_y, user_name.upper() if user_name else "MATRIX MAP")
    c.setFont("Helvetica", 9)
    c.drawRightString(end_of_grid_x, header_y - 6*mm, f"ARCHIVAL MAP | {expected_life} YEAR POTENTIAL")
    
    c.setFont("Times-Italic", 11)
    c.drawString(start_x - 12*mm, box_bottom + 12*mm, '"It is not that we have a short time to live,')
    c.drawString(start_x - 12*mm, box_bottom + 7*mm, 'but that we waste a lot of it." - Seneca')
    c.drawRightString(width - start_x + 12*mm, box_bottom + 12*mm, '"Very little is needed to make a happy life;')
    c.drawRightString(width - start_x + 12*mm, box_bottom + 7*mm, 'it is all within yourself." - Marcus Aurelius')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()