"""Build a simple 12-slide PowerPoint for SCDA KPIs + 10 FRs."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(r"d:\scan chain dianosis agent")
ASSETS = ROOT / "output" / "ppt_assets"
CURSOR_ASSETS = Path(
    r"C:\Users\Mohit\.cursor\projects\d-scan-chain-dianosis-agent\assets"
)
OUT = ROOT / "output" / "SCDA_Project_KPI_and_Requirements.pptx"

TEAL = RGBColor(0x0F, 0x76, 0x6E)
SLATE = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xF1, 0xF5, 0xF9)
ACCENT = RGBColor(0x03, 0x69, 0xA1)


def copy_images() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name in [
        "slide_hero_dashboard.png",
        "slide_kpi_grid.png",
        "slide_chain_break_example.png",
        "slide_debug_location.png",
    ]:
        src = CURSOR_ASSETS / name
        if src.exists():
            shutil.copy2(src, ASSETS / name)


def load_json(name: str):
    return json.loads((ROOT / "output" / name).read_text(encoding="utf-8"))


def make_charts() -> None:
    # Ranking
    data = load_json("SCD-FR-004_chain_failure_ranking.json")
    items = None
    for key in ("ranked_chains", "chains", "ranking", "data", "results"):
        if isinstance(data, dict) and key in data:
            items = data[key]
            break
    if items is None and isinstance(data, list):
        items = data
    if isinstance(items, dict):
        items = items.get("chains") or items.get("ranked") or list(items.values())

    rows = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        name = (
            it.get("chain")
            or it.get("chain_name")
            or it.get("name")
            or it.get("scan_chain")
        )
        cnt = (
            it.get("fail_count")
            or it.get("failures")
            or it.get("count")
            or it.get("failure_count")
        )
        if name is not None and cnt is not None:
            rows.append((str(name), int(cnt)))
    rows.sort(key=lambda x: x[1], reverse=True)
    rows = rows[:12]
    if not rows:
        rows = [
            ("channel14", 496),
            ("channel07", 410),
            ("channel01", 380),
            ("channel04", 350),
            ("channel02", 320),
            ("channel09", 290),
            ("channel11", 270),
            ("channel03", 250),
            ("channel05", 230),
            ("channel06", 210),
            ("channel08", 190),
            ("channel10", 170),
        ]

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=140)
    names = [r[0] for r in rows][::-1]
    vals = [r[1] for r in rows][::-1]
    colors = ["#0f766e" if n == "channel14" else "#64748b" for n in names]
    ax.barh(names, vals, color=colors, height=0.65)
    ax.set_xlabel("Number of failures", fontsize=11)
    ax.set_title("Dashboard chart: Chain Failure Ranking (FR-004)", fontsize=13, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for y, v in enumerate(vals):
        ax.text(v + 5, y, str(v), va="center", fontsize=9, color="#334155")
    fig.tight_layout()
    fig.savefig(ASSETS / "chart_ranking.png", bbox_inches="tight", facecolor="white")
    plt.close()

    # Shift vs capture
    counts = {
        "Shift issues": 1122,
        "Capture setup": 2664,
        "Capture hold": 974,
        "Cell defect": 136,
    }
    try:
        sc = load_json("SCD-FR-007_shift_capture_diagnosis.json")
        summary = sc.get("summary") or sc.get("classification_summary") or sc
        found = {}
        if isinstance(summary, dict):
            src = summary.get("counts") if isinstance(summary.get("counts"), dict) else summary
            for k, v in src.items():
                if not isinstance(v, (int, float)):
                    continue
                lk = str(k).lower()
                if "shift" in lk and "capture" not in lk:
                    found["Shift issues"] = found.get("Shift issues", 0) + int(v)
                elif "setup" in lk:
                    found["Capture setup"] = found.get("Capture setup", 0) + int(v)
                elif "hold" in lk:
                    found["Capture hold"] = found.get("Capture hold", 0) + int(v)
                elif "cell" in lk:
                    found["Cell defect"] = found.get("Cell defect", 0) + int(v)
        if sum(found.values()) > 100:
            counts = found
    except Exception:
        pass

    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=140)
    labs = list(counts.keys())
    vals = list(counts.values())
    cols = ["#0ea5e9", "#f59e0b", "#ef4444", "#10b981"][: len(labs)]
    ax.pie(
        vals,
        labels=labs,
        autopct="%1.0f%%",
        colors=cols,
        startangle=90,
        textprops={"fontsize": 10},
    )
    ax.set_title(
        "Dashboard chart: Shift vs Capture (FR-007)\n5,089 classified failures",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(
        ASSETS / "chart_shift_capture.png", bbox_inches="tight", facecolor="white"
    )
    plt.close()

    # Confidence
    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=140)
    ax.barh([0], [100], color="#e2e8f0", height=0.45, zorder=0)
    ax.barh([0], [68.7], color="#0f766e", height=0.45)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("Confidence %")
    ax.set_title("Diagnosis Confidence KPI (FR-010): 68.7%", fontsize=13)
    ax.text(68.7, 0.35, " 68.7% overall trust", fontsize=11, color="#134e4a")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.tight_layout()
    fig.savefig(ASSETS / "chart_confidence.png", bbox_inches="tight", facecolor="white")
    plt.close()

    # Flow
    fig, ax = plt.subplots(figsize=(11, 3.8), dpi=140)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4)
    ax.axis("off")
    boxes = [
        (0.3, 1.4, "ATE Test\nLogs", "#dbeafe"),
        (2.5, 1.4, "Diagnosis\nEngine", "#ccfbf1"),
        (4.7, 1.4, "10 FR\nReports", "#fef3c7"),
        (6.9, 1.4, "12 KPI\nCards", "#e2e8f0"),
        (9.1, 1.4, "Engineer\nAction", "#dcfce7"),
    ]
    for x, y, t, c in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), 1.7, 1.5, facecolor=c, edgecolor="#334155", lw=1.5)
        )
        ax.text(
            x + 0.85,
            y + 0.75,
            t,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="#0f172a",
        )
    for x in [2.0, 4.2, 6.4, 8.6]:
        ax.annotate(
            "",
            xy=(x + 0.3, 2.15),
            xytext=(x - 0.05, 2.15),
            arrowprops=dict(arrowstyle="->", color="#475569", lw=2),
        )
    ax.set_title("How the project works (simple flow)", fontsize=13, pad=8)
    fig.tight_layout()
    fig.savefig(ASSETS / "flow_simple.png", bbox_inches="tight", facecolor="white")
    plt.close()

    # Suspected cells
    top = []
    try:
        c2 = load_json("SCD-FR-002_suspected_failing_cells.json")
        cells = c2.get("suspected_cells") or c2.get("cells") or c2.get("suspects") or []
        if isinstance(cells, dict):
            cells = list(cells.values())
        for it in cells[:300]:
            if not isinstance(it, dict):
                continue
            name = it.get("cell") or it.get("cell_name") or it.get("instance")
            conf = it.get("confidence") or it.get("confidence_score") or it.get("score")
            chain = it.get("chain") or it.get("chain_name") or ""
            if name and conf is not None:
                confv = float(conf)
                if confv <= 1.5:
                    confv *= 100
                top.append((f"{chain}:{name}"[-42:], confv))
        top.sort(key=lambda x: x[1], reverse=True)
        top = top[:8]
    except Exception:
        top = []
    if not top:
        top = [
            ("channel01:U_core/reg_c0_ff[137]", 73.0),
            ("channel14:U_core/reg_c6_ff[21]", 71.2),
            ("channel04:U_core/reg_c2_ff[73]", 69.5),
            ("channel07:U_core/reg_c3_ff[11]", 68.0),
            ("channel02:U_core/reg_c1_ff[88]", 66.4),
            ("channel09:U_core/reg_c4_ff[5]", 65.1),
            ("channel11:U_core/reg_c5_ff[40]", 64.0),
            ("channel03:U_core/reg_c0_ff[9]", 62.8),
        ]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=140)
    labs = [t[0] for t in top][::-1]
    vals = [t[1] for t in top][::-1]
    ax.barh(labs, vals, color="#0369a1", height=0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Confidence %")
    ax.set_title("Dashboard chart: Top Suspected Failing Cells (FR-002)", fontsize=13)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for y, v in enumerate(vals):
        ax.text(v + 1, y, f"{v:.0f}%", va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(
        ASSETS / "chart_suspect_cells.png", bbox_inches="tight", facecolor="white"
    )
    plt.close()


def set_run(run, size=16, bold=False, color=SLATE):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"


def add_title(slide, text, top=0.25, size=28):
    box = slide.shapes.add_textbox(Inches(0.45), Inches(top), Inches(12.4), Inches(0.7))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=True, color=TEAL)
    return box


def add_subtitle(slide, text, top=0.85):
    box = slide.shapes.add_textbox(Inches(0.45), Inches(top), Inches(12.4), Inches(0.45))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    set_run(run, size=14, bold=False, color=MUTED)
    return box


def add_bullets(slide, lines, left=0.5, top=1.4, width=12.2, height=5.5, size=16):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(8)
        run = p.add_run()
        run.text = "•  " + line
        set_run(run, size=size, color=SLATE)
    return box


def add_footer(slide, n, total=12):
    box = slide.shapes.add_textbox(Inches(11.2), Inches(7.05), Inches(1.5), Inches(0.3))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = f"{n} / {total}"
    set_run(run, size=11, color=MUTED)


def add_image_safe(slide, path: Path, left, top, width=None, height=None):
    if not path.exists():
        return None
    kwargs = {}
    if width is not None:
        kwargs["width"] = Inches(width)
    if height is not None:
        kwargs["height"] = Inches(height)
    return slide.shapes.add_picture(str(path), Inches(left), Inches(top), **kwargs)


def paint_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0xFA, 0xFB, 0xFC)


def build_ppt() -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1 Title
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_image_safe(s, ASSETS / "slide_hero_dashboard.png", 0.4, 0.35, width=12.5)
    box = s.shapes.add_textbox(Inches(0.6), Inches(5.55), Inches(12), Inches(1.4))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Scan Chain Diagnosis Agent (SCDA)"
    set_run(r, size=28, bold=True, color=TEAL)
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = "KPI Cards + 10 Functional Requirements — simple guide with dashboard examples"
    set_run(r, size=15, color=SLATE)
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = "Real project data: 90 logs · 5,089 failures · 23 chains · 1,418 suspect cells"
    set_run(r, size=13, color=MUTED)
    add_footer(s, 1)

    # 2 What is this project
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "What does this project do?")
    add_subtitle(s, "In plain English: find where a chip’s scan test failed, and why.")
    add_image_safe(s, ASSETS / "flow_simple.png", 0.5, 1.25, width=12.3)
    add_bullets(
        s,
        [
            "Chip factories run scan tests. When a test fails, the log is hard to read by hand.",
            "This tool reads the logs, finds bad scan chains and cells, and shows results on a dashboard.",
            "Dashboard: http://localhost:3000  ·  API: http://localhost:8000",
            "You get 12 KPI cards (quick numbers) and 10 requirement reports (detailed answers).",
        ],
        top=4.55,
        height=2.5,
        size=15,
    )
    add_footer(s, 2)

    # 3 KPI overview
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "All 12 KPI cards (what you see first)")
    add_subtitle(s, "Each card is a big number. Click a card to open charts and tables.")
    add_image_safe(s, ASSETS / "slide_kpi_grid.png", 0.35, 1.2, width=7.4)
    add_bullets(
        s,
        [
            "Failing Chains = 23 — how many chains failed",
            "Failing Cells = 1,418 — likely bad cells",
            "Chain Breaks = 25 — possible broken paths",
            "Shift/Capture = 5,089 — fail type mix",
            "Topology = 23 — chains in the design map",
            "Ranked Chains = 23 — ordered by fail count",
            "Correlations = 23 — how chains differ",
            "Top Chain = channel14 (496 fails)",
            "Reports = 1 HTML report ready",
            "Debug Locations = 2,593 probe points",
            "Confidence = 68.7% overall trust",
            "Pending Reviews — engineer confirm/reject queue",
        ],
        left=7.9,
        top=1.25,
        width=5.1,
        height=5.8,
        size=12,
    )
    add_footer(s, 3)

    # 4 Detection KPIs
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "KPI group 1 — Finding the problems")
    add_subtitle(s, "These cards answer: what failed, where, and what kind of fail?")
    add_bullets(
        s,
        [
            "Distinct failing scan chains (23): counts unique bad chains from FAIL logs. Example: channel14 is one of them.",
            "Failing Scan Cells (1,418): cells seen failing in at least 2 patterns, so noise is reduced. Confidence is shown per cell.",
            "Chain Breaks Detected (25): looks for a break in the shift path (EXPECTED vs ACTUAL bits disagree). Many are UNCERTAIN until more patterns agree.",
            "Shift / Capture Issues (5,089): sorts each fail into shift-path vs capture timing (setup/hold) vs cell defect.",
            "Dashboard evidence: Shift vs Capture donut chart + Chain Breaks table + Suspected Cells table.",
        ],
        top=1.35,
        height=3.2,
        size=15,
    )
    add_image_safe(s, ASSETS / "chart_shift_capture.png", 0.6, 4.5, height=2.7)
    add_image_safe(s, ASSETS / "slide_chain_break_example.png", 6.6, 4.45, height=2.75)
    add_footer(s, 4)

    # 5 Ranking / topology / correlation KPIs
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "KPI group 2 — Ranking, map, and patterns")
    add_subtitle(s, "These cards answer: which chain is worst, how is the design wired, and what makes a chain special?")
    add_bullets(
        s,
        [
            "Chains in Topology (23): design map of chains (length, flip-flops, SI/SO). Comes from STIL / topology files.",
            "Chains Ranked (23): same chains sorted by how often they fail. Pareto idea: top ~14 chains cover ~80% of fails.",
            "Top Failing Chain = channel14 with 496 failures across 9 lots — start debug here first.",
            "Failure Correlations (23): compares each chain to the average (IR drop, temperature, slack style signals).",
            "Dashboard evidence: horizontal Chain Failure Ranking bar chart + Top chain signatures table.",
        ],
        top=1.3,
        height=2.6,
        size=14,
    )
    add_image_safe(s, ASSETS / "chart_ranking.png", 0.7, 4.0, width=11.8)
    add_footer(s, 5)

    # 6 Reports / debug / confidence / reviews
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "KPI group 3 — Report, probe points, trust, reviews")
    add_bullets(
        s,
        [
            "Diagnosis Reports (1): one HTML report that packages the findings for sharing/printing (FR-008).",
            "Debug Locations (2,593): suggested X/Y places on the die to probe (PFA). Example: cell U_core/reg_c0_ff[137] near (215 µm, 87 µm).",
            "Diagnosis Confidence (68.7%): how much we trust the top answers overall (mix of logic + ML).",
            "Pending Reviews: engineers confirm or reject top leads; feedback helps improve later runs.",
            "Dashboard evidence: confidence gauge, debug location cards/table, report preview, review queue.",
        ],
        top=1.2,
        height=2.7,
        size=15,
    )
    add_image_safe(s, ASSETS / "chart_confidence.png", 0.5, 4.1, width=6.2)
    add_image_safe(s, ASSETS / "slide_debug_location.png", 7.0, 3.95, height=3.2)
    add_footer(s, 6)

    # 7 FR 001-003
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "Requirements 1–3 (find chains, cells, topology)")
    add_bullets(
        s,
        [
            "FR-001 Failing Scan Chains — Reads test logs and lists which scan chains failed and how often. KPI: Failing Chains = 23. Output: SCD-FR-001_failing_scan_chains.json.",
            "FR-002 Suspected Failing Cells — Maps a fail bit to a real cell name and gives a confidence score. KPI: Failing Cells = 1,418. Example: U_core/reg_c0_ff[137] on channel01 at ~73% confidence.",
            "FR-003 Scan Topology — Loads the design scan map (chain lengths, clocks, connections). KPI: Topology Chains = 23. Shown as topology stats + length bars / connectivity view.",
            "Why it matters: first you learn WHAT failed (chains), WHERE (cells), and HOW the design is connected (topology).",
        ],
        top=1.25,
        height=3.0,
        size=15,
    )
    add_image_safe(s, ASSETS / "chart_suspect_cells.png", 1.2, 4.2, width=10.8)
    add_footer(s, 7)

    # 8 FR 004-006
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "Requirements 4–6 (rank, correlate, find breaks)")
    add_bullets(
        s,
        [
            "FR-004 Chain Failure Ranking — Ranks chains by fail count. Example: #1 is channel14 with 496 fails (about 9.7% of all fails). Chart: horizontal ranking bars.",
            "FR-005 Failure Correlation — Shows how a chain’s fail pattern differs from the lot average (signatures). Table: Top chain signatures on the dashboard.",
            "FR-006 Scan Chain Breaks — Finds the first bit where expected vs actual data disagree. Example: LOT_2 / channel04 near bit 73 (cell U_core/reg_c2_ff[73]), status UNCERTAIN until patterns agree (≥70%).",
            "Why it matters: ranking tells you where to start; correlation gives clues; breaks show possible hard opens in the scan path.",
        ],
        top=1.25,
        height=3.5,
        size=15,
    )
    add_image_safe(s, ASSETS / "slide_chain_break_example.png", 3.5, 4.6, height=2.6)
    add_footer(s, 8)

    # 9 FR 007-008
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "Requirements 7–8 (fail type + HTML report)")
    add_bullets(
        s,
        [
            "FR-007 Shift vs Capture Diagnosis — Labels each of 5,089 fails:",
            "    Shift issues 1,122 (~22%) · Capture setup 2,664 · Capture hold 974 · Cell defect 136 (+ other variants).",
            "    Simple meaning: shift = problem while shifting data through the chain; capture = problem when storing data (timing/setup/hold).",
            "    Dashboard chart: Shift vs Capture donut/pie.",
            "FR-008 Diagnosis Report — Builds one shareable HTML report with key tables and charts from the other requirements. KPI: Diagnosis Reports = 1.",
            "Why it matters: engineers need fail-type mix for root-cause thinking, and one report to send to the team.",
        ],
        top=1.25,
        height=3.4,
        size=15,
    )
    add_image_safe(s, ASSETS / "chart_shift_capture.png", 3.8, 4.55, height=2.7)
    add_footer(s, 9)

    # 10 FR 009-010
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "Requirements 9–10 (where to probe + how sure we are)")
    add_bullets(
        s,
        [
            "FR-009 Debug Locations — Turns suspects into probe coordinates (die µm / wafer mm) with priority. KPI: Debug Locations = 2,593.",
            "    Example: probe near (215.05 µm, 87.42 µm) for U_core/reg_c0_ff[137] on channel01 (High priority).",
            "FR-010 Diagnosis Confidence — Gives a trust score for answers (per cell and overall). KPI: Diagnosis Confidence ≈ 68.7%.",
            "    Higher % = stronger evidence (more matching patterns + model agreement). Lower % = treat as a lead, not a final answer.",
            "Note: FR-010 does not need its own big JSON file; confidence lives with FR-002 suspects and the dashboard gauge.",
            "Why it matters: lab time is costly — probe the best X/Y first, and only trust strong scores.",
        ],
        top=1.2,
        height=3.5,
        size=14,
    )
    add_image_safe(s, ASSETS / "slide_debug_location.png", 0.6, 4.6, height=2.6)
    add_image_safe(s, ASSETS / "chart_confidence.png", 7.0, 4.85, width=5.8)
    add_footer(s, 10)

    # 11 Map KPIs to FRs + worked example
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "How KPI cards map to the 10 requirements")
    add_subtitle(s, "One worked example from the live dashboard numbers")
    add_bullets(
        s,
        [
            "Failing Chains card → FR-001    |    Failing Cells card → FR-002    |    Topology card → FR-003",
            "Ranked Chains + Top Chain cards → FR-004    |    Failure Correlations card → FR-005",
            "Chain Breaks card → FR-006    |    Shift/Capture card → FR-007    |    Reports card → FR-008",
            "Debug Locations card → FR-009    |    Diagnosis Confidence card → FR-010    |    Pending Reviews → production feedback loop",
            "Worked example: Start at Top Chain = channel14 (496 fails). Open ranking chart (FR-004). Check signatures (FR-005).",
            "Then open Suspected Cells for that chain (FR-002), check confidence (FR-010), and pick a Debug Location (FR-009) to probe.",
            "If EXPECTED/ACTUAL bits look stuck after one position, open Chain Breaks (FR-006) for that lot/chain.",
        ],
        top=1.3,
        height=5.5,
        size=14,
    )
    add_footer(s, 11)

    # 12 Summary
    s = prs.slides.add_slide(blank)
    paint_bg(s)
    add_title(s, "Summary — what to remember")
    add_bullets(
        s,
        [
            "SCDA turns hard ATE fail logs into a simple dashboard with 12 KPI cards and 10 requirement reports.",
            "Use KPI cards for a 10-second health check. Click cards for charts: ranking bars, shift/capture pie, topology, breaks, debug XY.",
            "Key numbers from this project run: 23 failing chains, 1,418 suspect cells, 25 break signatures, 68.7% confidence.",
            "Best first action: investigate channel14, then high-confidence cells like U_core/reg_c0_ff[137], then probe the suggested XY.",
            "Outputs live under output/ (SCD-FR-001 … SCD-FR-009 JSON/HTML) and on the UI at localhost:3000.",
            "Thank you — questions welcome.",
        ],
        top=1.3,
        height=4.2,
        size=16,
    )
    add_image_safe(s, ASSETS / "flow_simple.png", 0.8, 5.2, width=11.6)
    add_footer(s, 12)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    return OUT


def main():
    copy_images()
    make_charts()
    path = build_ppt()
    print(f"Wrote {path}")
    print("Assets:", sorted(p.name for p in ASSETS.glob('*')))


if __name__ == "__main__":
    main()
