import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Design Palette (Executive White Theme)
COLOR_BG = RGBColor(248, 250, 252)        # #f8fafc
COLOR_CARD_BG = RGBColor(255, 255, 255)   # #ffffff
COLOR_CARD_ALT = RGBColor(241, 245, 249)  # #f1f5f9
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)    # #0f172a
COLOR_TEXT_MUTED = RGBColor(71, 85, 105)  # #475569
COLOR_TEXT_LIGHT = RGBColor(148, 163, 184)# #94a3b8
COLOR_AMBER = RGBColor(217, 119, 6)       # #d97706
COLOR_AMBER_LIGHT = RGBColor(254, 243, 199) # #fef3c7
COLOR_ORANGE = RGBColor(234, 88, 12)      # #ea580c
COLOR_EMERALD = RGBColor(5, 150, 105)     # #059669
COLOR_BLUE = RGBColor(37, 99, 235)        # #2563eb
COLOR_BLUE_LIGHT = RGBColor(239, 246, 255)# #eff6ff
COLOR_RED = RGBColor(220, 38, 38)         # #dc2626
COLOR_RED_LIGHT = RGBColor(254, 242, 242) # #fef2f2
COLOR_BORDER = RGBColor(226, 232, 240)    # #e2e8f0

FONT_MAIN = "Calibri"
FONT_HEADING = "Segoe UI"

def add_header(slide, slide_num, total_slides=8):
    # Top background bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.8))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_CARD_BG
    top_bar.line.color.rgb = COLOR_BORDER
    top_bar.line.width = Pt(1)

    # Brand Title
    txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.15), Inches(4.5), Inches(0.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🏭 PlantMind Edge  "
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN

    run_badge = p.add_run()
    run_badge.text = "[ Qdrant Hackathon ]"
    run_badge.font.name = FONT_MAIN
    run_badge.font.size = Pt(11)
    run_badge.font.bold = True
    run_badge.font.color.rgb = COLOR_AMBER

    # Center Badge
    txCenter = slide.shapes.add_textbox(Inches(5.0), Inches(0.18), Inches(4.0), Inches(0.45))
    tfCenter = txCenter.text_frame
    pCenter = tfCenter.paragraphs[0]
    pCenter.text = "Executive Product Showcase"
    pCenter.alignment = PP_ALIGN.CENTER
    pCenter.font.name = FONT_MAIN
    pCenter.font.size = Pt(11)
    pCenter.font.color.rgb = COLOR_TEXT_MUTED

    # Right Counter & Voice
    txRight = slide.shapes.add_textbox(Inches(9.2), Inches(0.18), Inches(3.5), Inches(0.45))
    tfRight = txRight.text_frame
    pRight = tfRight.paragraphs[0]
    pRight.text = f"🎙️ Indian English | Slide {slide_num:02d} / {total_slides:02d}"
    pRight.alignment = PP_ALIGN.RIGHT
    pRight.font.name = FONT_MAIN
    pRight.font.size = Pt(11)
    pRight.font.bold = True
    pRight.font.color.rgb = COLOR_TEXT_MUTED

def add_slide_titles(slide, tag, title, subtitle):
    # Tag
    txTag = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.5), Inches(0.35))
    tfTag = txTag.text_frame
    pTag = tfTag.paragraphs[0]
    pTag.text = tag.upper()
    pTag.font.name = FONT_HEADING
    pTag.font.size = Pt(10)
    pTag.font.bold = True
    pTag.font.color.rgb = COLOR_AMBER

    # Title
    txTitle = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(11.5), Inches(0.65))
    tfTitle = txTitle.text_frame
    pTitle = tfTitle.paragraphs[0]
    pTitle.text = title
    pTitle.font.name = FONT_HEADING
    pTitle.font.size = Pt(26)
    pTitle.font.bold = True
    pTitle.font.color.rgb = COLOR_TEXT_MAIN

    # Subtitle
    txSub = slide.shapes.add_textbox(Inches(0.8), Inches(1.85), Inches(11.5), Inches(0.45))
    tfSub = txSub.text_frame
    pSub = tfSub.paragraphs[0]
    pSub.text = subtitle
    pSub.font.name = FONT_MAIN
    pSub.font.size = Pt(13)
    pSub.font.color.rgb = COLOR_TEXT_MUTED

def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def build_presentation():
    print("Building Executive 16:9 PPTX Presentation for PlantMind Edge...")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title & Hero Keynote
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_header(s1, 1)
    add_slide_titles(s1, "Product Keynote", "PlantMind Edge", "Offline-First Industrial Knowledge Continuity Powered by Qdrant Edge")
    
    # 3 Feature Cards
    card_data = [
        ("CORE ADVANTAGE 01", "Sub-150ms Vector Search", 
         "Runs an embedded Qdrant EdgeShard with FastEmbed 384d ONNX on shop-floor tablets. Zero cloud dependency.",
         "FastEmbed BAAI/bge-small-en-v1.5", COLOR_AMBER),
        ("CORE ADVANTAGE 02", "Deliberate Data Policy", 
         "Technicians decide what stays local vs. what synchronizes. Unverified observations stay protected on-device.",
         "Data Sovereignty by Design", COLOR_BLUE),
        ("CORE ADVANTAGE 03", "Groq LLaMA Safety Sync", 
         "Rejects 'last-write-wins' on safety-critical procedures. Groq LLaMA-3.3-70B synthesizes risk diffs for humans.",
         "Zero Fatal Overwrites", COLOR_EMERALD),
    ]

    for i, (tag, title, desc, badge, color) in enumerate(card_data):
        left = Inches(0.8 + i * 3.95)
        top = Inches(2.45)
        width = Inches(3.8)
        height = Inches(4.3)

        box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.5)

        # Top accent strip
        strip = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.1))
        strip.fill.solid()
        strip.fill.fore_color.rgb = color
        strip.line.fill.background()

        # Text inside card
        tb = s1.shapes.add_textbox(left + Inches(0.25), top + Inches(0.25), width - Inches(0.5), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = tag
        p0.font.name = FONT_HEADING
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = color

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MAIN
        p1.space_before = Pt(8)
        p1.space_after = Pt(12)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_after = Pt(24)

        p3 = tf.add_paragraph()
        p3.text = f"• {badge}"
        p3.font.name = FONT_MAIN
        p3.font.size = Pt(11)
        p3.font.bold = True
        p3.font.color.rgb = COLOR_TEXT_MAIN

    set_speaker_notes(s1, "Welcome to PlantMind Edge. An offline-first industrial knowledge continuity platform powered by Qdrant Edge. On modern manufacturing plant floors, connectivity is never guaranteed. PlantMind Edge brings real-time vector intelligence directly onto rugged edge tablets, ensuring mission-critical maintenance knowledge is always accessible.")

    # =========================================================================
    # SLIDE 2: The Problem Statement
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, 2)
    add_slide_titles(s2, "The Problem Statement", "The $22,000 / Minute Downtime Crisis", "When production halts in a concrete Faraday cage, cloud AI is completely dead.")

    problem_cards = [
        ("STAMPING LINE COST", "$22,000", "Per minute of unplanned factory line halt ($1.32M / hour).",
         "High Stakes: Automotive OEM penalties exceed $50K per delayed shipment batch.", COLOR_RED),
        ("DEMOGRAPHIC CLIFF", "10,000", "Senior technicians retiring every single day in North America.",
         "Tribal Loss: Master tech Dave Miller retires next month with 28 years of unwritten fixes.", COLOR_AMBER),
        ("FLOOR CONNECTIVITY", "0% Wi-Fi", "Reinforced concrete & EMI shields create permanent dead zones.",
         "Cloud Failure: Cloud AI cannot open the login page in plant dead zones.", COLOR_BLUE),
    ]

    for i, (label, val, sub, note, color) in enumerate(problem_cards):
        left = Inches(0.8 + i * 3.95)
        top = Inches(2.45)
        width = Inches(3.8)
        height = Inches(4.3)

        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.5)

        strip = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.1))
        strip.fill.solid()
        strip.fill.fore_color.rgb = color
        strip.line.fill.background()

        tb = s2.shapes.add_textbox(left + Inches(0.25), top + Inches(0.25), width - Inches(0.5), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = label
        p0.font.name = FONT_HEADING
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_TEXT_MUTED

        p1 = tf.add_paragraph()
        p1.text = val
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(36)
        p1.font.bold = True
        p1.font.color.rgb = color
        p1.space_before = Pt(6)
        p1.space_after = Pt(10)

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_TEXT_MAIN
        p2.space_after = Pt(20)

        p3 = tf.add_paragraph()
        p3.text = note
        p3.font.name = FONT_MAIN
        p3.font.size = Pt(11)
        p3.font.color.rgb = COLOR_TEXT_MUTED

    set_speaker_notes(s2, "Every minute of downtime on an automotive stamping line costs twenty-two thousand dollars. That is over one point three million dollars an hour. Technicians face two brutal walls: factory floors are wireless dead zones where cloud AI fails, and senior technicians with decades of tribal knowledge are retiring every single day, taking critical plant memory with them.")

    # =========================================================================
    # SLIDE 3: System Architecture
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, 3)
    add_slide_titles(s3, "System Architecture", "Embedded Edge Intelligence: Qdrant on the Floor", "Local CPU vectorization paired with intelligent, conflict-aware central synchronization.")

    # Left: Rugged Edge Tablet
    box_edge = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.45), Inches(5.3), Inches(4.3))
    box_edge.fill.solid()
    box_edge.fill.fore_color.rgb = COLOR_CARD_BG
    box_edge.line.color.rgb = COLOR_AMBER
    box_edge.line.width = Pt(2)

    tb_e = s3.shapes.add_textbox(Inches(1.1), Inches(2.7), Inches(4.7), Inches(3.8))
    tf_e = tb_e.text_frame
    tf_e.word_wrap = True
    p_e0 = tf_e.paragraphs[0]
    p_e0.text = "📱 Rugged Edge Tablet (Shop Floor)"
    p_e0.font.name = FONT_HEADING
    p_e0.font.size = Pt(16)
    p_e0.font.bold = True
    p_e0.font.color.rgb = COLOR_TEXT_MAIN
    p_e0.space_after = Pt(14)

    items_edge = [
        ("FastEmbed BAAI/bge-small-en-v1.5", "384-dimensional dense ONNX embeddings executed locally on CPU with zero cloud roundtrips."),
        ("Embedded Qdrant EdgeShard", "High-performance HNSW cosine vector index delivering sub-150ms semantic search on constrained memory."),
        ("Append-Only SQLite Log", "Tamper-proof monotonic sequence counter (#1042) ensuring immediate local searchability and data sovereignty.")
    ]
    for h, b in items_edge:
        ph = tf_e.add_paragraph()
        ph.text = f"• {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = COLOR_AMBER
        pb = tf_e.add_paragraph()
        pb.text = f"  {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(8)

    # Center Bridge Box
    box_mid = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.3), Inches(3.6), Inches(1.3), Inches(2.0))
    box_mid.fill.solid()
    box_mid.fill.fore_color.rgb = COLOR_AMBER_LIGHT
    box_mid.line.color.rgb = COLOR_AMBER
    tb_m = s3.shapes.add_textbox(Inches(6.3), Inches(3.8), Inches(1.3), Inches(1.6))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    pm = tf_m.paragraphs[0]
    pm.text = "Intermittent\nLAN Sync\n⇄\nSnapshot\nTransfer"
    pm.alignment = PP_ALIGN.CENTER
    pm.font.name = FONT_MAIN
    pm.font.size = Pt(11)
    pm.font.bold = True
    pm.font.color.rgb = COLOR_AMBER

    # Right: Central Engineering Cloud
    box_cloud = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.8), Inches(2.45), Inches(4.7), Inches(4.3))
    box_cloud.fill.solid()
    box_cloud.fill.fore_color.rgb = COLOR_CARD_BG
    box_cloud.line.color.rgb = COLOR_BLUE
    box_cloud.line.width = Pt(2)

    tb_c = s3.shapes.add_textbox(Inches(8.1), Inches(2.7), Inches(4.1), Inches(3.8))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p_c0 = tf_c.paragraphs[0]
    p_c0.text = "☁️ Central Engineering Cloud"
    p_c0.font.name = FONT_HEADING
    p_c0.font.size = Pt(16)
    p_c0.font.bold = True
    p_c0.font.color.rgb = COLOR_TEXT_MAIN
    p_c0.space_after = Pt(14)

    items_cloud = [
        ("Central Qdrant Vector Server", "Global golden master database managing corporate procedures, manuals, and synchronized plant fleet records."),
        ("Groq LLaMA-3.3-70B Reconciler", "Automated AI conflict analysis; generates plain-language diffs and blocks fatal last-write-wins overwrites."),
        ("Plant Fleet Inventory Hub", "Multi-tablet management tracking hardware health, memory pressure, and delta sync versions across plants.")
    ]
    for h, b in items_cloud:
        ph = tf_c.add_paragraph()
        ph.text = f"• {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = COLOR_BLUE
        pb = tf_c.add_paragraph()
        pb.text = f"  {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(8)

    set_speaker_notes(s3, "PlantMind Edge solves this with a purpose-built edge architecture. We run an embedded Qdrant EdgeShard and a local FastEmbed ONNX model directly on the shop floor tablet. Queries are vectorized and matched against local HNSW vector indexes in under one hundred and fifty milliseconds on CPU, with zero reliance on cloud connectivity.")

    # =========================================================================
    # SLIDE 4: Live Demo - Offline Semantic Search
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, 4)
    add_slide_titles(s4, "Live Demonstration 01", "Sub-150ms Offline Semantic Search", "Tested in isolated Airplane Mode: Instant retrieval of Dave Miller's tribal workaround.")

    # Image Left
    img4_path = os.path.abspath("presentation/screenshots/01_offline_search.png")
    if os.path.exists(img4_path):
        s4.shapes.add_picture(img4_path, Inches(0.8), Inches(2.45), width=Inches(7.2))

    # Right Card
    box4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(2.45), Inches(4.2), Inches(4.3))
    box4.fill.solid()
    box4.fill.fore_color.rgb = COLOR_CARD_BG
    box4.line.color.rgb = COLOR_BORDER
    box4.line.width = Pt(1.5)

    tb4 = s4.shapes.add_textbox(Inches(8.55), Inches(2.7), Inches(3.7), Inches(3.8))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    p4_0 = tf4.paragraphs[0]
    p4_0.text = "Key Verification Proofs"
    p4_0.font.name = FONT_HEADING
    p4_0.font.size = Pt(18)
    p4_0.font.bold = True
    p4_0.font.color.rgb = COLOR_TEXT_MAIN
    p4_0.space_after = Pt(14)

    proofs4 = [
        ("Strict Airplane Mode Active", "Tablet operates in 100% network isolation with zero cloud or cellular dependencies.", COLOR_RED),
        ("133ms Retrieval Latency", "Vector search executes comfortably under the strict 150ms edge latency budget.", COLOR_AMBER),
        ("0.94 Semantic Match", "Top rank delivers Dave Miller's Viton bypass seal workaround in Bin 14, saving 3.8 hours of downtime.", COLOR_EMERALD)
    ]
    for h, b, c in proofs4:
        ph = tf4.add_paragraph()
        ph.text = f"✓ {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = c
        pb = tf4.add_paragraph()
        pb.text = f"   {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(10)

    set_speaker_notes(s4, "Here is our live offline search in action. Notice the airplane mode indicator: the tablet is completely isolated from the internet. When the technician searches for 'hydraulic pressure dropping on Line 3 press', our local engine returns Dave Miller's tribal workaround in just one hundred and thirty-three milliseconds, cutting repair time from four hours down to twelve minutes.")

    # =========================================================================
    # SLIDE 5: Live Demo - Append-Only Write & Policy
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, 5)
    add_slide_titles(s5, "Live Demonstration 02", "On-Floor Capture & Deliberate Data Policy", "Capturing observations instantly while giving technicians control over what syncs.")

    img5_path = os.path.abspath("presentation/screenshots/02_append_only_write.png")
    if os.path.exists(img5_path):
        s5.shapes.add_picture(img5_path, Inches(0.8), Inches(2.45), width=Inches(7.2))

    box5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(2.45), Inches(4.2), Inches(4.3))
    box5.fill.solid()
    box5.fill.fore_color.rgb = COLOR_CARD_BG
    box5.line.color.rgb = COLOR_BORDER
    box5.line.width = Pt(1.5)

    tb5 = s5.shapes.add_textbox(Inches(8.55), Inches(2.7), Inches(3.7), Inches(3.8))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    p5_0 = tf5.paragraphs[0]
    p5_0.text = "Sovereignty by Design"
    p5_0.font.name = FONT_HEADING
    p5_0.font.size = Pt(18)
    p5_0.font.bold = True
    p5_0.font.color.rgb = COLOR_TEXT_MAIN
    p5_0.space_after = Pt(14)

    proofs5 = [
        ("Immutable Local Sequence Log", "Every observation receives a sequence counter (#1042) ensuring an untampered audit trail.", COLOR_AMBER),
        ("'Keep Local Until Reviewed' Flag", "Unverified or experimental notes remain strictly on-device until peer review is complete.", COLOR_BLUE),
        ("Immediate Vector Indexing", "New observations are embedded on-device and searchable locally in 0 seconds with zero lag.", COLOR_EMERALD)
    ]
    for h, b, c in proofs5:
        ph = tf5.add_paragraph()
        ph.text = f"✓ {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = c
        pb = tf5.add_paragraph()
        pb.text = f"   {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(10)

    set_speaker_notes(s5, "Technicians can log immediate observations directly on the floor. PlantMind Edge provides deliberate data sovereignty. A technician can flag an unverified observation to 'keep local until reviewed', preventing unvalidated notes from polluting the central repository until peer review is complete.")

    # =========================================================================
    # SLIDE 6: Live Demo - Device Memory Inspector
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, 6)
    add_slide_titles(s6, "Device Engineering", "Constrained Device Memory Inspector", "Operating safely inside strict 1GB RAM ceilings with automated TTL retention policies.")

    img6_path = os.path.abspath("presentation/screenshots/03_device_memory_inspector.png")
    if os.path.exists(img6_path):
        s6.shapes.add_picture(img6_path, Inches(0.8), Inches(2.45), width=Inches(7.2))

    box6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(2.45), Inches(4.2), Inches(4.3))
    box6.fill.solid()
    box6.fill.fore_color.rgb = COLOR_CARD_BG
    box6.line.color.rgb = COLOR_BORDER
    box6.line.width = Pt(1.5)

    tb6 = s6.shapes.add_textbox(Inches(8.55), Inches(2.7), Inches(3.7), Inches(3.8))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    p6_0 = tf6.paragraphs[0]
    p6_0.text = "Embedded Footprint Metrics"
    p6_0.font.name = FONT_HEADING
    p6_0.font.size = Pt(18)
    p6_0.font.bold = True
    p6_0.font.color.rgb = COLOR_TEXT_MAIN
    p6_0.space_after = Pt(14)

    proofs6 = [
        ("184 MB / 1024 MB RAM (18% Usage)", "Lightweight footprint leaves ample headroom for diagnostics and host operating systems.", COLOR_EMERALD),
        ("14.2 MB Disk Storage", "Quantized vectors and compact payload storage protect flash memory from write fatigue.", COLOR_BLUE),
        ("Automated TTL Retention Engine", "Points older than 90 days are automatically summarized or evicted, eliminating OOM crashes forever.", COLOR_AMBER)
    ]
    for h, b, c in proofs6:
        ph = tf6.add_paragraph()
        ph.text = f"✓ {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = c
        pb = tf6.add_paragraph()
        pb.text = f"   {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(10)

    set_speaker_notes(s6, "Industrial edge tablets have strict hardware limits. PlantMind Edge includes an on-device Memory Inspector that continuously monitors RAM, vector cache, and disk usage. Our local EdgeShard consumes under two hundred megabytes of RAM with automated TTL retention policies, guaranteeing peak performance on low-power devices.")

    # =========================================================================
    # SLIDE 7: Safety Secret - Groq LLaMA Conflict Reconciliation
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, 7)
    add_slide_titles(s7, "Safety Critical Architecture", "Groq LLaMA: No Last-Write-Wins on Safety", "Guarding human lives against silent database overwrites with AI risk reasoning.")

    img7_path = os.path.abspath("presentation/screenshots/04_conflict_reconciliation.png")
    if os.path.exists(img7_path):
        s7.shapes.add_picture(img7_path, Inches(0.8), Inches(2.45), width=Inches(7.2))

    box7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(2.45), Inches(4.2), Inches(4.3))
    box7.fill.solid()
    box7.fill.fore_color.rgb = COLOR_CARD_BG
    box7.line.color.rgb = COLOR_RED
    box7.line.width = Pt(2)

    tb7 = s7.shapes.add_textbox(Inches(8.55), Inches(2.7), Inches(3.7), Inches(3.8))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    p7_0 = tf7.paragraphs[0]
    p7_0.text = "⚠️ SAFETY PRINCIPLE"
    p7_0.font.name = FONT_HEADING
    p7_0.font.size = Pt(13)
    p7_0.font.bold = True
    p7_0.font.color.rgb = COLOR_RED

    p7_sub = tf7.add_paragraph()
    p7_sub.text = '"Last-write-wins kills people on a factory floor."'
    p7_sub.font.name = FONT_HEADING
    p7_sub.font.size = Pt(14)
    p7_sub.font.bold = True
    p7_sub.font.color.rgb = COLOR_TEXT_MAIN
    p7_sub.space_after = Pt(12)

    proofs7 = [
        ("Omission Detected by LLaMA-3.3", "Version B omitted the mandatory 10-minute cool-down cycle to rush tool changes.", COLOR_RED),
        ("Severe Hazard Warning", "Identified risk of 500-bar hydraulic injection and flash fire hazard under hot manifold conditions.", COLOR_AMBER),
        ("One-Click Human Reconciliation", "Knowledge manager accepts Version A; standard instantly broadcasts across all plant edge tablets.", COLOR_EMERALD)
    ]
    for h, b, c in proofs7:
        ph = tf7.add_paragraph()
        ph.text = f"• {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = c
        pb = tf7.add_paragraph()
        pb.text = f"  {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(8)

    set_speaker_notes(s7, "When tablets reconnect, conflicting offline updates are intelligently reconciled. Most edge databases rely on last-write-wins. On a manufacturing line, last-write-wins can cause fatal accidents. PlantMind Edge blocks safety-critical overwrites and invokes Groq LLaMA-3.3-70B to generate plain-language risk breakdowns and enforce master safety standards.")

    # =========================================================================
    # SLIDE 8: Enterprise Scale & Vision
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, 8)
    add_slide_titles(s8, "Business Value & Vision", "Enterprise Scale & Transformational ROI", "Capturing human expertise before it walks out the door.")

    img8_path = os.path.abspath("presentation/screenshots/05_central_knowledge_explorer.png")
    if os.path.exists(img8_path):
        s8.shapes.add_picture(img8_path, Inches(0.8), Inches(2.45), width=Inches(7.2))

    box8 = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(2.45), Inches(4.2), Inches(4.3))
    box8.fill.solid()
    box8.fill.fore_color.rgb = COLOR_CARD_BG
    box8.line.color.rgb = COLOR_EMERALD
    box8.line.width = Pt(2)

    tb8 = s8.shapes.add_textbox(Inches(8.55), Inches(2.7), Inches(3.7), Inches(3.8))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    p8_0 = tf8.paragraphs[0]
    p8_0.text = "Measurable Enterprise ROI"
    p8_0.font.name = FONT_HEADING
    p8_0.font.size = Pt(18)
    p8_0.font.bold = True
    p8_0.font.color.rgb = COLOR_TEXT_MAIN

    p8_val = tf8.add_paragraph()
    p8_val.text = "18x ROI"
    p8_val.font.name = FONT_HEADING
    p8_val.font.size = Pt(38)
    p8_val.font.bold = True
    p8_val.font.color.rgb = COLOR_EMERALD
    p8_val.space_after = Pt(4)

    p8_sub = tf8.add_paragraph()
    p8_sub.text = "A single avoided 2-hour downtime incident saves $2.6M — paying for PlantMind Edge across an entire factory facility for years."
    p8_sub.font.name = FONT_MAIN
    p8_sub.font.size = Pt(11)
    p8_sub.font.color.rgb = COLOR_TEXT_MUTED
    p8_sub.space_after = Pt(12)

    proofs8 = [
        ("$14.2B Addressable Market", "Connected worker and industrial edge intelligence sector growing at 24% CAGR.", COLOR_BLUE),
        ("Fleet Knowledge Master", "Synchronizes maintenance best practices across multiple factories worldwide with Qdrant.", COLOR_AMBER)
    ]
    for h, b, c in proofs8:
        ph = tf8.add_paragraph()
        ph.text = f"✓ {h}"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = c
        pb = tf8.add_paragraph()
        pb.text = f"   {b}"
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11)
        pb.font.color.rgb = COLOR_TEXT_MUTED
        pb.space_after = Pt(8)

    set_speaker_notes(s8, "From individual floor tablets to enterprise fleet management, PlantMind Edge scales seamlessly across multi-plant operations. Preventing just one two-hour downtime incident saves two point six million dollars, paying for PlantMind Edge across an entire enterprise. Capturing human expertise before it walks out the door. This is PlantMind Edge.")

    # =========================================================================
    # Save Presentation to multiple accessible locations
    # =========================================================================
    targets = [
        "presentation/PlantMind_Edge_Executive_Deck.pptx",
        "brag-output/PlantMind_Edge_Executive_Deck.pptx",
        "PlantMind_Edge_Executive_Deck.pptx",
        "public/PlantMind_Edge_Executive_Deck.pptx",
        "frontend/public/PlantMind_Edge_Executive_Deck.pptx"
    ]
    for t in targets:
        os.makedirs(os.path.dirname(t) if os.path.dirname(t) else ".", exist_ok=True)
        prs.save(t)
        print(f"Saved PPTX to: {t} ({os.path.getsize(t)} bytes)")

    print("PPTX Generation Complete!")

if __name__ == "__main__":
    build_presentation()
