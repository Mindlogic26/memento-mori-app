from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
import os

def generate_memento_mori_final(filename, name, current_age):
    c = canvas.Canvas(filename, pagesize=A3)
    width, height = A3

    # 1. GRID GEOMETRY CALCULATIONS
    start_x = 55*mm 
    box_size = 3.0*mm         
    padding = 1.0*mm          
    gap_between_halves = 8*mm 
    decade_gap = 4.3*mm 
    total_grid_width = (52 * box_size) + (50 * padding) + gap_between_halves
    end_of_grid_x = start_x + total_grid_width
    
    header_y = height - 25*mm 
    grid_start_y = header_y - 20*mm 
    total_grid_height = (80 * (box_size + padding)) + (7 * decade_gap)
    grid_end_y = grid_start_y - total_grid_height
    box_bottom = grid_end_y - 18*mm 

    # 2. IMAGE DISCOVERY (Looks for png or jpg)
    image_path = None
    for ext in ["skull.png", "Skull.png", "skull.jpg", "Skull.jpg"]:
        if os.path.exists(ext):
            image_path = ext
            break

    # 3. DRAW THE BACKGROUND IMAGE (Bottom-Anchored)
    if image_path:
        try:
            c.saveState()
            c.setFillAlpha(0.40) 
            img_w = 280*mm 
            img_h = 360*mm 
            c.drawImage(image_path, (width - img_w)/2 + 20*mm, box_bottom - 5*mm, 
                        width=img_w, height=img_h, mask='auto')
            c.restoreState()
        except Exception as e:
            print(f"Image error: {e}")
    else:
        print("Note: No skull image found in folder. Generating grid only.")

    # 4. VERTICAL SPINE
    c.setFont("Times-Bold", 42) 
    spine_text = "M  E  M  E  N  T  O     M  O  R  I"
    c.saveState()
    c.translate(22*mm, height / 2 + 20*mm) 
    c.rotate(90)
    c.drawCentredString(0, 0, spine_text)
    c.restoreState()

    # 5. OUTER BOX
    c.setLineWidth(0.6) 
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(start_x - 15*mm, box_bottom, (end_of_grid_x - start_x) + 37*mm, (header_y + 8*mm - box_bottom))

    # 6. THE GRID
    current_y = grid_start_y
    total_weeks_lived = int(current_age * 52)
    epoch_targets = {
        10: "SPRING: LEARNING", 30: "SUMMER: ACTION", 
        50: "AUTUMN: HARVEST", 70: "WINTER: WISDOM"
    }

    for year in range(1, 81):
        if year > 1 and (year-1) % 10 == 0: current_y -= decade_gap 
        
        if year in epoch_targets:
            c.saveState()
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColorRGB(0, 0, 0)
            c.translate(end_of_grid_x + 7*mm, current_y - (decade_gap / 2) - 1.5*mm)
            c.rotate(-90)
            c.drawCentredString(0, 0, epoch_targets[year])
            c.restoreState()

        for week in range(52):
            x_offset = (week * (box_size + padding))
            if week >= 26: x_offset += gap_between_halves
            x = start_x + x_offset
            week_id = ((year - 1) * 52) + week
            
            if week_id < total_weeks_lived:
                c.setFillColorRGB(0, 0, 0)
                c.rect(x, current_y, box_size, box_size, fill=1, stroke=0)
            else:
                c.setStrokeColorRGB(0.2, 0.2, 0.2)
                c.setLineWidth(0.1)
                c.rect(x, current_y, box_size, box_size, fill=0, stroke=1)
        current_y -= (box_size + padding)

    # 7. HEADER & STOIC QUOTES
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16) 
    c.drawRightString(end_of_grid_x, header_y, name.upper())
    
    c.setFont("Helvetica", 9)
    c.drawRightString(end_of_grid_x, header_y - 6*mm, "ARCHIVAL MAP | 80 YEAR POTENTIAL")
    
    c.setFont("Times-Italic", 11)
    # Seneca
    c.drawString(start_x, box_bottom + 8*mm, '"It is not that we have a short time to live,')
    c.drawString(start_x, box_bottom + 4*mm, 'but that we waste a lot of it." - Seneca')
    
    # Marcus Aurelius
    c.drawRightString(end_of_grid_x, box_bottom + 8*mm, '"Very little is needed to make a happy life;')
    c.drawRightString(end_of_grid_x, box_bottom + 4*mm, 'it is all within yourself." - Marcus Aurelius')

    c.showPage()
    c.save()
    print(f"Final PDF Created: {filename}")

# Launch
generate_memento_mori_final("Memento_Mori_Masterpiece_Final.pdf", "JOHN DOE", 32)