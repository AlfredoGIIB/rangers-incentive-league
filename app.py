from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Rangers Incentive League",
    page_icon="🏆",
    layout="wide",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
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
    .heatmap-table a:hover {
        text-decoration: underline;
        color: #BA0C2F;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def money_fmt(value):
    try:
        value = float(value)
    except Exception:
        value = 0
    sign = "-" if value < 0 else ""
    return f"{sign}RD${abs(value):,.0f}"


def show_program_banner(group_name=None):
    group_html = f" — {html_escape(group_name)}" if group_name else ""
    st.markdown(
        f"""
        <div class="rangers-banner">
            <div class="banner-kicker">Texas Rangers</div>
            <div class="banner-title">DSL 2026 Incentive Program</div>
            <div class="banner-subtitle">Rangers Incentive League{group_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def detect_header_and_weight_rows(raw):
    first_col = raw.iloc[:, 0].astype(str).str.strip().str.lower()
    header_candidates = raw.index[first_col.isin(["players", "pitchers"])].tolist()
    if not header_candidates:
        raise ValueError("No pude encontrar una fila que empiece con Players o Pitchers.")
    header_row = header_candidates[0]
    weight_row = header_row - 1
    return header_row, weight_row


def process_sheet(excel_file, sheet_name):
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
        st.info("No data available yet.")
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
        html.append(f"<th>{html_escape(c)}</th>")
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


def clear_query_and_go_home():
    st.query_params.clear()
    st.session_state["view"] = "🏠 League Home"


def show_top_cards(df, category_cols, weight_map, group_name):
    top3 = df.sort_values("Total", ascending=False).head(3).reset_index(drop=True)
    medals = ["🥇", "🥈", "🥉"]
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
                    <div class="rank-number">{medals[i]} #{i+1}</div>
                    <div class="player-name"><a href="{url}" target="_self" style="color:#002D72;text-decoration:none;">{name}</a></div>
                    <div class="small-label">Team {html_escape(r.get('Team', ''))}</div>
                    <div style="height:10px"></div>
                    <div class="metric-big">{money_fmt(r['Total'])}</div>
                    <div style="height:8px"></div>
                    <div class="small-label">Biggest Contributor</div>
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

    st.subheader("📊 Stats Leaders")
    st.markdown('<div class="section-note">Top 3 jugadores por cada stat positivo del programa de incentivos DSL 2026.</div>', unsafe_allow_html=True)

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


def show_general_page(df, category_cols, money_cols, weight_map, group_name):
    show_program_banner(group_name)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Program Bank", money_fmt(df["Total"].sum()))
    c2.metric("Average", money_fmt(df["Total"].mean()))
    c3.metric("Leader", money_fmt(df["Total"].max()))
    c4.metric("Players", f"{len(df)}")

    st.divider()
    st.subheader("🔥 Top Performers")
    show_top_cards(df, category_cols, weight_map, group_name)

    st.divider()
    st.subheader("💸 Primary Earnings Sources")
    st.markdown('<div class="section-note">Top 3 jugadores y los stats que más han aportado a sus ganancias acumuladas dentro del programa.</div>', unsafe_allow_html=True)
    show_top_money_sources(df, category_cols, weight_map, group_name)

    st.divider()
    show_category_leaders(df, category_cols, weight_map, group_name)

    st.divider()
    st.subheader("📋 Full Standings")
    st.markdown('<div class="section-note">Haz click en cualquier nombre para abrir el reporte individual del jugador.</div>', unsafe_allow_html=True)
    show_full_standings(df, category_cols, weight_map, group_name)
    st.markdown('<div style="color:#857874;font-size:13px;margin-top:20px;text-align:center;">Texas Rangers Baseball Club · DSL 2026 Incentive Program</div>', unsafe_allow_html=True)


def show_player_page(df, category_cols, weight_map, selected_player, group_name):
    player_rows = df[df["Player"] == selected_player]
    if player_rows.empty:
        st.error("No encontré ese jugador.")
        return

    row = player_rows.iloc[0]
    bd = player_breakdown(row, category_cols, weight_map)
    positive = bd[bd["Earnings"] > 0].sort_values("Earnings", ascending=False)
    negative = bd[bd["Earnings"] < 0].sort_values("Earnings")

    st.markdown(f'<div class="main-title">👤 {html_escape(selected_player)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Individual report — {group_name}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Earnings", money_fmt(row["Total"]))
    c2.metric("Program Rank", f"#{int(row['Rank'])}")
    c3.metric("Team", row.get("Team", ""))
    c4.metric("Group", group_name)

    st.markdown(f"[← Back to Full Standings](?group={quote(str(group_name))})")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("📈 Earnings Sources")
        st.caption("Stats que más han aportado a sus ganancias dentro del programa de incentivos DSL 2026.")
        if positive.empty:
            st.info("No positive earnings registered yet.")
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
        st.subheader("📉 Earnings Deductions")
        st.caption("Stats que han generado pérdidas dentro del programa de incentivos DSL 2026.")
        if negative.empty:
            st.success("No earnings deductions registered.")
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
    st.subheader("🎯 Player Incentive Summary")
    c1, c2 = st.columns(2)
    if not positive.empty:
        top_strength = positive.iloc[0]
        c1.success(f"Primary Earnings Source: {top_strength['Stats']} — {money_fmt(top_strength['Earnings'])}")
    else:
        c1.info("No main money source yet.")

    if not negative.empty:
        biggest_leak = negative.iloc[0]
        c2.error(f"Largest Deduction: {biggest_leak['Stats']} — {money_fmt(biggest_leak['Earnings'])}")
    else:
        c2.success("No earnings deductions registered.")

    st.subheader("🧾 Full Earnings Breakdown")
    display_heatmap_table(
        bd,
        columns=["Stats", "Qty", "Weight", "Earnings"],
        sort_by="Earnings",
        ascending=False,
        cmap="RdYlGn",
        group_name=group_name,
    )
    st.markdown('<div style="color:#857874;font-size:13px;margin-top:20px;text-align:center;">Texas Rangers Baseball Club · DSL 2026 Incentive Program</div>', unsafe_allow_html=True)


# -----------------------------
# App
# -----------------------------
DEFAULT_EXCEL_PATH = Path(__file__).with_name("Incentives System - DR TEX 2026.xlsx")

st.sidebar.title("🏆 Rangers Incentive League")
uploaded_file = st.sidebar.file_uploader("Upload a different incentives Excel", type=["xlsx"])

if uploaded_file is not None:
    excel_source = uploaded_file
    st.sidebar.success("Using uploaded Excel")
elif DEFAULT_EXCEL_PATH.exists():
    excel_source = DEFAULT_EXCEL_PATH
    st.sidebar.success("Using default Excel")
else:
    show_program_banner()
    st.markdown(
        '<div class="subtitle">Upload the incentives Excel to generate the DSL 2026 Texas Rangers incentive report.</div>',
        unsafe_allow_html=True,
    )
    st.info("No default Excel was found. Upload an Excel with the sheets 'Position Players' and 'Pitchers'.")
    st.stop()

try:
    sheet_names = pd.ExcelFile(excel_source).sheet_names
except Exception as e:
    st.error(f"No pude leer el archivo: {e}")
    st.stop()

preferred = [s for s in ["Position Players", "Pitchers"] if s in sheet_names]
other = [s for s in sheet_names if s not in preferred]
sheet_options = preferred + other

query_group = st.query_params.get("group")
query_player = st.query_params.get("player")
query_view = st.query_params.get("view")

sheet_index = 0
if query_group in sheet_options:
    sheet_index = sheet_options.index(query_group)

selected_sheet = st.sidebar.radio("Group", sheet_options, index=sheet_index)

try:
    df, category_cols, money_cols, weight_map = process_sheet(excel_source, selected_sheet)
except Exception as e:
    st.error(f"Error procesando la hoja {selected_sheet}: {e}")
    st.stop()

players = df.sort_values("Total", ascending=False)["Player"].tolist()

if query_view == "player" and query_player in players:
    show_player_page(df, category_cols, weight_map, query_player, selected_sheet)
else:
    show_general_page(df, category_cols, money_cols, weight_map, selected_sheet)
