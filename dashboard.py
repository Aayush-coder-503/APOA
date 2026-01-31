import streamlit as st
import json
import pandas as pd
import time
import plotly.express as px

st.set_page_config(page_title="AI Payment Ops", layout="wide")

REFRESH_SECONDS = 2

st.title("Live Autonomous Payment Intelligence")

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

metrics = load_json("live_metrics.json")
decisions = load_json("live_decisions.json")
memory = load_json("memory.json")

if not metrics:
    st.warning("Waiting for live payment data...")
    time.sleep(REFRESH_SECONDS)
    st.rerun()

rows = []
for route, v in metrics.items():
    rows.append({
        "Route": route,
        "Success %": round(v["success_rate"] * 100, 1),
        "Latency (ms)": v["avg_latency"],
        "Errors": sum(v["errors"].values())
    })

df = pd.DataFrame(rows)

avg_success = round(df["Success %"].mean(), 2)
avg_latency = round(df["Latency (ms)"].mean(), 1)

col1, col2, col3 = st.columns(3)
col1.metric("Network Success", f"{avg_success}%")
col2.metric("Avg Latency", f"{avg_latency} ms")
col3.metric("Learned Routes", len(memory))

st.divider()


left, right = st.columns(2)

with left:
    st.subheader("Route Risk Heatmap")
    fig = px.bar(
        df,
        x="Route",
        y="Errors",
        color="Errors",
        title="Where Payments Are Failing",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Performance Map")
    fig2 = px.scatter(
        df,
        x="Latency (ms)",
        y="Success %",
        size="Errors",
        color="Route",
        title="High Latency = Low Success"
    )
    st.plotly_chart(fig2, width="stretch")

st.divider()

st.subheader("AI Live Decisions")

if decisions:
    dec_df = pd.DataFrame(decisions)
    dec_df["Route"] = dec_df["bank"] + "-" + dec_df["card"]
    dec_df = dec_df[["Route", "impact_percent", "probability", "suggested_action"]]

    fig3 = px.bar(
        dec_df,
        x="Route",
        y="impact_percent",
        color="suggested_action",
        title="AI Interventions"
    )
    st.plotly_chart(fig3, width="stretch")
else:
    st.info("AI is not taking action right now.")

st.divider()


st.subheader("AI Memory & Learning")

mem_rows = []
for k, v in memory.items():
    mem_rows.append({
        "Route": k,
        "Confidence": round(v["confidence"], 2),
        "Times Seen": v["times_seen"]
    })

mem_df = pd.DataFrame(mem_rows)

if not mem_df.empty:
    fig4 = px.scatter(
        mem_df,
        x="Times Seen",
        y="Confidence",
        size="Confidence",
        color="Route",
        title="AI Trust vs Experience"
    )
    st.plotly_chart(fig4, width="stretch")
else:
    st.write("Memory warming up…")

st.caption("Autonomous system refreshing every 2 seconds")

time.sleep(REFRESH_SECONDS)
st.rerun()
