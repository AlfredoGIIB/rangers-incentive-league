from pathlib import Path

import altair as alt
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
    .main-title {
        font-size: 42px;
        font-weight: 900;
        margin-bottom: -8px;
        color: #0f172a;
    }
    .subtitle {
        font-size: 17px;
        color: #64748b;
        margin-bottom: 20px;
    }
    .league-card {
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(0,0,0,.07);
        min-height: 145px;
    }
    .rank-number {
        font-size: 34px;
        font-weight: 900;
    }
    .player-name {
        font-size: 22px;
        font-weight: 900;
        color: #111827;
    }
    .metric-big {
        font-size: 32px;
        font-weight: 900;
        color: #0f172a;
    }
    .small-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: .06em;
        font-weight: 700;
    }
    .positive-money {
        color: #15803d;
        font-weight: 900;
    }
    .negative-money {
        color: #b91c1c;
        font-weight: 900;
    }
    .section-note {
        color: #64748b;
        font-size: 14px;
        margin-top: -8px;
        margin-bottom: 12px;
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


def detect_header_and_weight_rows(raw):
    """
    Finds the row where first column is Players or Pitchers.
    The row above it is assumed to contain incentive weights.
    """
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


def red_loss_chart(data, limit=8):
    chart_data = data.head(limit).copy()
    chart_data["Loss"] = chart_data["Earnings"].abs()
    chart_data = chart_data.sort_values("Loss", ascending=True)

    chart = (
        alt.Chart(chart_data)
        .mark_bar(color="#dc2626")
        .encode(
            x=alt.X("Loss:Q", title="Earnings lost", axis=alt.Axis(format=",.0f")),
            y=alt.Y("Stats:N", sort=None, title="Stats"),
            tooltip=[
                alt.Tooltip("Stats:N", title="Stats"),
                alt.Tooltip("Earnings:Q", title="Earnings", format=",.0f"),
                alt.Tooltip("Qty:Q", title="Qty", format=",.0f"),
            ],
        )
        .properties(height=max(260, len(chart_data) * 34))
    )
    st.altair_chart(chart, use_container_width=True)


def set_player_and_open(player):
    st.session_state["selected_player"] = player
    st.session_state["view"] = "👤 Player Report"
    st.session_state["view_radio"] = "👤 Player Report"


def show_top_cards(df, category_cols, weight_map):
    top3 = df.sort_values("Total", ascending=False).head(3).reset_index(drop=True)
    medals = ["🥇", "🥈", "🥉"]
    cols = st.columns(3)
    for i, col in enumerate(cols):
        if i < len(top3):
            r = top3.iloc[i]
            top_stat, top_earnings = top_positive_stat(r, category_cols, weight_map)
            col.markdown(
                f"""
                <div class="league-card">
                    <div class="rank-number">{medals[i]} #{i+1}</div>
                    <div class="player-name">{r['Player']}</div>
                    <div class="small-label">Team {r.get('Team', '')}</div>
                    <div style="height:10px"></div>
                    <div class="metric-big">{money_fmt(r['Total'])}</div>
                    <div style="height:8px"></div>
                    <div class="small-label">Biggest Contributor</div>
                    <div class="positive-money">{top_stat} — {money_fmt(top_earnings)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col.button(
                f"Open {r['Player']}",
                key=f"top_open_{i}_{r['Player']}",
                on_click=set_player_and_open,
                args=(r["Player"],),
                use_container_width=True,
            )


def show_top_money_sources(df, category_cols, weight_map):
    top_players = df.sort_values("Total", ascending=False).head(5)
    for _, player in top_players.iterrows():
        bd = player_breakdown(player, category_cols, weight_map)
        positive = bd[bd["Earnings"] > 0].sort_values("Earnings", ascending=False).head(5)
        if positive.empty:
            continue

        st.markdown(f"### #{int(player['Rank'])} {player['Player']} — {money_fmt(player['Total'])}")
        chart_df = positive.set_index("Stats")[["Earnings"]]
        st.bar_chart(chart_df)

        display = positive.copy()
        display["Earnings"] = display["Earnings"].apply(money_fmt)
        display["Weight"] = display["Weight"].apply(lambda x: money_fmt(x).replace("RD$", ""))
        display["Qty"] = display["Qty"].map(lambda x: f"{x:,.0f}")
        st.dataframe(display, use_container_width=True, hide_index=True)


def show_full_standings(df, category_cols, weight_map):
    standings = df[["Rank", "Player", "Team", "Total"]].sort_values("Rank").copy()
    contributors = df.apply(lambda r: top_positive_stat(r, category_cols, weight_map), axis=1)
    contributor_map = {
        player: f"{stat} ({money_fmt(value)})" if stat != "—" else "—"
        for player, (stat, value) in zip(df["Player"], contributors)
    }
    standings["Biggest Contributor"] = standings["Player"].map(contributor_map)

    styled = (
        standings.style
        .background_gradient(subset=["Total"], cmap="RdYlGn")
        .format({"Total": money_fmt})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("### Open Individual Report")
    st.caption("Selecciona un jugador para abrir su reporte individual.")
    players = df.sort_values("Rank")["Player"].tolist()
    cols = st.columns(3)
    for idx, player in enumerate(players):
        with cols[idx % 3]:
            total = df.loc[df["Player"] == player, "Total"].iloc[0]
            rank = df.loc[df["Player"] == player, "Rank"].iloc[0]
            st.button(
                f"#{int(rank)} {player} — {money_fmt(total)}",
                key=f"standings_open_{idx}_{player}",
                on_click=set_player_and_open,
                args=(player,),
                use_container_width=True,
            )


def show_category_leaders(df, category_cols, weight_map):
    positive_categories = [c for c in category_cols if weight_map.get(c, 0) and weight_map.get(c, 0) > 0]
    if not positive_categories:
        return

    st.subheader("📊 League Leaders by Stats")
    st.markdown('<div class="section-note">Top performers by positive incentive stats.</div>', unsafe_allow_html=True)

    selected_categories = positive_categories[:6]
    cols = st.columns(3)
    for idx, cat in enumerate(selected_categories):
        with cols[idx % 3]:
            leaders = df[["Player", cat]].copy()
            leaders[cat] = pd.to_numeric(leaders[cat], errors="coerce").fillna(0)
            leaders = leaders.sort_values(cat, ascending=False).head(5)
            st.markdown(f"#### {cat}")
            st.dataframe(leaders, use_container_width=True, hide_index=True)


def show_general_page(df, category_cols, money_cols, weight_map, group_name):
    st.markdown('<div class="main-title">🏆 Rangers Incentive League</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="subtitle">Fantasy-style standings report — {group_name}</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("League Bank", money_fmt(df["Total"].sum()))
    c2.metric("Average", money_fmt(df["Total"].mean()))
    c3.metric("Leader", money_fmt(df["Total"].max()))
    c4.metric("Players", f"{len(df)}")

    st.divider()
    st.subheader("🔥 Top Performers")
    show_top_cards(df, category_cols, weight_map)

    st.divider()
    st.subheader("💸 Where Top Performers Made Their Money")
    st.markdown('<div class="section-note">Igual que Fantasy Football: no solo el total, sino de dónde vienen los puntos/dinero.</div>', unsafe_allow_html=True)
    show_top_money_sources(df, category_cols, weight_map)

    st.divider()
    show_category_leaders(df, category_cols, weight_map)

    st.divider()
    st.subheader("📋 Full Standings")
    show_full_standings(df, category_cols, weight_map)


def show_player_page(df, category_cols, weight_map, selected_player, group_name):
    player_rows = df[df["Player"] == selected_player]
    if player_rows.empty:
        st.error("No encontré ese jugador.")
        return

    row = player_rows.iloc[0]
    bd = player_breakdown(row, category_cols, weight_map)
    positive = bd[bd["Earnings"] > 0].sort_values("Earnings", ascending=False)
    negative = bd[bd["Earnings"] < 0].sort_values("Earnings")

    st.markdown(f'<div class="main-title">👤 {selected_player}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Individual report — {group_name}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Earnings", money_fmt(row["Total"]))
    c2.metric("League Rank", f"#{int(row['Rank'])}")
    c3.metric("Team", row.get("Team", ""))
    c4.metric("Group", group_name)

    if st.button("← Back to Full Standings", use_container_width=False):
        st.session_state["view"] = "🏠 League Home"
        st.session_state["view_radio"] = "🏠 League Home"
        st.rerun()

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("📈 Money Earned")
        st.caption("Stats that have added the most to his earnings.")
        if positive.empty:
            st.info("No positive earnings registered yet.")
        else:
            st.bar_chart(positive.head(8).set_index("Stats")[["Earnings"]])
            display = positive.copy()
            display["Earnings"] = display["Earnings"].apply(money_fmt)
            display["Weight"] = display["Weight"].apply(lambda x: money_fmt(x).replace("RD$", ""))
            display["Qty"] = display["Qty"].map(lambda x: f"{x:,.0f}")
            st.dataframe(display, use_container_width=True, hide_index=True)

    with right:
        st.subheader("📉 Money Lost")
        st.caption("Stats that have cost him money.")
        if negative.empty:
            st.success("No money lost in negative stats.")
        else:
            red_loss_chart(negative, limit=8)
            display = negative.copy()
            display["Earnings"] = display["Earnings"].apply(money_fmt)
            display["Weight"] = display["Weight"].apply(lambda x: money_fmt(x).replace("RD$", ""))
            display["Qty"] = display["Qty"].map(lambda x: f"{x:,.0f}")
            st.dataframe(display, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🎯 Fantasy Summary")
    c1, c2 = st.columns(2)
    if not positive.empty:
        top_strength = positive.iloc[0]
        c1.success(f"Main Money Source: {top_strength['Stats']} — {money_fmt(top_strength['Earnings'])}")
    else:
        c1.info("No main money source yet.")

    if not negative.empty:
        biggest_leak = negative.iloc[0]
        c2.error(f"Biggest Cost: {biggest_leak['Stats']} — {money_fmt(biggest_leak['Earnings'])}")
    else:
        c2.success("No negative category cost yet.")

    st.subheader("🧾 Full Money Breakdown")
    full = bd.copy()
    full["Earnings"] = full["Earnings"].apply(money_fmt)
    full["Weight"] = full["Weight"].apply(lambda x: money_fmt(x).replace("RD$", ""))
    full["Qty"] = full["Qty"].map(lambda x: f"{x:,.0f}")
    st.dataframe(full, use_container_width=True, hide_index=True)


# -----------------------------
# App
# -----------------------------
DEFAULT_EXCEL_PATH = Path(__file__).with_name("Incentives System - DR TEX 2026.xlsx")

st.sidebar.title("🏆 Rangers Incentive League")
uploaded_file = st.sidebar.file_uploader("Upload a different incentives Excel", type=["xlsx"])

if "view" not in st.session_state:
    st.session_state["view"] = "🏠 League Home"

if uploaded_file is not None:
    excel_source = uploaded_file
    st.sidebar.success("Using uploaded Excel")
elif DEFAULT_EXCEL_PATH.exists():
    excel_source = DEFAULT_EXCEL_PATH
    st.sidebar.success("Using default Excel")
else:
    st.markdown('<div class="main-title">🏆 Rangers Incentive League</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Upload the incentives Excel to generate the Fantasy-style dashboard.</div>',
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

selected_sheet = st.sidebar.radio("Group", sheet_options, index=0)

try:
    df, category_cols, money_cols, weight_map = process_sheet(excel_source, selected_sheet)
except Exception as e:
    st.error(f"Error procesando la hoja {selected_sheet}: {e}")
    st.stop()

players = df.sort_values("Total", ascending=False)["Player"].tolist()

view = st.sidebar.radio(
    "View",
    ["🏠 League Home", "👤 Player Report"],
    index=0 if st.session_state.get("view") == "🏠 League Home" else 1,
    key="view_radio",
)
st.session_state["view"] = view

if "selected_player" not in st.session_state or st.session_state["selected_player"] not in players:
    st.session_state["selected_player"] = players[0] if players else None

if st.session_state["view"] == "👤 Player Report":
    selected_player = st.sidebar.selectbox(
        "Select Player",
        players,
        index=players.index(st.session_state["selected_player"]) if st.session_state["selected_player"] in players else 0,
    )
    st.session_state["selected_player"] = selected_player
    show_player_page(df, category_cols, weight_map, selected_player, selected_sheet)
else:
    show_general_page(df, category_cols, money_cols, weight_map, selected_sheet)
