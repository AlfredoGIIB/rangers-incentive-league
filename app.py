from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import legal, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

st.set_page_config(
    page_title="Rangers Incentive League",
    page_icon=None,
    layout="wide",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"], .stApp, .stMarkdown, .stButton button, .stMetric {
        font-family: Inter, Aptos, "Segoe UI", Arial, sans-serif !important;
    }
    .rangers-banner {
        background: #002D72;
        color: white;
        padding: 22px 26px;
        border-radius: 14px;
        border-bottom: 6px solid #BA0C2F;
        margin-bottom: 18px;
        box-shadow: 0 5px 18px rgba(0,45,114,.22);
    }
    .banner-kicker {
        font-size: 15px;
        font-weight: 900;
        letter-spacing: .14em;
        text-transform: uppercase;
        opacity: .95;
        margin-bottom: 4px;
    }
    .banner-title {
        font-size: 38px;
        line-height: 1.05;
        font-weight: 950;
        margin: 0;
    }
    .banner-subtitle {
        font-size: 16px;
        font-weight: 700;
        color: rgba(255,255,255,.9);
        margin-top: 8px;
    }
    .banner-updated {
        font-size: 12px;
        font-weight: 700;
        color: rgba(255,255,255,.82);
        margin-top: 10px;
        letter-spacing: .03em;
        text-transform: uppercase;
    }
    .language-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-bottom: 8px;
        gap: 8px;
    }
    .language-caption {
        font-size: 12px;
        color: #857874;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .06em;
    }
    .main-title {
        font-size: 38px;
        font-weight: 900;
        margin-bottom: -8px;
        color: #002D72;
    }
    .subtitle {
        font-size: 16px;
        color: #857874;
        margin-bottom: 20px;
    }
    .league-card {
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid #857874;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(0,45,114,.10);
        min-height: 145px;
    }
    .rank-number {
        font-size: 34px;
        font-weight: 900;
    }
    .player-name {
        font-size: 22px;
        font-weight: 900;
        color: #002D72;
    }
    .metric-big {
        font-size: 32px;
        font-weight: 900;
        color: #002D72;
    }
    .info-card {
        border: 1px solid rgba(133,120,116,.55);
        border-radius: 12px;
        background: #ffffff;
        padding: 13px 15px;
        min-height: 76px;
        box-shadow: 0 2px 8px rgba(0,45,114,.06);
    }
    .info-card-label {
        font-size: 12px;
        line-height: 1.15;
        font-weight: 850;
        letter-spacing: .07em;
        text-transform: uppercase;
        color: #857874;
        margin-bottom: 8px;
    }
    .info-card-value {
        font-size: clamp(14px, 1.25vw, 18px);
        line-height: 1.18;
        font-weight: 850;
        color: #002D72;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    .small-label {
        font-size: 13px;
        color: #857874;
        text-transform: uppercase;
        letter-spacing: .06em;
        font-weight: 700;
    }
    .positive-money {
        color: #15803d;
        font-weight: 900;
    }
    .negative-money {
        color: #BA0C2F;
        font-weight: 900;
    }
    .section-note {
        color: #857874;
        font-size: 14px;
        margin-top: -8px;
        margin-bottom: 12px;
    }
    .heatmap-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        margin-bottom: 18px;
    }
    .heatmap-table th {
        background: #002D72;
        color: white;
        text-align: left;
        padding: 9px 10px;
        border: 1px solid #857874;
        font-weight: 800;
    }
    .heatmap-table td {
        padding: 8px 10px;
        border: 1px solid #857874;
        color: #002D72;
        background: white;
    }
    .heatmap-table tr:nth-child(even) td {
        background: #f7f7f7;
    }
    .heatmap-table a {
        color: #002D72;
        font-weight: 800;
        text-decoration: none;
    }
    a {
        text-decoration: none !important;
    }
    a:hover {
        text-decoration: none !important;
    }
    .heatmap-table a:hover {
        text-decoration: none !important;
        color: #BA0C2F;
    }
    .top-nav-label {
        color: #857874;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin: 2px 0 6px 0;
    }
    .top-nav-wrap {
        margin-top: -4px;
        margin-bottom: 14px;
    }
    div.stButton > button {
        border-radius: 10px;
        font-weight: 800;
        letter-spacing: .02em;
    }
    [data-testid="stMetricLabel"] {
        color: #857874;
        font-weight: 800;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(20px, 2.1vw, 30px) !important;
        line-height: 1.1 !important;
        white-space: nowrap !important;
    }
    [data-testid="stMetric"] {
        overflow: visible !important;
    }
    h1, h2, h3, h4 {
        color: #002D72 !important;
        font-weight: 850 !important;
        letter-spacing: -.02em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------

TEXT = {
    "ES": {
        "app_title": "Rangers Incentive League",
        "banner_kicker": "Texas Rangers",
        "banner_title": "DSL 2026 Programa de Incentivos",
        "position_players": "Jugadores de Posición",
        "pitchers": "Lanzadores",
        "program_bank": "Banco del Programa",
        "average": "Promedio",
        "leader": "Líder",
        "players": "Jugadores",
        "top_performers": "Mejores Rendimientos",
        "primary_sources": "Fuentes Principales de Ganancias",
        "primary_sources_note": "Top 3 jugadores y los stats que más han aportado a sus ganancias acumuladas dentro del programa.",
        "stats_leaders": "Líderes por Stats",
        "stats_leaders_note": "Top 3 jugadores por cada stat positivo del programa de incentivos DSL 2026.",
        "full_standings": "Ranking General",
        "full_standings_note": "Haz click en cualquier nombre para abrir el reporte individual del jugador.",
        "team": "Equipo",
        "biggest_contributor": "Mayor Aporte",
        "individual_report": "Reporte individual",
        "current_earnings": "Ganancias Actuales",
        "program_rank": "Ranking del Programa",
        "group": "Grupo",
        "back": "Volver al Ranking General",
        "earnings_sources": "Fuentes de Ganancias",
        "earnings_sources_note": "Stats que más han aportado a sus ganancias dentro del programa de incentivos DSL 2026.",
        "deductions": "Pérdidas",
        "deductions_note": "Stats donde el jugador ha perdido ganancias dentro del programa de incentivos DSL 2026.",
        "no_positive": "Todavía no hay ganancias positivas registradas.",
        "no_deductions": "No hay pérdidas registradas.",
        "player_summary": "Resumen de Incentivos del Jugador",
        "primary_source": "Fuente Principal de Ganancias",
        "largest_deduction": "Mayor Pérdida",
        "no_main_source": "Todavía no hay una fuente principal de ganancias.",
        "full_breakdown": "Desglose Completo de Ganancias",
        "upload_label": "Subir otro Excel de incentivos",
        "using_uploaded": "Excel subido activo",
        "using_default": "Excel predeterminado activo",
        "upload_needed": "Sube el Excel de incentivos para generar el reporte DSL 2026 de Texas Rangers.",
        "no_default": "No se encontró un Excel predeterminado. Sube un Excel con las hojas 'Position Players' y 'Pitchers'.",
        "read_error": "No pude leer el archivo",
        "process_error": "Error procesando la hoja",
        "not_found": "No encontré ese jugador.",
        "no_data": "Todavía no hay datos disponibles.",
        "footer": "Texas Rangers Baseball Club · DSL 2026 Programa de Incentivos",
        "language": "Idioma",
        "updated": "Actualizado",
        "export_summary": "Exportar Resumen Ejecutivo",
        "export_help": "Descarga un PDF ejecutivo con jugadores de posición y lanzadores.",
        "summary_pdf_name": "resumen_ejecutivo_incentivos_rangers.pdf",
        "top_performers_pdf": "Mejores Rendimientos",
        "full_items_pdf": "Ranking General con Items",
        "col_rank": "Rank",
        "col_player": "Jugador",
        "col_team": "Equipo",
        "col_total": "Ganancias",
        "col_biggest_contributor": "Mayor Aporte",
        "col_stats": "Stats",
        "col_qty": "Cant.",
        "col_weight": "Peso",
        "col_earnings": "Ganancias"
    },
    "EN": {
        "app_title": "Rangers Incentive League",
        "banner_kicker": "Texas Rangers",
        "banner_title": "DSL 2026 Incentive Program",
        "position_players": "Position Players",
        "pitchers": "Pitchers",
        "program_bank": "Program Bank",
        "average": "Average",
        "leader": "Leader",
        "players": "Players",
        "top_performers": "Top Performers",
        "primary_sources": "Primary Earnings Sources",
        "primary_sources_note": "Top 3 players and the stats that have contributed the most to their accumulated earnings in the program.",
        "stats_leaders": "Stats Leaders",
        "stats_leaders_note": "Top 3 players for each positive stat in the DSL 2026 incentive program.",
        "full_standings": "Full Standings",
        "full_standings_note": "Click any player name to open the individual report.",
        "team": "Team",
        "biggest_contributor": "Biggest Contributor",
        "individual_report": "Individual report",
        "current_earnings": "Current Earnings",
        "program_rank": "Program Rank",
        "group": "Group",
        "back": "Back to Full Standings",
        "earnings_sources": "Earnings Sources",
        "earnings_sources_note": "Stats that have contributed the most to the player's earnings in the DSL 2026 incentive program.",
        "deductions": "Earnings Lost",
        "deductions_note": "Stats where the player has lost earnings in the DSL 2026 incentive program.",
        "no_positive": "No positive earnings registered yet.",
        "no_deductions": "No earnings lost registered.",
        "player_summary": "Player Incentive Summary",
        "primary_source": "Primary Earnings Source",
        "largest_deduction": "Largest Loss",
        "no_main_source": "No main earnings source yet.",
        "full_breakdown": "Full Earnings Breakdown",
        "upload_label": "Upload a different incentives Excel",
        "using_uploaded": "Uploaded Excel active",
        "using_default": "Default Excel active",
        "upload_needed": "Upload the incentives Excel to generate the DSL 2026 Texas Rangers incentive report.",
        "no_default": "No default Excel was found. Upload an Excel with the sheets 'Position Players' and 'Pitchers'.",
        "read_error": "Could not read the file",
        "process_error": "Error processing sheet",
        "not_found": "Player not found.",
        "no_data": "No data available yet.",
        "footer": "Texas Rangers Baseball Club · DSL 2026 Incentive Program",
        "language": "Language",
        "updated": "Updated",
        "export_summary": "Export Executive Summary",
        "export_help": "Download an executive PDF with position players and pitchers.",
        "summary_pdf_name": "rangers_incentives_executive_summary.pdf",
        "top_performers_pdf": "Top Performers",
        "full_items_pdf": "Full Standings with Items",
        "col_rank": "Rank",
        "col_player": "Player",
        "col_team": "Team",
        "col_total": "Earnings",
        "col_biggest_contributor": "Biggest Contributor",
        "col_stats": "Stats",
        "col_qty": "Qty",
        "col_weight": "Weight",
        "col_earnings": "Earnings"
    }
}

def get_lang():
    if "language" not in st.session_state:
        st.session_state["language"] = "ES"
    return st.session_state["language"]

def t(key):
    return TEXT[get_lang()].get(key, key)


def display_group_name(group_name):
    if group_name == "Position Players":
        return t("position_players")
    if group_name == "Pitchers":
        return t("pitchers")
    return str(group_name)


def team_display(team_value):
    value = str(team_value).strip()
    if value.upper() == "R":
        return "Rojo" if get_lang() == "ES" else "Red"
    if value.upper() == "B":
        return "Azul" if get_lang() == "ES" else "Blue"
    return value


def team_display_static(team_value, lang="ES"):
    value = str(team_value).strip()
    if value.upper() == "R":
        return "Rojo" if lang == "ES" else "Red"
    if value.upper() == "B":
        return "Azul" if lang == "ES" else "Blue"
    return value


def col_label(name):
    labels = {
        "Rank": t("col_rank"),
        "Player": t("col_player"),
        "Team": t("col_team"),
        "Total": t("col_total"),
        "Biggest Contributor": t("col_biggest_contributor"),
        "Stats": t("col_stats"),
        "Qty": t("col_qty"),
        "Weight": t("col_weight"),
        "Earnings": t("col_earnings"),
    }
    return labels.get(name, name)

def set_language(lang):
    st.session_state["language"] = lang

def show_language_nav():
    st.markdown('<div class="language-bar">', unsafe_allow_html=True)
    c0, c1, c2 = st.columns([8.8, 0.6, 0.6])
    with c0:
        st.markdown(f'<div class="language-caption">{t("language")}</div>', unsafe_allow_html=True)
    with c1:
        st.button("🇪🇸", key="lang_es", use_container_width=True, type="primary" if get_lang() == "ES" else "secondary", on_click=set_language, args=("ES",))
    with c2:
        st.button("🇺🇸", key="lang_en", use_container_width=True, type="primary" if get_lang() == "EN" else "secondary", on_click=set_language, args=("EN",))
    st.markdown('</div>', unsafe_allow_html=True)


def money_fmt(value):
    try:
        value = float(value)
    except Exception:
        value = 0
    sign = "-" if value < 0 else ""
    return f"{sign}RD${abs(value):,.0f}"


def show_program_banner(group_name=None, updated_label=None):
    group_html = f" — {html_escape(display_group_name(group_name))}" if group_name else ""
    updated_html = f'<div class="banner-updated">{t("updated")}: {html_escape(updated_label)}</div>' if updated_label else ""
    st.markdown(
        f"""
        <div class="rangers-banner">
            <div class="banner-kicker">{t("banner_kicker")}</div>
            <div class="banner-title">{t("banner_title")}</div>
            <div class="banner-subtitle">{t("app_title")}{group_html}</div>
            {updated_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_group(group_name):
    st.session_state["selected_sheet"] = group_name
    st.query_params.clear()
    st.query_params["group"] = group_name


def show_group_nav(sheet_options, selected_sheet):
    if not sheet_options:
        return

    label_map = {
        "Position Players": t("position_players"),
        "Pitchers": t("pitchers"),
    }

    cols = st.columns(len(sheet_options))
    for col, sheet in zip(cols, sheet_options):
        label = label_map.get(sheet, sheet)
        with col:
            st.button(
                label,
                key=f"nav_{sheet}",
                use_container_width=True,
                type="primary" if sheet == selected_sheet else "secondary",
                on_click=set_group,
                args=(sheet,),
            )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def show_top_nav(sheet_options, selected_sheet):
    """Professional one-line navigation for player group."""
    if not sheet_options:
        return

    label_map = {
        "Position Players": t("position_players"),
        "Pitchers": t("pitchers"),
    }

    st.markdown('<div class="top-nav-wrap">', unsafe_allow_html=True)
    cols = st.columns([1, 1])

    for idx, sheet in enumerate(sheet_options[:2]):
        with cols[idx]:
            st.button(
                label_map.get(sheet, sheet),
                key=f"top_nav_{sheet}",
                use_container_width=True,
                type="primary" if sheet == selected_sheet else "secondary",
                on_click=set_group,
                args=(sheet,),
            )
    st.markdown('</div>', unsafe_allow_html=True)


def detect_header_and_weight_rows(raw):
    first_col = raw.iloc[:, 0].astype(str).str.strip().str.lower()
    header_candidates = raw.index[first_col.isin(["players", "pitchers"])].tolist()
    if not header_candidates:
        raise ValueError("No pude encontrar una fila que empiece con Players o Pitchers.")
    header_row = header_candidates[0]
    weight_row = header_row - 1
    return header_row, weight_row


def process_sheet(excel_file, sheet_name):
    if hasattr(excel_file, "seek"):
        excel_file.seek(0)
    raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    header_row, weight_row = detect_header_and_weight_rows(raw)

    headers = raw.iloc[header_row].tolist()
    weights = raw.iloc[weight_row].tolist()

    df = raw.iloc[header_row + 1:].copy()
    df.columns = headers
    df = df.dropna(how="all")

    first_col = headers[0]
    team_col = headers[1]
    total_col = "$RD"

    df = df.rename(columns={first_col: "Player", team_col: "Team"})
    df = df[df["Player"].notna()].copy()
    df["Player"] = df["Player"].astype(str).str.strip()

    category_cols = [
        c for c in df.columns
        if c not in ["Player", "Team", total_col]
        and pd.notna(c)
        and str(c).strip() != ""
    ]

    weight_map = {}
    for col, weight in zip(headers, weights):
        if col in category_cols:
            weight_map[col] = pd.to_numeric(weight, errors="coerce")

    for col in category_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    money_cols = []
    for col in category_cols:
        money_col = f"${col}"
        weight = weight_map.get(col, 0)
        if pd.isna(weight):
            weight = 0
        df[money_col] = df[col] * weight
        money_cols.append(money_col)

    df["Total Calculated"] = df[money_cols].sum(axis=1)
    if total_col in df.columns:
        df["Total Excel"] = pd.to_numeric(df[total_col], errors="coerce")
        df["Total"] = df["Total Excel"].fillna(df["Total Calculated"])
    else:
        df["Total"] = df["Total Calculated"]

    df["Rank"] = df["Total"].rank(method="min", ascending=False).astype(int)
    return df, category_cols, money_cols, weight_map


def player_breakdown(row, category_cols, weight_map):
    records = []
    for col in category_cols:
        qty = float(row[col]) if pd.notna(row[col]) else 0
        weight = weight_map.get(col, 0)
        if pd.isna(weight):
            weight = 0
        value = qty * weight
        if qty != 0 or value != 0:
            records.append({
                "Stats": col,
                "Qty": qty,
                "Weight": weight,
                "Earnings": value,
            })
    out = pd.DataFrame(records)
    if out.empty:
        return pd.DataFrame(columns=["Stats", "Qty", "Weight", "Earnings"])
    return out.sort_values("Earnings", ascending=False)


def top_positive_stat(row, category_cols, weight_map):
    bd = player_breakdown(row, category_cols, weight_map)
    positive = bd[bd["Earnings"] > 0].sort_values("Earnings", ascending=False)
    if positive.empty:
        return "—", 0
    top = positive.iloc[0]
    return str(top["Stats"]), float(top["Earnings"])


def player_link(player, group_name):
    return f"?view=player&group={quote(str(group_name))}&player={quote(str(player))}"


def html_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(v))):02x}" for v in rgb)


def blend(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((r1 + (r2-r1)*t, g1 + (g2-g1)*t, b1 + (b2-b1)*t))


def heat_color(value, vmin, vmax, cmap="RdYlGn"):
    try:
        value = float(value)
    except Exception:
        return "#ffffff"
    if vmax == vmin:
        t = 1.0
    else:
        t = (value - vmin) / (vmax - vmin)
    t = max(0, min(1, t))

    if cmap == "Greens":
        return blend("#dcfce7", "#15803d", t)
    if cmap == "Reds":
        return blend("#fde8ed", "#BA0C2F", t)

    # Red -> Yellow -> Green
    if t < 0.5:
        return blend("#fde8ed", "#fef3c7", t / 0.5)
    return blend("#fef3c7", "#22c55e", (t - 0.5) / 0.5)


def display_heatmap_table(df, columns=None, sort_by="Earnings", ascending=False, cmap="RdYlGn", group_name=None, player_link_cols=None):
    if df.empty:
        st.info(t("no_data"))
        return

    table = df.copy()
    if sort_by in table.columns:
        table = table.sort_values(sort_by, ascending=ascending)
    if columns:
        table = table[columns]

    player_link_cols = player_link_cols or []
    numeric_heat_cols = [c for c in table.columns if c in ["Total", "Earnings"] or pd.api.types.is_numeric_dtype(table[c])]
    # Only heatmap the most important money/value column when present.
    if "Earnings" in table.columns:
        heat_cols = ["Earnings"]
    elif "Total" in table.columns:
        heat_cols = ["Total"]
    else:
        heat_cols = [c for c in numeric_heat_cols if c not in ["Rank", "Qty", "Weight"]]

    mins = {c: pd.to_numeric(table[c], errors="coerce").min() for c in heat_cols}
    maxs = {c: pd.to_numeric(table[c], errors="coerce").max() for c in heat_cols}

    html = ['<table class="heatmap-table">']
    html.append("<thead><tr>")
    for c in table.columns:
        html.append(f"<th>{html_escape(col_label(c))}</th>")
    html.append("</tr></thead><tbody>")

    for _, row in table.iterrows():
        html.append("<tr>")
        for c in table.columns:
            val = row[c]
            style = ""
            if c in heat_cols:
                bg = heat_color(val, mins[c], maxs[c], cmap=cmap)
                style = f' style="background:{bg}; font-weight:800;"'
            if c in player_link_cols and group_name:
                display_val = html_escape(val)
                cell = f'<a href="{player_link(val, group_name)}" target="_self">{display_val}</a>'
            elif c == "Team":
                cell = html_escape(team_display(val))
            elif c in ["Total", "Earnings"]:
                cell = money_fmt(val)
            elif c == "Weight":
                cell = money_fmt(val).replace("RD$", "")
            elif c == "Qty":
                try:
                    cell = f"{float(val):,.0f}"
                except Exception:
                    cell = html_escape(val)
            else:
                cell = html_escape(val)
            html.append(f"<td{style}>{cell}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)



def pdf_money_fmt(value):
    try:
        value = float(value)
    except Exception:
        value = 0
    sign = "-" if value < 0 else ""
    return f"{sign}RD${abs(value):,.0f}"


def generate_executive_pdf(excel_source, sheet_options, updated_label, lang="ES"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(legal),
        rightMargin=0.18 * inch,
        leftMargin=0.18 * inch,
        topMargin=0.22 * inch,
        bottomMargin=0.20 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "RangersTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=18,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "RangersSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#002D72"),
        spaceBefore=4,
        spaceAfter=3,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=5.0,
        leading=5.45,
        textColor=colors.HexColor("#1f2937"),
        alignment=TA_LEFT,
    )
    cell_bold_style = ParagraphStyle(
        "CellBold",
        parent=cell_style,
        fontName="Helvetica-Bold",
        fontSize=6.0,
        leading=6.4,
        textColor=colors.HexColor("#002D72"),
    )
    header_cell_style = ParagraphStyle(
        "HeaderCell",
        parent=cell_style,
        fontName="Helvetica-Bold",
        fontSize=4.8,
        leading=5.25,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    total_cell_style = ParagraphStyle(
        "TotalCell",
        parent=cell_style,
        fontName="Helvetica-Bold",
        fontSize=6.1,
        leading=6.5,
        textColor=colors.HexColor("#111827"),
        alignment=TA_CENTER,
    )

    def pcell(value, bold=False, header=False, total=False):
        text = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace("\n", "<br/>")
        style = header_cell_style if header else (total_cell_style if total else (cell_bold_style if bold else cell_style))
        return Paragraph(text, style)

    def qty_fmt(qty):
        try:
            q = float(qty)
        except Exception:
            q = 0
        if abs(q - round(q)) < 0.00001:
            return f"{int(round(q)):,}"
        return f"{q:,.1f}"

    def money_qty_fmt(value, qty):
        try:
            v = float(value)
        except Exception:
            v = 0
        try:
            q = float(qty)
        except Exception:
            q = 0
        if abs(v) < 0.00001 and abs(q) < 0.00001:
            return "—"
        return f"{pdf_money_fmt(v)} ({qty_fmt(q)})"

    def get_pdf_top_rows(sheet_name, category_cols):
        """Return compact merged metadata rows for the PDF table.

        The source sheet uses top rows to explain each incentive item. This
        function preserves that structure but groups repeated cells visually:
        HITTING / DEFENSE / TEAM and DAILY / WEEKLY / TEAM are shown once per
        span instead of repeated above every item.
        """
        if hasattr(excel_source, "seek"):
            excel_source.seek(0)
        raw_meta = pd.read_excel(excel_source, sheet_name=sheet_name, header=None)
        header_row, weight_row = detect_header_and_weight_rows(raw_meta)
        header_values = raw_meta.iloc[header_row].tolist()

        col_positions = {}
        for idx, h in enumerate(header_values):
            if pd.notna(h):
                col_positions[str(h).strip()] = idx

        source_positions = [col_positions.get(str(col).strip()) for col in category_cols]
        valid_positions = [pos for pos in source_positions if pos is not None]
        min_pos = min(valid_positions) if valid_positions else 0
        max_pos = max(valid_positions) if valid_positions else raw_meta.shape[1] - 1

        def clean_meta_value(v):
            if pd.isna(v):
                return ""
            text = str(v).strip()
            if text.lower() == "nan":
                return ""
            if "INCENTIVOS" in text.upper() or "TEXAS RANGERS" in text.upper() or "ACTUALIZ" in text.upper():
                return ""
            return text

        def row_values_at(ridx):
            return [clean_meta_value(raw_meta.iat[ridx, c]) if c < raw_meta.shape[1] else "" for c in range(raw_meta.shape[1])]

        def ff_all(raw_vals):
            last = ""
            filled = []
            for c, val in enumerate(raw_vals):
                if c < min_pos or c > max_pos:
                    filled.append(val)
                    continue
                if val != "":
                    last = val
                filled.append(last)
            return filled

        def values_for_category_positions(filled):
            return [filled[pos] if pos is not None and pos < len(filled) else "" for pos in source_positions]

        # Identify text metadata rows above the header. Ignore weight/title rows.
        text_rows = []
        for ridx in range(header_row):
            if ridx == weight_row:
                continue
            raw_vals = row_values_at(ridx)
            region_vals = [raw_vals[c] for c in range(min_pos, max_pos + 1) if c < len(raw_vals)]
            non_empty = [v for v in region_vals if str(v).strip() != ""]
            if not non_empty:
                continue
            text_count = 0
            for val in non_empty:
                try:
                    float(str(val).replace("RD$", "").replace(",", ""))
                except Exception:
                    text_count += 1
            if text_count:
                text_rows.append(ridx)

        meta_rows = []
        span_commands = []
        parent_groups = None

        def append_grouped_row(label, values):
            row_index = len(meta_rows)
            row = [pcell(label, bold=True), pcell(""), pcell(""), pcell("")]
            groups = []
            start = 0
            while start < len(values):
                val = str(values[start]).strip().upper()
                end = start
                while end + 1 < len(values) and str(values[end + 1]).strip().upper() == val:
                    end += 1
                groups.append((start, end, val))
                start = end + 1
            for i, val in enumerate([str(v).strip().upper() for v in values]):
                # Show value only in first cell of a group; merged cells take the label.
                first_in_group = any(g[0] == i for g in groups)
                row.append(pcell(val if first_in_group else "", bold=True))
            meta_rows.append(row)
            # Merge label cells over Rank/Player/Team/Total area.
            span_commands.append(("SPAN", (0, row_index), (3, row_index)))
            for start, end, val in groups:
                if val and end > start:
                    span_commands.append(("SPAN", (4 + start, row_index), (4 + end, row_index)))

        # First text row can be item area (HITTING/DEFENSE/TEAM) or directly type.
        for n, ridx in enumerate(text_rows):
            raw_vals = row_values_at(ridx)
            filled = ff_all(raw_vals)
            vals = values_for_category_positions(filled)
            upper_vals = [str(v).strip().upper() for v in vals]
            unique_vals = {v for v in upper_vals if v}

            # If a later metadata row is blank under a TEAM area, classify it as TEAM.
            if parent_groups is not None:
                raw_item_vals = values_for_category_positions(raw_vals)
                adjusted = []
                last_by_parent = {}
                for i, raw_v in enumerate(raw_item_vals):
                    parent = parent_groups[i] if i < len(parent_groups) else ""
                    if str(raw_v).strip():
                        last_by_parent[parent] = str(raw_v).strip()
                        adjusted.append(str(raw_v).strip())
                    else:
                        if str(parent).strip().upper() == "TEAM":
                            adjusted.append("TEAM")
                        else:
                            adjusted.append(last_by_parent.get(parent, ""))
                vals = adjusted
                upper_vals = [str(v).strip().upper() for v in vals]
                unique_vals = {v for v in upper_vals if v}

            lowered = {v.lower() for v in unique_vals}
            is_type_row = bool(lowered & {"daily", "weekly", "team", "diario", "semana", "semanal", "equipo"})
            label = ("Tipo" if lang == "ES" else "Type") if is_type_row else ("Grupo" if lang == "ES" else "Group")
            append_grouped_row(label, vals)

            # Save parent group if this looks like the area row (HITTING/DEFENSE/TEAM).
            if not is_type_row or ("HITTING" in unique_vals or "DEFENSE" in unique_vals):
                parent_groups = upper_vals

        # Weight row: group label cells but keep individual weights visible.
        if weight_row is not None and weight_row < raw_meta.shape[0]:
            weight_values = []
            for col in category_cols:
                pos = col_positions.get(str(col).strip())
                val = raw_meta.iat[weight_row, pos] if pos is not None and pos < raw_meta.shape[1] else ""
                if pd.isna(val) or str(val).strip() == "":
                    weight_values.append("")
                else:
                    weight_values.append(pdf_money_fmt(val))
            label = "Peso" if lang == "ES" else "Weight"
            row_index = len(meta_rows)
            meta_rows.append([pcell(label, bold=True), pcell(""), pcell(""), pcell("")] + [pcell(v, bold=True) for v in weight_values])
            span_commands.append(("SPAN", (0, row_index), (3, row_index)))

        return meta_rows, span_commands

    def blend(c1, c2, pct):
        pct = max(0, min(1, pct))
        return tuple(int(c1[i] + (c2[i] - c1[i]) * pct) for i in range(3))

    def total_gradient_color(value, min_value, max_value):
        # Low totals = red, midpoint = pale yellow, high totals = green.
        red = (248, 113, 113)
        yellow = (254, 243, 199)
        green = (134, 239, 172)
        if max_value == min_value:
            rgb = yellow
        else:
            pct = (float(value) - float(min_value)) / (float(max_value) - float(min_value))
            if pct <= 0.5:
                rgb = blend(red, yellow, pct / 0.5)
            else:
                rgb = blend(yellow, green, (pct - 0.5) / 0.5)
        return colors.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

    story = []
    pages = [s for s in ["Position Players", "Pitchers"] if s in sheet_options]
    if not pages:
        pages = sheet_options[:2]

    for page_idx, sheet in enumerate(pages):
        df, category_cols, money_cols, weight_map = process_sheet(excel_source, sheet)
        group_label = ("Jugadores de Posición" if sheet == "Position Players" else "Lanzadores") if lang == "ES" else ("Position Players" if sheet == "Position Players" else "Pitchers")
        header_title = "DSL 2026 PROGRAMA DE INCENTIVOS" if lang == "ES" else "DSL 2026 INCENTIVE PROGRAM"
        updated_word = "Actualizado" if lang == "ES" else "Updated"
        header_subtitle = f"Texas Rangers Baseball Club · {group_label} · {updated_word}: {updated_label}"
        header = Table([[Paragraph(header_title, title_style)], [Paragraph(header_subtitle, subtitle_style)]], colWidths=[13.60 * inch])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#002D72")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#002D72")),
            ("LINEBELOW", (0, -1), (-1, -1), 3, colors.HexColor("#BA0C2F")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(header)
        story.append(Spacer(1, 0.06 * inch))

        story.append(Paragraph(t("full_items_pdf"), section_style))
        headers = ["Rank", "Player" if lang == "EN" else "Jugador", "Team" if lang == "EN" else "Equipo", "Total"] + [str(c) for c in category_cols]
        meta_rows, meta_spans = get_pdf_top_rows(sheet, category_cols)
        money_matrix = meta_rows + [[pcell(h, header=True) for h in headers]]
        header_pdf_row = len(meta_rows)
        first_data_row = header_pdf_row + 1
        full = df.sort_values("Rank").copy()
        totals = pd.to_numeric(full["Total"], errors="coerce").fillna(0)
        min_total = float(totals.min()) if not totals.empty else 0
        max_total = float(totals.max()) if not totals.empty else 0

        for _, r in full.iterrows():
            row = [
                pcell(f"#{int(r['Rank'])}"),
                pcell(r["Player"], bold=True),
                pcell(team_display_static(r.get("Team", ""), lang)),
                pcell(pdf_money_fmt(r["Total"]), total=True),
            ]
            for c in category_cols:
                w = weight_map.get(c, 0)
                qty = float(r[c]) if pd.notna(r[c]) else 0
                val = qty * (0 if pd.isna(w) else w)
                row.append(pcell(money_qty_fmt(val, qty)))
            money_matrix.append(row)

        page_width = 13.60 * inch
        fixed = 0.38*inch + 1.72*inch + 0.50*inch + 0.88*inch
        remaining = page_width - fixed
        raw_stat_widths = []
        for col in category_cols:
            text_len = max(len(str(col)), 7)
            raw_stat_widths.append(min(0.95*inch, max(0.34*inch, (0.20 + text_len * 0.035) * inch)))
        raw_total = sum(raw_stat_widths) if raw_stat_widths else 1
        scale = remaining / raw_total
        stat_widths = [max(0.32*inch, w * scale) for w in raw_stat_widths]
        col_widths = [0.38*inch, 1.72*inch, 0.50*inch, 0.88*inch] + stat_widths
        item_table = Table(money_matrix, colWidths=col_widths, repeatRows=header_pdf_row + 1)
        ts = [
            ("BACKGROUND", (0, 0), (-1, max(0, header_pdf_row - 1)), colors.HexColor("#EEF2F7")),
            ("TEXTCOLOR", (0, 0), (-1, max(0, header_pdf_row - 1)), colors.HexColor("#002D72")),
            ("FONTNAME", (0, 0), (-1, max(0, header_pdf_row - 1)), "Helvetica-Bold"),
            ("BACKGROUND", (0, header_pdf_row), (-1, header_pdf_row), colors.HexColor("#002D72")),
            ("TEXTCOLOR", (0, header_pdf_row), (-1, header_pdf_row), colors.white),
            ("FONTNAME", (0, header_pdf_row), (-1, header_pdf_row), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.22, colors.HexColor("#857874")),
            ("FONTSIZE", (0, 0), (-1, -1), 4.8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, first_data_row), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("FONTNAME", (1, first_data_row), (1, -1), "Helvetica-Bold"),
            ("FONTNAME", (3, first_data_row), (3, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (1, first_data_row), (1, -1), "LEFT"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1.2),
        ]

        ts.extend(meta_spans)

        # Total earnings gradient: highest totals green, lowest totals red.
        for ridx, (_, r) in enumerate(full.iterrows(), start=first_data_row):
            ts.append(("BACKGROUND", (3, ridx), (3, ridx), total_gradient_color(r["Total"], min_total, max_total)))

            # Color item text only: green for gains, Rangers red for losses.
            for cidx, c in enumerate(category_cols, start=4):
                w = weight_map.get(c, 0)
                qty = float(r[c]) if pd.notna(r[c]) else 0
                val = qty * (0 if pd.isna(w) else w)
                if val > 0:
                    ts.append(("BACKGROUND", (cidx, ridx), (cidx, ridx), colors.HexColor("#DCFCE7")))
                    ts.append(("TEXTCOLOR", (cidx, ridx), (cidx, ridx), colors.HexColor("#166534")))
                elif val < 0:
                    ts.append(("BACKGROUND", (cidx, ridx), (cidx, ridx), colors.HexColor("#FEE2E2")))
                    ts.append(("TEXTCOLOR", (cidx, ridx), (cidx, ridx), colors.HexColor("#991B1B")))
        item_table.setStyle(TableStyle(ts))
        story.append(item_table)
        if page_idx < len(pages) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def clear_query_and_go_home():
    st.query_params.clear()
    st.session_state["view"] = "home"


def show_top_cards(df, category_cols, weight_map, group_name):
    top3 = df.sort_values("Total", ascending=False).head(3).reset_index(drop=True)
    rank_labels = ["#1", "#2", "#3"]
    cols = st.columns(3)
    for i, col in enumerate(cols):
        if i < len(top3):
            r = top3.iloc[i]
            top_stat, top_earnings = top_positive_stat(r, category_cols, weight_map)
            name = html_escape(r["Player"])
            url = player_link(r["Player"], group_name)
            col.markdown(
                f"""
                <div class="league-card">
                    <div class="rank-number">{rank_labels[i]}</div>
                    <div class="player-name"><a href="{url}" target="_self" style="color:#002D72;text-decoration:none;">{name}</a></div>
                    <div class="small-label">{t("team")} {html_escape(team_display(r.get('Team', '')))}</div>
                    <div style="height:10px"></div>
                    <div class="metric-big">{money_fmt(r['Total'])}</div>
                    <div style="height:8px"></div>
                    <div class="small-label">{t("biggest_contributor")}</div>
                    <div class="positive-money">{html_escape(top_stat)} — {money_fmt(top_earnings)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show_top_money_sources(df, category_cols, weight_map, group_name):
    top_players = df.sort_values("Total", ascending=False).head(3)
    for _, player in top_players.iterrows():
        bd = player_breakdown(player, category_cols, weight_map)
        positive = bd[bd["Earnings"] > 0].sort_values("Earnings", ascending=False).head(5)
        if positive.empty:
            continue

        url = player_link(player["Player"], group_name)
        st.markdown(f"### #{int(player['Rank'])} [{player['Player']}]({url}) — {money_fmt(player['Total'])}")
        display_heatmap_table(
            positive,
            columns=["Stats", "Qty", "Weight", "Earnings"],
            sort_by="Earnings",
            ascending=False,
            cmap="Greens",
            group_name=group_name,
        )


def show_full_standings(df, category_cols, weight_map, group_name):
    standings = df[["Rank", "Player", "Team", "Total"]].sort_values("Rank").copy()
    contributors = df.apply(lambda r: top_positive_stat(r, category_cols, weight_map), axis=1)
    contributor_map = {
        player: f"{stat} ({money_fmt(value)})" if stat != "—" else "—"
        for player, (stat, value) in zip(df["Player"], contributors)
    }
    standings["Biggest Contributor"] = standings["Player"].map(contributor_map)

    display_heatmap_table(
        standings,
        columns=["Rank", "Player", "Team", "Total", "Biggest Contributor"],
        sort_by="Rank",
        ascending=True,
        cmap="RdYlGn",
        group_name=group_name,
        player_link_cols=["Player"],
    )


def show_category_leaders(df, category_cols, weight_map, group_name):
    positive_categories = [c for c in category_cols if weight_map.get(c, 0) and weight_map.get(c, 0) > 0]
    if not positive_categories:
        return

    st.subheader(t("stats_leaders"))
    st.markdown(f'<div class="section-note">{t("stats_leaders_note")}</div>', unsafe_allow_html=True)

    selected_categories = positive_categories[:6]
    cols = st.columns(3)
    for idx, cat in enumerate(selected_categories):
        with cols[idx % 3]:
            leaders = df[["Player", cat]].copy()
            leaders[cat] = pd.to_numeric(leaders[cat], errors="coerce").fillna(0)
            leaders = leaders.sort_values(cat, ascending=False).head(3)
            st.markdown(f"#### {cat}")
            display_heatmap_table(
                leaders,
                columns=["Player", cat],
                sort_by=cat,
                ascending=False,
                cmap="RdYlGn",
                group_name=group_name,
                player_link_cols=["Player"],
            )


def show_general_page(df, category_cols, money_cols, weight_map, group_name, sheet_options, excel_source, updated_label=None):
    show_language_nav()
    show_program_banner(group_name, updated_label)
    show_top_nav(sheet_options, group_name)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("program_bank"), money_fmt(df["Total"].sum()))
    c2.metric(t("average"), money_fmt(df["Total"].mean()))
    c3.metric(t("leader"), money_fmt(df["Total"].max()))
    c4.metric(t("players"), f"{len(df)}")

    pdf_bytes = generate_executive_pdf(excel_source, sheet_options, updated_label, get_lang())
    st.download_button(
        t("export_summary"),
        data=pdf_bytes,
        file_name=t("summary_pdf_name"),
        mime="application/pdf",
        help=t("export_help"),
        use_container_width=True,
    )

    st.divider()
    st.subheader(t("top_performers"))
    show_top_cards(df, category_cols, weight_map, group_name)

    st.divider()
    st.subheader(t("primary_sources"))
    st.markdown(f'<div class="section-note">{t("primary_sources_note")}</div>', unsafe_allow_html=True)
    show_top_money_sources(df, category_cols, weight_map, group_name)

    st.divider()
    show_category_leaders(df, category_cols, weight_map, group_name)

    st.divider()
    st.subheader(t("full_standings"))
    st.markdown(f'<div class="section-note">{t("full_standings_note")}</div>', unsafe_allow_html=True)
    show_full_standings(df, category_cols, weight_map, group_name)
    st.markdown(f'<div style="color:#857874;font-size:13px;margin-top:20px;text-align:center;">{t("footer")}</div>', unsafe_allow_html=True)



def small_info_card(label, value):
    st.markdown(
        f"""<div class="info-card">
            <div class="info-card-label">{html_escape(str(label))}</div>
            <div class="info-card-value">{html_escape(str(value))}</div>
        </div>""",
        unsafe_allow_html=True,
    )

def show_player_page(df, category_cols, weight_map, selected_player, group_name, sheet_options, updated_label=None):
    player_rows = df[df["Player"] == selected_player]
    if player_rows.empty:
        st.error(t("not_found"))
        return

    show_language_nav()
    show_program_banner(group_name, updated_label)
    show_top_nav(sheet_options, group_name)

    row = player_rows.iloc[0]
    bd = player_breakdown(row, category_cols, weight_map)
    positive = bd[bd["Earnings"] > 0].sort_values("Earnings", ascending=False)
    negative = bd[bd["Earnings"] < 0].sort_values("Earnings")

    st.markdown(f'<div class="main-title">{html_escape(selected_player)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{t("individual_report")} — {display_group_name(group_name)}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("current_earnings"), money_fmt(row["Total"]))
    c2.metric(t("program_rank"), f"#{int(row['Rank'])}")
    with c3:
        small_info_card(t("team"), team_display(row.get("Team", "")))
    with c4:
        small_info_card(t("group"), display_group_name(group_name))

    st.markdown(f"[{t("back")}](?group={quote(str(group_name))})")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader(t("earnings_sources"))
        st.caption(t("earnings_sources_note"))
        if positive.empty:
            st.info(t("no_positive"))
        else:
            display_heatmap_table(
                positive.head(10),
                columns=["Stats", "Qty", "Weight", "Earnings"],
                sort_by="Earnings",
                ascending=False,
                cmap="Greens",
                group_name=group_name,
            )

    with right:
        st.subheader(t("deductions"))
        st.caption(t("deductions_note"))
        if negative.empty:
            st.success(t("no_deductions"))
        else:
            display_heatmap_table(
                negative.head(10),
                columns=["Stats", "Qty", "Weight", "Earnings"],
                sort_by="Earnings",
                ascending=True,
                cmap="Reds",
                group_name=group_name,
            )

    st.divider()
    st.subheader(t("player_summary"))
    c1, c2 = st.columns(2)
    if not positive.empty:
        top_strength = positive.iloc[0]
        c1.success(f"{t("primary_source")}: {top_strength['Stats']} — {money_fmt(top_strength['Earnings'])}")
    else:
        c1.info(t("no_main_source"))

    if not negative.empty:
        biggest_leak = negative.iloc[0]
        c2.error(f"{t("largest_deduction")}: {biggest_leak['Stats']} — {money_fmt(biggest_leak['Earnings'])}")
    else:
        c2.success(t("no_deductions"))

    st.subheader(t("full_breakdown"))
    display_heatmap_table(
        bd,
        columns=["Stats", "Qty", "Weight", "Earnings"],
        sort_by="Earnings",
        ascending=False,
        cmap="RdYlGn",
        group_name=group_name,
    )
    st.markdown(f'<div style="color:#857874;font-size:13px;margin-top:20px;text-align:center;">{t("footer")}</div>', unsafe_allow_html=True)


# -----------------------------
# App
# -----------------------------
DEFAULT_EXCEL_PATH = Path(__file__).with_name("Incentives System - DR TEX 2026.xlsx")

st.sidebar.title("Rangers Incentive League")
uploaded_file = st.sidebar.file_uploader(t("upload_label"), type=["xlsx"])

if uploaded_file is not None:
    excel_source = uploaded_file
    st.sidebar.success(t("using_uploaded"))
elif DEFAULT_EXCEL_PATH.exists():
    excel_source = DEFAULT_EXCEL_PATH
    st.sidebar.success(t("using_default"))
else:
    show_program_banner()
    st.markdown(
        f'<div class="subtitle">{t("upload_needed")}</div>',
        unsafe_allow_html=True,
    )
    st.info(t("no_default"))
    st.stop()


def get_updated_label(source):
    try:
        if isinstance(source, (str, Path)):
            dt = datetime.fromtimestamp(Path(source).stat().st_mtime)
        else:
            dt = datetime.now()
        if get_lang() == "ES":
            return dt.strftime("%d/%m/%Y")
        return dt.strftime("%m/%d/%Y")
    except Exception:
        return datetime.now().strftime("%d/%m/%Y" if get_lang() == "ES" else "%m/%d/%Y")

updated_label = get_updated_label(excel_source)

try:
    if hasattr(excel_source, "seek"):
        excel_source.seek(0)
    sheet_names = pd.ExcelFile(excel_source).sheet_names
except Exception as e:
    st.error(f"{t("read_error")}: {e}")
    st.stop()

preferred = [s for s in ["Position Players", "Pitchers"] if s in sheet_names]
other = [s for s in sheet_names if s not in preferred]
sheet_options = preferred + other

query_group = st.query_params.get("group")
query_player = st.query_params.get("player")
query_view = st.query_params.get("view")

if "selected_sheet" not in st.session_state or st.session_state["selected_sheet"] not in sheet_options:
    st.session_state["selected_sheet"] = sheet_options[0]

if query_group in sheet_options:
    st.session_state["selected_sheet"] = query_group

selected_sheet = st.session_state["selected_sheet"]

try:
    df, category_cols, money_cols, weight_map = process_sheet(excel_source, selected_sheet)
except Exception as e:
    st.error(f"{t("process_error")} {selected_sheet}: {e}")
    st.stop()

players = df.sort_values("Total", ascending=False)["Player"].tolist()

if query_view == "player" and query_player in players:
    show_player_page(df, category_cols, weight_map, query_player, selected_sheet, sheet_options, updated_label)
else:
    show_general_page(df, category_cols, money_cols, weight_map, selected_sheet, sheet_options, excel_source, updated_label)
