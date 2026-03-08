#!/usr/bin/env python3
"""
Generate all levels of DFDs for Fraud App Detection Using Sentiment Analysis.
Style: Fan-out layout matching reference DFDs (black background, white shapes).
Output: Docs/DFD/*.png
"""
import os
import sys
import math

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install Pillow: pip install pillow")
    sys.exit(1)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "Docs", "DFD")

# Config
W, H = 1000, 600
BG = (255, 255, 255)       # White background
FG = (0, 0, 0) # Black lines/text
FONT_NAME = "arial.ttf"


def get_font(size: int):
    try:
        return ImageFont.truetype(FONT_NAME, size)
    except OSError:
        try:
            return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
        except OSError:
            return ImageFont.load_default()


def draw_arrow(draw, x1, y1, x2, y2):
    """Draw line with arrow head at (x2, y2)."""
    draw.line([x1, y1, x2, y2], fill=FG, width=2)
    # Arrow head
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_len = 10
    angle1 = angle + math.pi * 0.85
    angle2 = angle - math.pi * 0.85
    x3 = x2 + arrow_len * math.cos(angle1)
    y3 = y2 + arrow_len * math.sin(angle1)
    x4 = x2 + arrow_len * math.cos(angle2)
    y4 = y2 + arrow_len * math.sin(angle2)
    draw.polygon([x2, y2, x3, y3, x4, y4], fill=FG)


def draw_entity(draw, x, y, w, h, label, font_size=12):
    """Rectangular entity."""
    draw.rectangle([x, y, x + w, y + h], outline=FG, width=2)
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2), label, fill=FG, font=font)
    return (x + w, y + h // 2)  # Return right connection point


def draw_process(draw, x, y, w, h, label, font_size=10):
    """Oval process."""
    draw.ellipse([x, y, x + w, y + h], outline=FG, width=2)
    font = get_font(font_size)
    lines = label.split("\n")
    line_h = int(font_size * 1.3)
    cx, cy = x + w // 2, y + h // 2
    start_y = cy - (len(lines) * line_h) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw // 2, start_y + i * line_h), line, fill=FG, font=font)
    return (x, y + h // 2), (x + w, y + h // 2)  # Left, Right connection points


def draw_datastore(draw, x, y, w, h, label, font_size=10):
    """Open-ended rectangle for data store."""
    # Top line
    draw.line([x, y, x + w, y], fill=FG, width=2)
    # Bottom line
    draw.line([x, y + h, x + w, y + h], fill=FG, width=2)
    # Left line (optional, some DFD styles omit right line)
    draw.line([x, y, x, y + h], fill=FG, width=2)
    
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2), label, fill=FG, font=font)
    return (x, y + h // 2)  # Left connection point


def draw_footer(draw, text):
    font = get_font(10)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((W // 2 - tw // 2, H - 30), text, fill=FG, font=font)


# --- Diagrams ---

def get_ellipse_point(x, y, w, h, y_offset=0, side='left'):
    """Calculate point on ellipse boundary for a given Y offset from center."""
    cx = x + w / 2
    cy = y + h / 2
    a = w / 2
    b = h / 2
    
    # Clamp offset to be inside ellipse
    if abs(y_offset) >= b:
        y_offset = (b - 1) if y_offset > 0 else -(b - 1)
        
    # Ellipse equation: x = cx +/- a * sqrt(1 - dy^2/b^2)
    dx = a * math.sqrt(1 - (y_offset / b) ** 2)
    
    if side == 'left':
        return (cx - dx, cy + y_offset)
    else:
        return (cx + dx, cy + y_offset)


def level_0_context():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Center Process
    pw, ph = 280, 120
    px, py = (W - pw) // 2, (H - ph) // 2
    pl, pr = draw_process(draw, px, py, pw, ph, "FRAUD APP DETECTION\nSYSTEM", 14)
    
    # Entities
    ew, eh = 100, 50
    ex1, ey1 = 100, py + (ph - eh) // 2
    ex2, ey2 = W - 100 - ew, py + (ph - eh) // 2
    
    er1 = draw_entity(draw, ex1, ey1, ew, eh, "USER", 12)
    # Admin on right needs left connection point logic, but draw_entity returns right.
    # Let's just calculate manually for simplicity or add return.
    draw_entity(draw, ex2, ey2, ew, eh, "ADMIN", 12)
    el2 = (ex2, ey2 + eh // 2)

    # Arrows
    # User <-> System
    draw_arrow(draw, er1[0], er1[1] - 10, pl[0], pl[1] - 10)
    draw_arrow(draw, pl[0], pl[1] + 10, er1[0], er1[1] + 10)
    
    # System <-> Admin
    draw_arrow(draw, pr[0], pr[1] - 10, el2[0], el2[1] - 10)
    draw_arrow(draw, el2[0], el2[1] + 10, pr[0], pr[1] + 10)

    draw_footer(draw, "Page 1 - Context Diagram (Level 0)")
    img.save(os.path.join(OUT_DIR, "dfd_level_0.png"))


def level_1_admin():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    # Admin -> Login -> System
    cy = H // 2
    er = draw_entity(draw, 50, cy - 25, 80, 50, "ADMIN")
    
    l_in, l_out = draw_process(draw, 180, cy - 25, 80, 50, "Login")
    draw_arrow(draw, er[0], er[1], l_in[0], l_in[1])
    
    s_in, s_out = draw_process(draw, 300, cy - 40, 140, 80, "Fraud App\nDetection\nSystem")
    draw_arrow(draw, l_out[0], l_out[1], s_in[0], s_in[1])
    
    # Fan out to sub-processes
    subs = ["User\nManagement", "Data\nManagement", "Reports\nManagement"]
    stores = ["users", "apps/reviews", "reports"]
    
    sy_start = cy - 120
    for i, sub in enumerate(subs):
        y = sy_start + i * 120
        sp_in, sp_out = draw_process(draw, 550, y - 30, 120, 60, sub)
        draw_arrow(draw, s_out[0], s_out[1], sp_in[0], sp_in[1])
        
        # Data store
        ds_in = draw_datastore(draw, 750, y - 20, 120, 40, stores[i])
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    draw_footer(draw, "Page 2 - Admin Level 1 DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_1_admin.png"))


def level_1_user():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    cy = H // 2
    er = draw_entity(draw, 40, cy - 25, 70, 50, "USER")
    
    l_in, l_out = draw_process(draw, 150, cy - 25, 70, 50, "Login")
    draw_arrow(draw, er[0], er[1], l_in[0], l_in[1])
    
    s_in, s_out = draw_process(draw, 260, cy - 40, 140, 80, "Fraud App\nDetection\nSystem")
    draw_arrow(draw, l_out[0], l_out[1], s_in[0], s_in[1])
    
    # Fan out
    subs = ["Register/\nProfile", "Dashboard/\nApps", "Submit\nReviews", "Run\nAnalysis", "View\nHistory", "Watchlist/\nInsights"]
    stores = ["users", "apps", "reviews", "analysis_runs", "history", "watchlist"]
    
    # 3 top, 3 bottom
    # Top
    for i in range(3):
        y = cy - 180 + i * 80
        sp_in, sp_out = draw_process(draw, 500, y - 25, 110, 50, subs[i])
        draw_arrow(draw, s_out[0], s_out[1], sp_in[0], sp_in[1])
        ds_in = draw_datastore(draw, 700, y - 20, 120, 40, stores[i])
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])
        
    # Bottom
    for i in range(3):
        y = cy + 60 + i * 80
        sp_in, sp_out = draw_process(draw, 500, y - 25, 110, 50, subs[i+3])
        draw_arrow(draw, s_out[0], s_out[1], sp_in[0], sp_in[1])
        ds_in = draw_datastore(draw, 700, y - 20, 120, 40, stores[i+3])
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    draw_footer(draw, "Page 3 - User Level 1 DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_1_user.png"))


def level_2_complete():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    cy = H // 2
    # Admin (Top Left)
    ea = draw_entity(draw, 50, cy - 150, 70, 40, "ADMIN")
    la_in, la_out = draw_process(draw, 160, cy - 150, 60, 40, "Login")
    draw_arrow(draw, ea[0], ea[1], la_in[0], la_in[1])
    
    # User (Bottom Left)
    eu = draw_entity(draw, 50, cy + 110, 70, 40, "USER")
    lu_in, lu_out = draw_process(draw, 160, cy + 110, 60, 40, "Login")
    draw_arrow(draw, eu[0], eu[1], lu_in[0], lu_in[1])
    
    # Central System
    sx, sy, sw, sh = 280, cy - 60, 160, 120
    draw_process(draw, sx, sy, sw, sh, "Fraud App\nDetection\nSystem")
    
    # Inputs (Left)
    # Admin Login -> System (Top Left)
    # Target y offset: -30
    tx, ty = get_ellipse_point(sx, sy, sw, sh, -30, 'left')
    draw_arrow(draw, la_out[0], la_out[1], tx, ty)
    
    # User Login -> System (Bottom Left)
    # Target y offset: +30
    tx, ty = get_ellipse_point(sx, sy, sw, sh, 30, 'left')
    draw_arrow(draw, lu_out[0], lu_out[1], tx, ty)
    
    # Fan out to processes (Right side)
    # Admin processes (Top)
    admin_subs = ["User Mgmt", "Data Mgmt", "Reports"]
    for i, sub in enumerate(admin_subs):
        y = cy - 200 + i * 70
        sp_in, sp_out = draw_process(draw, 550, y - 25, 100, 50, sub)
        
        # Output from System (Right side)
        # Distribute offsets: -40, -20, 0? Or just fan out from distributed points
        # Let's map i to y_offset. 
        # Admin side is top half. Let's say offsets -50, -30, -10
        y_off = -50 + i * 20
        ox, oy = get_ellipse_point(sx, sy, sw, sh, y_off, 'right')
        
        draw_arrow(draw, ox, oy, sp_in[0], sp_in[1])
        
        ds_in = draw_datastore(draw, 750, y - 20, 120, 40, "Admin DB")
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    # User processes (Bottom)
    user_subs = ["Apps/Reviews", "Analysis", "History", "Watchlist"]
    for i, sub in enumerate(user_subs):
        y = cy + 50 + i * 70
        sp_in, sp_out = draw_process(draw, 550, y - 25, 100, 50, sub)
        
        # Output from System (Right side)
        # Offsets: 10, 30, 50, 70
        y_off = 10 + i * 15
        ox, oy = get_ellipse_point(sx, sy, sw, sh, y_off, 'right')
        
        draw_arrow(draw, ox, oy, sp_in[0], sp_in[1])
        
        ds_in = draw_datastore(draw, 750, y - 20, 120, 40, "User DB")
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    draw_footer(draw, "Page 4 - Complete System Level 2 DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_2.png"))


def level_1_1_admin_user_mgmt():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    cy = H // 2
    
    # Admin -> User Mgmt
    er = draw_entity(draw, 50, cy - 25, 80, 50, "ADMIN")
    um_in, um_out = draw_process(draw, 200, cy - 30, 140, 60, "User\nManagement")
    draw_arrow(draw, er[0], er[1], um_in[0], um_in[1])
    
    # Branches
    subs = ["View Registered\nUsers", "View User\nProfiles", "Manage User\nStatus"]
    for i, sub in enumerate(subs):
        y = cy - 120 + i * 120
        sp_in, sp_out = draw_process(draw, 450, y - 30, 140, 60, sub)
        draw_arrow(draw, um_out[0], um_out[1], sp_in[0], sp_in[1])
        
        ds_in = draw_datastore(draw, 700, y - 20, 120, 40, "users")
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    draw_footer(draw, "Page 5 - Admin User Management DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_1_1_admin_user_management.png"))


def level_1_1_user_app_reviews():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    cy = H // 2
    
    er = draw_entity(draw, 50, cy - 25, 70, 50, "USER")
    um_in, um_out = draw_process(draw, 180, cy - 30, 140, 60, "App & Review\nManagement")
    draw_arrow(draw, er[0], er[1], um_in[0], um_in[1])
    
    subs = ["Add/Register\nApp", "View App\nDetail", "Add/Import\nReviews", "Run Analysis\n(LLM)"]
    stores = ["apps", "apps", "reviews", "analysis_runs"]
    
    for i, sub in enumerate(subs):
        y = cy - 180 + i * 120
        sp_in, sp_out = draw_process(draw, 450, y - 30, 140, 60, sub)
        draw_arrow(draw, um_out[0], um_out[1], sp_in[0], sp_in[1])
        
        ds_in = draw_datastore(draw, 700, y - 20, 120, 40, stores[i])
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    draw_footer(draw, "Page 6 - User App & Review Management DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_1_1_user_app_reviews.png"))


def level_1_2_admin_data_mgmt():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    cy = H // 2
    
    er = draw_entity(draw, 50, cy - 25, 80, 50, "ADMIN")
    dm_in, dm_out = draw_process(draw, 200, cy - 30, 140, 60, "Data\nManagement")
    draw_arrow(draw, er[0], er[1], dm_in[0], dm_in[1])
    
    subs = ["Manage Apps", "Manage Reviews", "Manage Analysis", "View Reports"]
    stores = ["apps", "reviews", "analysis_runs", "reports"]
    
    for i, sub in enumerate(subs):
        y = cy - 180 + i * 120
        sp_in, sp_out = draw_process(draw, 450, y - 30, 140, 60, sub)
        draw_arrow(draw, dm_out[0], dm_out[1], sp_in[0], sp_in[1])
        
        ds_in = draw_datastore(draw, 700, y - 20, 120, 40, stores[i])
        draw_arrow(draw, sp_out[0], sp_out[1], ds_in[0], ds_in[1])

    draw_footer(draw, "Page 7 - Admin Data Management DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_1_2_admin_data_management.png"))


def level_1_2_user_analysis():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    cy = H // 2
    
    er = draw_entity(draw, 50, cy - 25, 70, 50, "USER")
    am_in, am_out = draw_process(draw, 180, cy - 30, 140, 60, "Analysis\nProcess")
    draw_arrow(draw, er[0], er[1], am_in[0], am_in[1])
    
    subs = ["Submit App\n& Reviews", "Run LLM\nAnalysis", "Parse &\nScore", "Store\nRun", "Return\nResults"]
    
    # Sequential flow for analysis
    prev_out = am_out
    for i, sub in enumerate(subs):
        x = 400 + i * 110
        # Stagger y slightly for visual interest or keep straight? Straight is cleaner.
        y = cy
        sp_in, sp_out = draw_process(draw, x, y - 30, 90, 60, sub, 9)
        draw_arrow(draw, prev_out[0], prev_out[1], sp_in[0], sp_in[1])
        prev_out = sp_out
        
        # Connect to DB if needed
        if i == 0: # Submit
             ds_in = draw_datastore(draw, x, y - 100, 90, 40, "apps/reviews")
             draw_arrow(draw, sp_in[0] + 45, sp_in[1] - 30, ds_in[0] + 45, ds_in[1] + 20)
        if i == 3: # Store
             ds_in = draw_datastore(draw, x, y + 80, 90, 40, "analysis_runs")
             draw_arrow(draw, sp_in[0] + 45, sp_in[1] + 30, ds_in[0] + 45, ds_in[1] - 20)

    draw_footer(draw, "Page 8 - User Analysis Process DFD")
    img.save(os.path.join(OUT_DIR, "dfd_level_1_2_user_analysis.png"))


def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    
    level_0_context()
    level_1_admin()
    level_1_user()
    level_2_complete()
    level_1_1_admin_user_mgmt()
    level_1_1_user_app_reviews()
    level_1_2_admin_data_mgmt()
    level_1_2_user_analysis()
    
    print(f"Generated 8 DFD images in {OUT_DIR}")


if __name__ == "__main__":
    main()
