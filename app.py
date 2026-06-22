from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import legal, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image

st.set_page_config(
     page_title="Texas Rangers | DSL 2026 Incentivos",
    page_icon="Texas-Rangers-Symbol-cropped.png",
    layout="wide",
    initial_sidebar_state="collapsed",
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

    [data-testid="stSidebar"] {
    display: none;
    }

    [data-testid="collapsedControl"] {
    display: none;
    }

    #MainMenu {
    visibility: hidden;
    }

    /* Oculta footer */
    footer {
        visibility: hidden;
    }

    /* Oculta header Streamlit */
    header {
        visibility: hidden;
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
        "export_summary": "Exportar Resumen",
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
        "export_summary": "Export Summary",
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

def pdf_number_fmt(value):
    try:
        value = float(value)
    except Exception:
        value = 0
    sign = "-" if value < 0 else ""
    return f"{sign}{abs(value):,.0f}"


def generate_executive_pdf(excel_source, sheet_options, updated_label, lang="ES"):
    """Create the executive PDF downloaded by Export Summary.

    The PDF is intentionally kept in English for staff consistency while the
    Streamlit interface remains bilingual.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(legal),
        rightMargin=0.18 * inch,
        leftMargin=0.18 * inch,
        topMargin=0.16 * inch,
        bottomMargin=0.18 * inch,
    )

    page_width = 13.20 * inch
    RANGERS_BLUE = colors.HexColor("#002D72")
    RANGERS_RED = colors.HexColor("#BA0C2F")
    RANGERS_GRAY = colors.HexColor("#857874")
    LIGHT_GRAY = colors.HexColor("#F1F3F5")
    DARK_GREEN = colors.HexColor("#006B2E")
    BLACK = colors.HexColor("#111827")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PDFMainTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19.5,
        leading=21.0,
        textColor=RANGERS_BLUE,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    subtitle_style = ParagraphStyle(
        "PDFSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.8,
        leading=14.2,
        textColor=RANGERS_RED,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    updated_style = ParagraphStyle(
        "PDFUpdated",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.4,
        leading=8.2,
        textColor=RANGERS_BLUE,
        alignment=TA_LEFT,
    )
    section_badge_style = ParagraphStyle(
        "PDFBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.0,
        leading=11.0,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    group_style = ParagraphStyle(
        "PDFGroup",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.0,
        leading=6.5,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    header_style = ParagraphStyle(
        "PDFHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.6,
        leading=7.2,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    player_style = ParagraphStyle(
        "PDFPlayer",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=11.2,
        textColor=RANGERS_BLUE,
        alignment=TA_CENTER,
        splitLongWords=0,
        wordWrap=None,
    )
    team_style = ParagraphStyle(
        "PDFTeam",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=4.9,
        leading=5.25,
        textColor=colors.white,
        alignment=TA_CENTER,
    )
    value_style = ParagraphStyle(
        "PDFValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.3,
        leading=8.1,
        textColor=BLACK,
        alignment=TA_CENTER,
        splitLongWords=0,
        wordWrap=None,
    )
    total_style = ParagraphStyle(
        "PDFTotal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.7,
        leading=11.6,
        textColor=colors.HexColor("#064E3B"),
        alignment=TA_CENTER,
        splitLongWords=0,
        wordWrap=None,
    )
    note_style = ParagraphStyle(
        "PDFNote",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=6.6,
        leading=7.3,
        textColor=RANGERS_BLUE,
        alignment=TA_LEFT,
    )
    slogan_style = ParagraphStyle(
        "PDFSlogan",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=10.0,
        textColor=RANGERS_BLUE,
        alignment=TA_RIGHT,
    )

    def esc(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def pcell(value, style=value_style):
        return Paragraph(esc(value).replace("\n", "<br/>"), style)

    def rich_cell(markup, style=value_style):
        return Paragraph(str(markup), style)

    def qty_fmt(qty):
        try:
            q = float(qty)
        except Exception:
            q = 0
        if abs(q - round(q)) < 0.00001:
            return f"{int(round(q)):,}"
        return f"{q:,.1f}"

    def money_qty_markup(value, qty):
        try:
            v = float(value)
        except Exception:
            v = 0
        try:
            q = float(qty)
        except Exception:
            q = 0
        if abs(v) < 0.00001 and abs(q) < 0.00001:
            return '<font color="#111827"><b>0&#160;(0)</b></font>'
        color = "#006B2E" if v > 0 else ("#BA0C2F" if v < 0 else "#111827")
        amount = pdf_number_fmt(v)
        return f'<font color="{color}"><b>{amount}&#160;({qty_fmt(q)})</b></font>'

    def team_pdf_label(value):
        value = str(value).strip().upper()
        if value == "R":
            return "RED"
        if value == "B":
            return "BLUE"
        return value

    def get_group_values(sheet_name, category_cols):
        """Return the top metadata row used for merged PDF table headers.

        Position Players uses a fixed incentive-frequency rule requested by the
        program: H10+, E0, W, and Chase% < 20% are TEAM incentives; SL+ is
        WEEKLY; all other position-player items are DAILY. Pitchers are left
        untouched and continue reading the existing metadata row from the Excel.
        """
        def normalize_item_name(value):
            return (
                str(value)
                .strip()
                .upper()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
            )

        if sheet_name == "Position Players":
            team_items = {"H10+", "E0", "W", "CHASE%<20%", "CHASE%<20", "CHASE<20%", "CHASE<20"}
            weekly_items = {"SL+"}
            forced_groups = []
            for col in category_cols:
                key = normalize_item_name(col)
                if key in team_items:
                    forced_groups.append("TEAM")
                elif key in weekly_items:
                    forced_groups.append("WEEKLY")
                else:
                    forced_groups.append("DAILY")
            return forced_groups

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
        if not valid_positions:
            return [""] * len(category_cols)
        min_pos, max_pos = min(valid_positions), max(valid_positions)

        def clean(v):
            if pd.isna(v):
                return ""
            text = str(v).strip()
            if text.lower() == "nan":
                return ""
            if "INCENTIVOS" in text.upper() or "TEXAS RANGERS" in text.upper() or "ACTUALIZ" in text.upper():
                return ""
            return text

        best = [""] * len(category_cols)
        best_score = (-1, -1, -1)
        for ridx in range(header_row):
            if ridx == weight_row:
                continue
            vals = [clean(raw_meta.iat[ridx, c]) if c < raw_meta.shape[1] else "" for c in range(raw_meta.shape[1])]
            # Forward-fill across incentive item columns to account for merged cells.
            last = ""
            filled = []
            for c, val in enumerate(vals):
                if c < min_pos or c > max_pos:
                    filled.append(val)
                    continue
                if val:
                    last = val
                filled.append(last)
            candidate = [filled[pos] if pos is not None and pos < len(filled) else "" for pos in source_positions]
            upper = [str(v).strip().upper() for v in candidate]

            # Prefer the frequency/type row for the PDF header.
            type_score = sum(1 for v in upper if v in {"DAILY", "WEEKLY", "TEAM", "DIARIO", "SEMANAL", "SEMANA", "EQUIPO"})
            group_score = sum(1 for v in upper if v in {"HITTING", "PITCHING", "DEFENSE"})
            total_score = type_score + group_score
            score = (type_score, total_score, ridx)
            if score > best_score:
                best_score = score
                best = upper
        return best

    def group_spans(groups):
        spans = []
        start = 0
        while start < len(groups):
            val = str(groups[start]).strip().upper()
            end = start
            while end + 1 < len(groups) and str(groups[end + 1]).strip().upper() == val:
                end += 1
            spans.append((start, end, val))
            start = end + 1
        return spans

    def blend(c1, c2, pct):
        pct = max(0, min(1, pct))
        return tuple(int(c1[i] + (c2[i] - c1[i]) * pct) for i in range(3))

    def total_gradient_color(value, min_value, max_value):
        red = (254, 202, 202)
        yellow = (254, 243, 199)
        green = (187, 247, 208)
        if max_value == min_value:
            rgb = yellow
        else:
            pct = (float(value) - float(min_value)) / (float(max_value) - float(min_value))
            if pct <= 0.5:
                rgb = blend(red, yellow, pct / 0.5)
            else:
                rgb = blend(yellow, green, (pct - 0.5) / 0.5)
        return colors.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

    def build_header(section_label):
        logo_candidates = [
            Path(__file__).with_name("Texas-Rangers-Symbol-cropped.png"),
            Path(__file__).with_name("Texas-Rangers-Symbol.png"),
            Path("/mnt/data/Texas-Rangers-Symbol-cropped.png"),
            Path("/mnt/data/Texas-Rangers-Symbol.png"),
        ]
        logo_path = next((p for p in logo_candidates if p.exists()), None)
        logo_cell = ""
        if logo_path:
            logo_cell = Image(str(logo_path), width=0.70 * inch, height=0.70 * inch)

        title_block = [
            [Paragraph("TEXAS RANGERS", title_style)],
            [Paragraph("2026 DSL INCENTIVE SUMMARY", subtitle_style)],
            [Paragraph(f"Last Updated: {esc(updated_label)}", updated_style)],
        ]
        title_table = Table(title_block, colWidths=[7.95 * inch])
        title_table.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        badge = Table([[Paragraph(section_label.upper(), section_badge_style)]], colWidths=[2.45 * inch], rowHeights=[0.27 * inch])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), RANGERS_RED),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]))
        spacer = ""
        header = Table([[logo_cell, title_table, spacer, badge]], colWidths=[0.85 * inch, 8.00 * inch, 2.10 * inch, 2.45 * inch])
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LINEBELOW", (0, 0), (-1, 0), 2.0, RANGERS_BLUE),
        ]))
        return header

    def build_footer():
        note = "Note: Values shown in Dominican Pesos (DOP). Numbers in parentheses indicate the number of times each incentive was achieved."
        ft = Table([[Paragraph(note, note_style)]], colWidths=[13.60 * inch])
        ft.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return ft

    story = []
    pages = [s for s in ["Position Players", "Pitchers"] if s in sheet_options]
    if not pages:
        pages = sheet_options[:2]

    for page_idx, sheet in enumerate(pages):
        df, category_cols, money_cols, weight_map = process_sheet(excel_source, sheet)
        section_label = "POSITION PLAYERS" if sheet == "Position Players" else "PITCHERS"
        story.append(build_header(section_label))
        story.append(Spacer(1, 0.045 * inch))

        groups = get_group_values(sheet, category_cols)
        spans = group_spans(groups)
        # First row: merged section labels. Second row: actual column headers attached to data.
        group_row = [pcell("", group_style), pcell("", group_style)] + [pcell(g if i == next((s for s, e, v in spans if s <= i <= e), i) else "", group_style) for i, g in enumerate(groups)] + [pcell("", group_style)]
        headers = ["PLAYER", "TEAM"] + [str(c).upper() for c in category_cols] + ["TOTAL RD$"]
        header_row = [pcell(h, header_style) for h in headers]
        matrix = [group_row, header_row]
        first_data_row = 2

        full = df.sort_values("Rank").copy()
        totals = pd.to_numeric(full["Total"], errors="coerce").fillna(0)
        min_total = float(totals.min()) if not totals.empty else 0
        max_total = float(totals.max()) if not totals.empty else 0

        for _, r in full.iterrows():
            row = [
                pcell(r["Player"], player_style),
                pcell(team_pdf_label(r.get("Team", "")), team_style),
            ]
            for c in category_cols:
                w = weight_map.get(c, 0)
                qty = float(r[c]) if pd.notna(r[c]) else 0
                val = qty * (0 if pd.isna(w) else w)
                row.append(rich_cell(money_qty_markup(val, qty), value_style))
            row.append(rich_cell(f'<b>{pdf_number_fmt(r["Total"])}</b>', total_style))
            matrix.append(row)

        fixed = 1.78 * inch + 0.48 * inch + 0.76 * inch
        remaining = page_width - fixed
        raw_stat_widths = []
        for col in category_cols:
            text_len = max(len(str(col)), 5)
            raw_stat_widths.append(min(0.78 * inch, max(0.29 * inch, (0.16 + text_len * 0.027) * inch)))
        raw_total = sum(raw_stat_widths) if raw_stat_widths else 1
        scale = remaining / raw_total
        stat_widths = [max(0.29 * inch, w * scale) for w in raw_stat_widths]
        col_widths = [1.78 * inch, 0.48 * inch] + stat_widths + [0.76 * inch]

        row_heights = [0.16 * inch, 0.23 * inch] + [None] * len(full)
        item_table = Table(matrix, colWidths=col_widths, rowHeights=row_heights, repeatRows=2)
        ts = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("TOPPADDING", (0, 0), (-1, -1), 1.05),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.05),
            ("LEFTPADDING", (0, 0), (-1, -1), 0.65),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0.65),
            ("BACKGROUND", (0, 0), (-1, 1), RANGERS_GRAY),
            ("TEXTCOLOR", (0, 0), (-1, 1), colors.white),
            ("LINEABOVE", (0, 0), (-1, 0), 2.0, RANGERS_BLUE),
            ("LINEBELOW", (0, -1), (-1, -1), 0.22, RANGERS_BLUE),
            ("LINEBELOW", (0, 1), (-1, 1), 0.45, colors.HexColor("#A8A8A8")),
            ("ROWBACKGROUNDS", (0, first_data_row), (-1, -1), [colors.white, LIGHT_GRAY]),
        ]

        # Merge and center section labels such as HITTING, DEFENSE, DAILY, WEEKLY, TEAM.
        for start, end, label in spans:
            if label and end >= start:
                ts.append(("SPAN", (2 + start, 0), (2 + end, 0)))
                if start > 0:
                    ts.append(("LINEBEFORE", (2 + start, 0), (2 + start, -1), 0.6, colors.HexColor("#A8A8A8")))
        # Separate total from item sections.
        ts.append(("LINEBEFORE", (-1, 0), (-1, -1), 0.6, colors.HexColor("#A8A8A8")))

        # Team color blocks. Keep TEAM text smaller than player names and values.
        for ridx, (_, r) in enumerate(full.iterrows(), start=first_data_row):
            team = team_pdf_label(r.get("Team", ""))
            if team == "RED":
                ts.append(("BACKGROUND", (1, ridx), (1, ridx), RANGERS_RED))
            elif team == "BLUE":
                ts.append(("BACKGROUND", (1, ridx), (1, ridx), RANGERS_BLUE))
            ts.append(("TEXTCOLOR", (1, ridx), (1, ridx), colors.white))
            ts.append(("FONTNAME", (1, ridx), (1, ridx), "Helvetica-Bold"))
            ts.append(("BACKGROUND", (-1, ridx), (-1, ridx), total_gradient_color(r["Total"], min_total, max_total)))

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
