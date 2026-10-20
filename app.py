"""
Option Desk: binomial pricing of American and European options (Streamlit, dark theme).

Folder layout:
    MTA7108-American-Option-Pricing/
        app.py                 this file (the dashboard)
        launch.py              desktop window or web version
        requirements.txt
        .streamlit/config.toml dark theme
        optionlib/             library used by the app
            binomial.py          the tree, the early exercise test, convergence
            blackscholes.py      the European formula, used as a check
            pdf_report.py        builds the valuation note PDF
            records.py           valuation numbers, the log and saved PDFs
            presets.py           the worked example from the course notes
            ui.py                dashboard styling, cards and charts
        data/                  created on first run

Run from inside the folder:
    python -m pip install -r requirements.txt
    python launch.py
"""

import os
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from optionlib import (CONVENTIONS, KINDS, STYLES, Records, blackscholes, build_pdf,
                       convergence, exercise_boundary, greeks, limit_price, node_table,
                       parameters, payoff, presets, price, ui)

DESKTOP = os.environ.get("OPTIONDESK_MODE") == "desktop"
records = Records(Path(__file__).parent / "data", prefix="OP")

I_OPT = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg>'
I_TREE = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="5" cy="12" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="19" cy="18" r="2"/><path d="M7 11l10-4M7 13l10 4"/></svg>'
I_TABLE = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M9 4v16"/></svg>'
I_CHART = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 20h18"/><path d="M6 16l4-5 4 3 5-7"/></svg>'
I_CHECK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>'
I_DOC = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></svg>'
I_BOUND = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 18h18"/><path d="M3 14h5v4H3zM8 10h5v8H8zM13 6h5v12h-5z"/></svg>'

st.set_page_config(page_title="Option Desk", page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject_css()

log = records.load_log()

# ================================================================ sidebar
with st.sidebar:
    ui.brand("Option Desk", "Binomial pricing of options")

    ui.side_label("The option")
    underlying = st.text_input("Underlying", "Lecture example")
    a, b = st.columns(2)
    kind = a.selectbox("Type", KINDS)
    style = b.selectbox("Style", STYLES)
    a, b = st.columns(2)
    S0 = a.number_input("Stock price S(0)", min_value=0.0001, value=9.0, step=0.5,
                        format="%.4f")
    K = b.number_input("Strike K", min_value=0.0001, value=10.0, step=0.5, format="%.4f")
    a, b = st.columns(2)
    T = a.number_input("Years to expiry T", min_value=0.0001, value=0.25, step=0.25,
                       format="%.4f")
    n = b.number_input("Steps n", min_value=1, max_value=400, value=5, step=1)
    a, b = st.columns(2)
    sigma_pct = a.number_input("Volatility σ (%)", min_value=0.01, value=30.0, step=1.0,
                               format="%.2f")
    r_pct = b.number_input("Interest rate r (%)", min_value=-10.0, value=6.0, step=0.5,
                           format="%.2f")

    ui.side_label("Conventions")
    convention_label = st.selectbox("Risk neutral probability", list(CONVENTIONS))
    currency = st.text_input("Currency symbol", "$")
    prepared_by = st.text_input("Prepared by (PDF header)", "")

    sigma, r = sigma_pct / 100.0, r_pct / 100.0
    convention = CONVENTIONS[convention_label]

    ui.side_label("Record")
    ui.side_stats([("Valuations saved", f"{len(log):,}"),
                   ("Next number", records.peek_serial())])

# ================================================================ header
ui.page_header("Option Desk",
               f"Binomial pricing of American and European options · {date.today():%d %b %Y}",
               "Next valuation", records.peek_serial())

try:
    value, par, nodes = price(S0, K, T, sigma, r, int(n), kind, style, convention)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

df_nodes = node_table(nodes)
euro_tree = price(S0, K, T, sigma, r, int(n), kind, "European", convention)[0]
amer_tree = price(S0, K, T, sigma, r, int(n), kind, "American", convention)[0]
bs_price = blackscholes.european(S0, K, T, sigma, r, kind)
premium = amer_tree - euro_tree
now = payoff(S0, K, kind)
settled = limit_price(S0, K, T, sigma, r, kind, style, convention,
                      n=400 if int(n) <= 400 else int(n))

tab_price, tab_tree, tab_conv, tab_bound, tab_check, tab_log = st.tabs(
    ["Price", "The tree", "Convergence", "Early exercise", "Lecture example", "Valuations"])

# ================================================================ price
with tab_price:
    k1, k2, k3, k4 = st.columns(4, gap="small")
    with k1:
        ui.kpi(f"{style} {kind.lower()}", f"{value:,.4f}", currency,
               f"{int(n)} steps · σ {sigma_pct:g}% · r {r_pct:g}%", ui.WAIT)
    with k2:
        ui.kpi("Exercising today", f"{now:,.4f}", currency,
               ("In the money" if now > 0 else "Out of the money"), ui.EXERCISE)
    with k3:
        ui.kpi("Early exercise premium", f"{premium:,.4f}", currency,
               "American less European, same tree")
    with k4:
        ui.kpi("Black and Scholes", f"{bs_price:,.4f}", currency,
               f"European {kind.lower()} · tree gives {euro_tree:,.4f}")

    left, right = st.columns([3, 2], gap="medium")

    with left, st.container(border=True):
        ui.card_title(I_OPT, "What the price is made of",
                      "The tree values the option, the formula checks the European case")
        g = greeks(S0, K, T, sigma, r, max(int(n), 2), kind, style, convention)
        rows = [
            ("Price on the tree", f"{value:,.4f}"),
            ("Value of exercising today", f"{now:,.4f}"),
            ("Value of waiting", f"{df_nodes.iloc[-1]['Wait']:,.4f}"
                if pd.notna(df_nodes.iloc[-1]["Wait"]) else "-"),
            ("Price as the tree is refined", f"{settled:,.4f}"),
            ("Delta", f"{g['delta']:,.4f}"),
            ("Gamma", f"{g['gamma']:,.4f}"),
            ("Theta (per year)", f"{g['theta']:,.4f}"),
        ]
        st.dataframe(pd.DataFrame(rows, columns=["Quantity", "Value"]),
                     width="stretch", hide_index=True)

    with right, st.container(border=True):
        ui.card_title(I_TABLE, "The tree parameters", "One step of length dt = T / n")
        p_rows = [
            ("dt", f"{par['dt']:.6f}"),
            ("u = exp(σ√dt)", f"{par['u']:.4f}"),
            ("d = 1/u", f"{par['d']:.4f}"),
            ("β = exp(−r dt)", f"{par['beta']:.4f}"),
            ("p", f"{par['p']:.4f}"),
            ("β p", f"{par['beta_p']:.4f}"),
            ("β (1 − p)", f"{par['beta_q']:.4f}"),
        ]
        st.dataframe(pd.DataFrame(p_rows, columns=["Quantity", "Value"]),
                     width="stretch", hide_index=True)

    with st.container(border=True):
        ui.card_title(I_CHART, "Value today against the stock price",
                      "The dashed line is the payoff from exercising immediately")
        spots = [S0 * (0.4 + 0.016 * j) for j in range(0, 101)]
        curve = []
        for s in spots:
            try:
                v = price(s, K, T, sigma, r, min(int(n), 120), kind, style, convention)[0]
            except ValueError:
                continue
            curve.append({"Spot": s, "Value": v, "Exercise now": payoff(s, K, kind)})
        st.altair_chart(ui.value_chart(pd.DataFrame(curve), K), width="stretch")

    with st.container(border=True):
        ui.card_title(I_DOC, "Valuation note",
                      "Saves the valuation and produces a PDF of every node")
        note = st.text_input("Note (optional)", key="note")
        c1, c2 = st.columns([1, 3])
        if c1.button("Save and build the PDF", type="primary"):
            serial = records.take_serial()
            inputs = {
                "Underlying": underlying or "-",
                "Option": f"{style} {kind.lower()}",
                "Stock price S(0)": f"{S0:,.4f}",
                "Strike K": f"{K:,.4f}",
                "Years to expiry T": f"{T:,.4f}",
                "Volatility σ": f"{sigma_pct:.2f}%",
                "Interest rate r": f"{r_pct:.2f}%",
                "Steps n": str(int(n)),
                "Risk neutral probability": convention_label,
                "Valued on": date.today().strftime("%d %b %Y"),
            }
            results = {
                "Price": f"{currency}{value:,.4f}",
                "Exercising today": f"{currency}{now:,.4f}",
                "European on the same tree": f"{currency}{euro_tree:,.4f}",
                "Early exercise premium": f"{currency}{premium:,.4f}",
                "Black and Scholes (European)": f"{currency}{bs_price:,.4f}",
                "Price as the tree is refined": f"{currency}{settled:,.4f}",
            }
            pdf = build_pdf(serial, inputs, results, par, nodes,
                            prepared_by=prepared_by, currency=currency)
            path = records.save_pdf(f"{serial}.pdf", pdf)
            records.add({"Valuation": serial, "Prepared": datetime.now().strftime("%Y-%m-%d %H:%M"),
                         "Underlying": underlying, "Kind": kind, "Style": style,
                         "Spot": S0, "Strike": K, "Years": T, "Volatility": sigma,
                         "Rate": r, "Steps": int(n), "Price": value,
                         "European": euro_tree, "Premium": premium, "Note": note})
            st.session_state["last_pdf"] = (serial, pdf, str(path))
            st.success(f"Saved as {serial}.")

        if "last_pdf" in st.session_state:
            serial, pdf, path = st.session_state["last_pdf"]
            d1, d2 = st.columns([1, 3])
            d1.download_button("Download the note", data=pdf, file_name=f"{serial}.pdf",
                               mime="application/pdf")
            if DESKTOP and hasattr(os, "startfile"):
                if d2.button("Open the PDF"):
                    os.startfile(path)

# ================================================================ the tree
with tab_tree:
    with st.container(border=True):
        ui.card_title(I_TREE, "The lattice",
                      "Orange where exercising now is worth more than waiting")
        if int(n) > 60:
            st.info("The lattice is drawn for trees of 60 steps or fewer. "
                    "Reduce n in the sidebar to see it.")
        else:
            st.altair_chart(ui.tree_chart(nodes, par["dt"], kind), width="stretch")

    with st.container(border=True):
        ui.card_title(I_TABLE, "Every node, working back from expiry",
                      "k is the step, i the number of up moves, "
                      "so the stock price is S(0) u^i d^(k−i)")
        show = df_nodes.copy()
        show["Wait"] = [("–" if w is None else f"{w:,.4f}") for w in show["Wait"]]
        styler = (show.style
                  .format({"Stock price": "{:,.4f}", "Exercise": "{:,.4f}",
                           "Value": "{:,.4f}"})
                  .map(ui.style_decision, subset=["Decision"]))
        st.dataframe(styler, width="stretch", hide_index=True,
                     height=min(640, 38 + 35 * len(show)))
        st.download_button("Download the nodes (CSV)",
                           data=show.to_csv(index=False).encode(),
                           file_name=f"nodes_{kind.lower()}_{int(n)}_steps.csv",
                           mime="text/csv")

# ================================================================ convergence
with tab_conv:
    with st.container(border=True):
        ui.card_title(I_CHART, "Refining the tree",
                      "Accuracy improves by increasing n, at the cost of more nodes")
        a, b, c = st.columns(3)
        n_from = a.number_input("From", min_value=1, max_value=400, value=1, step=1)
        n_to = b.number_input("To", min_value=2, max_value=400, value=60, step=1)
        step_by = c.number_input("In steps of", min_value=1, max_value=50, value=1, step=1)
        steps = range(int(n_from), int(n_to) + 1, int(step_by))
        conv = convergence(S0, K, T, sigma, r, steps, kind, style, convention)
        if conv.empty:
            st.info("No usable tree in that range.")
        else:
            target = limit_price(S0, K, T, sigma, r, kind, style, convention, n=600)
            k1, k2, k3 = st.columns(3)
            with k1:
                ui.kpi("Settling on", f"{target:,.4f}", currency,
                       "Average of two large trees", ui.EXERCISE)
            with k2:
                ui.kpi(f"Price at n = {int(n)}", f"{value:,.4f}", currency,
                       f"Difference {value - target:+,.4f}", ui.WAIT)
            with k3:
                last = conv.iloc[-1]
                ui.kpi(f"Price at n = {int(last['n'])}", f"{last['Price']:,.4f}", currency,
                       f"Difference {last['Price'] - target:+,.4f}")
            st.altair_chart(ui.convergence_chart(conv, target, "As n grows"),
                            width="stretch")
            out = conv.copy()
            out["Difference from the limit"] = out["Price"] - target
            out["Change"] = [("–" if pd.isna(c) else f"{c:+,.4f}") for c in out["Change"]]
            st.dataframe(out.style.format({"Price": "{:,.4f}",
                                           "Difference from the limit": "{:+,.4f}"}),
                         width="stretch", hide_index=True, height=300)

# ================================================================ early exercise
with tab_bound:
    with st.container(border=True):
        ui.card_title(I_BOUND, "Where exercising early is worth more than waiting",
                      "The boundary is the highest stock price at which a put should be "
                      "exercised at that step")
        if style == "European":
            st.info("A European option cannot be exercised before expiry, so there is no "
                    "boundary. Switch the style to American in the sidebar.")
        else:
            bound = exercise_boundary(nodes, int(n), par["dt"])
            early = df_nodes[(df_nodes["Decision"] == "Exercise") & (df_nodes["k"] < int(n))]
            k1, k2, k3 = st.columns(3)
            with k1:
                ui.kpi("Nodes where exercising early wins", f"{len(early):,}", "",
                       f"of {len(df_nodes):,} nodes in the tree", ui.EXERCISE)
            with k2:
                ui.kpi("Early exercise premium", f"{premium:,.4f}", currency,
                       "What the right to exercise early is worth")
            with k3:
                before_expiry = bound[bound["k"] < int(n)] if len(bound) else bound
                ui.kpi("Earliest step with exercise",
                       f"{int(before_expiry['k'].min())}" if len(before_expiry) else "none",
                       "", "Before expiry")
            if bound.empty:
                st.info("Exercising early never beats waiting for these inputs. For a call "
                        "on a stock that pays no dividends this is always so, which is why "
                        "an American call is worth the same as a European one.")
            else:
                st.altair_chart(ui.boundary_chart(bound, K), width="stretch")
                st.dataframe(bound.style.format({"Time": "{:,.4f}", "Boundary": "{:,.4f}"}),
                             width="stretch", hide_index=True, height=260)

# ================================================================ lecture example
with tab_check:
    L = presets.LECTURE
    with st.container(border=True):
        ui.card_title(I_CHECK, L["name"],
                      "The application recomputes the example and compares it with the notes")
        st.markdown(
            f"**American put**, S(0) = {L['S0']:g}, K = {L['K']:g}, T = {L['T']:g} years, "
            f"σ = {L['sigma']:g}, r = {L['r']:g}, n = {L['n']} steps.")
        checks = pd.DataFrame(presets.check_lecture_example(parameters, price, limit_price))
        agree = checks["Agrees"].all()
        st.dataframe(checks, width="stretch", hide_index=True,
                     column_config={"Agrees": st.column_config.CheckboxColumn("Agrees")})
        if agree:
            st.success("Every figure matches the notes, so the application reproduces the "
                       "worked example exactly.")
        else:
            st.error("At least one figure does not match the notes.")
        if st.button("Load this example into the sidebar"):
            st.info("Set the sidebar to S(0) = 9, K = 10, T = 0.25, σ = 30%, r = 6%, "
                    "n = 5, American put.")

    with st.container(border=True):
        ui.card_title(I_TABLE, "The example node by node",
                      "The same table that appears in the notes")
        lv, lpar, lnodes = price(L["S0"], L["K"], L["T"], L["sigma"], L["r"], L["n"],
                                 L["kind"], L["style"], L["convention"])
        ldf = node_table(lnodes)
        ldf["Wait"] = [("–" if w is None else f"{w:,.4f}") for w in ldf["Wait"]]
        st.dataframe(ldf.style.format({"Stock price": "{:,.4f}", "Exercise": "{:,.4f}",
                                       "Value": "{:,.4f}"})
                     .map(ui.style_decision, subset=["Decision"]),
                     width="stretch", hide_index=True, height=640)
        st.caption(f"Root value {lv:,.4f}, against 1.1375 in the notes. The exact price, "
                   f"as n grows, is 1.126.")

# ================================================================ valuations
with tab_log:
    with st.container(border=True):
        ui.card_title(I_DOC, "Saved valuations", "Every note built on this computer")
        if log.empty:
            st.info("No valuations saved yet. Price an option and save the note.")
        else:
            show = log.copy()
            show["Volatility"] = show["Volatility"] * 100
            show["Rate"] = show["Rate"] * 100
            st.dataframe(show.style.format({"Spot": "{:,.4f}", "Strike": "{:,.4f}",
                                            "Years": "{:,.4f}", "Volatility": "{:,.2f}",
                                            "Rate": "{:,.2f}", "Price": "{:,.4f}",
                                            "European": "{:,.4f}", "Premium": "{:,.4f}"}),
                         width="stretch", hide_index=True, height=420)
            st.download_button("Download the log (CSV)",
                               data=log.to_csv(index=False).encode(),
                               file_name="valuations.csv", mime="text/csv")
