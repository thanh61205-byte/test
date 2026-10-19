import io
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parent
DEFAULT_PRED = "artifacts/modeling/test_predictions_best_model.csv"
st.set_page_config(page_title="City Hotel Lisbon - Cancellation Risk", layout="wide")


# ---------- Helpers ----------
@st.cache_data
def load_csv(rel_path):
    return pd.read_csv(ROOT / rel_path)


@st.cache_resource
def load_model():
    p = ROOT / "artifacts/modeling/final_model.joblib"
    return joblib.load(p) if p.exists() else None


def required_features(model):
    try:
        return list(model.feature_names_in_)
    except AttributeError:
        return list(model.named_steps["preprocess"].feature_names_in_)


@st.cache_data(show_spinner="Scoring uploaded file...")
def score_upload(file_bytes):
    model = load_model()
    new = pd.read_csv(io.BytesIO(file_bytes))
    needed = required_features(model)
    missing = [c for c in needed if c not in new.columns]
    if missing:
        return None, missing
    out = new.copy()
    out["predicted_probability"] = model.predict_proba(new[needed])[:, 1]
    return out, []


@st.cache_data
def make_template(needed):
    p = ROOT / "data/processed/modeling_dataset.csv"
    if not p.exists():
        return None
    keep = lambda c: c in needed or c in ("booking_id", "arrival_date", "is_canceled")
    return pd.read_csv(p, usecols=keep).head(50).to_csv(index=False).encode("utf-8")


# ---------- Sidebar: data source ----------
st.sidebar.header("Data")
up = st.sidebar.file_uploader(
    "Upload your dataset (CSV) to predict. Leave empty to use the default 2017 test predictions.",
    type=["csv"],
)

model = load_model()
if model is not None:
    tpl = make_template(tuple(required_features(model)))
    if tpl is not None:
        st.sidebar.download_button("Download template CSV", tpl, file_name="template_bookings.csv",
                                   mime="text/csv")

default_pred = load_csv(DEFAULT_PRED)
model_thr = float(default_pred["threshold"].iloc[0]) if "threshold" in default_pred.columns else 0.50

book = load_csv("data/processed/bookings_prepared.csv")
has_real_ids = True

if up is None:
    pred = default_pred.copy()
    st.sidebar.caption("Using default: test_predictions_best_model.csv (2017 test).")
else:
    if model is None:
        st.error("Khong thay artifacts/modeling/final_model.joblib. Hay chay notebook 04 truoc.")
        st.stop()
    pred, missing = score_upload(up.getvalue())
    if pred is None:
        st.error(f"File upload dang thieu {len(missing)} cot feature: {missing}")
        st.info("Hay bam 'Download template CSV' o thanh ben trai de lay file mau dung cot.")
        st.stop()
    if "booking_id" not in pred.columns:
        pred.insert(0, "booking_id", np.arange(1, len(pred) + 1))
        has_real_ids = False
    st.sidebar.caption(f"Using uploaded file: {up.name} ({len(pred):,} rows).")

if "booking_id" not in pred.columns:
    st.error("File khong co cot booking_id, khong join duoc.")
    st.stop()

# Join voi bookings_prepared de lay gross_value, kenh, loai phong...
if has_real_ids:
    df = pred.merge(book, on="booking_id", how="left", suffixes=("", "_book"))
else:
    df = pred.copy()
df["p_cancel"] = df["predicted_probability"].astype(float)

value_col = "gross_value" if "gross_value" in df.columns else None
df["revenue_at_risk"] = df["p_cancel"] * df[value_col] if value_col else np.nan

# ---------- Sidebar: thresholds & filters ----------
thr_high = st.sidebar.slider("High-risk threshold (default = model threshold)", 0.05, 0.95,
                             float(np.clip(round(model_thr, 2), 0.05, 0.95)), 0.01)
thr_med = st.sidebar.slider("Medium-risk threshold", 0.05, 0.95, float(min(0.30, thr_high)), 0.05)
df["risk_band"] = np.select(
    [df.p_cancel >= thr_high, df.p_cancel >= thr_med], ["High", "Medium"], default="Low"
)

for col, label in [("market_segment", "Market segment"), ("reserved_room_type", "Room type")]:
    if col in df.columns:
        opts = sorted(df[col].dropna().astype(str).unique())
        sel = st.sidebar.multiselect(label, opts, default=opts)
        df = df[df[col].astype(str).isin(sel)]

st.sidebar.caption("Retrospective prototype. Test 2017 la holdout da duoc kham pha mot phan.")

if df.empty:
    st.warning("Khong co booking nao sau khi loc.")
    st.stop()

# ---------- Header ----------
st.title("City Hotel Lisbon - Booking Cancellation Risk")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Bookings scored", f"{len(df):,}")
c2.metric("High-risk bookings", f"{(df.risk_band == 'High').sum():,}")
c3.metric("Avg predicted cancel rate", f"{df.p_cancel.mean():.1%}")
if value_col:
    c4.metric("Revenue at risk (EUR)", f"{df.revenue_at_risk.sum():,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Booking risk", "Revenue at risk", "Follow-up actions", "Model check"])

# ---------- Tab 1 ----------
with tab1:
    left, right = st.columns(2)
    left.plotly_chart(px.histogram(df, x="p_cancel", nbins=40, title="Distribution of cancel probability"),
                      use_container_width=True)
    band = df.risk_band.value_counts().reindex(["High", "Medium", "Low"]).fillna(0).reset_index()
    band.columns = ["risk_band", "bookings"]
    right.plotly_chart(px.bar(band, x="risk_band", y="bookings", title="Bookings by risk band"),
                       use_container_width=True)
    show = [c for c in ["booking_id", "arrival_date", "market_segment", "reserved_room_type",
                        "lead_time", value_col, "p_cancel", "risk_band"] if c and c in df.columns]
    st.subheader("Top 100 riskiest bookings")
    st.dataframe(df.sort_values("p_cancel", ascending=False)[show].head(100), use_container_width=True)
    st.download_button("Download all scored bookings (CSV)",
                       df.sort_values("p_cancel", ascending=False).to_csv(index=False).encode("utf-8"),
                       file_name="scored_bookings.csv", mime="text/csv")

# ---------- Tab 2 ----------
with tab2:
    if not value_col:
        st.info("Khong co cot gross_value (file upload khong co booking_id that, nen khong join duoc).")
    else:
        if "arrival_date" in df.columns:
            d = df.copy()
            d["month"] = pd.to_datetime(d["arrival_date"], errors="coerce").dt.to_period("M").astype(str)
            m = d.groupby("month", as_index=False).agg(revenue_at_risk=("revenue_at_risk", "sum"),
                                                       booked_value=(value_col, "sum"))
            st.plotly_chart(px.bar(m, x="month", y=["booked_value", "revenue_at_risk"], barmode="group",
                                   title="Booked value vs revenue at risk by arrival month (EUR)"),
                            use_container_width=True)
        if "market_segment" in df.columns:
            s = df.groupby("market_segment", as_index=False)["revenue_at_risk"].sum()
            st.plotly_chart(px.bar(s, x="market_segment", y="revenue_at_risk",
                                   title="Revenue at risk by market segment"), use_container_width=True)
        top = st.slider("Review top X% of bookings by risk", 5, 50, 20, 5)
        n = int(len(df) * top / 100)
        ranked = df.sort_values("p_cancel", ascending=False)
        total = df.revenue_at_risk.sum()
        share = ranked.head(n).revenue_at_risk.sum() / total if total else 0
        st.metric(f"Share of revenue at risk captured in top {top}%", f"{share:.1%}")

# ---------- Tab 3 ----------
with tab3:
    st.caption("Bang luat tam thoi (README 6.4). Nguong chi la placeholder cho den khi chot F2/G1.")

    def action(r):
        high_value = value_col and pd.notna(r[value_col]) and r[value_col] >= df[value_col].median()
        if r.risk_band == "High" and high_value:
            return "Call guest + request deposit"
        if r.risk_band == "High":
            return "Email/SMS reminder + confirm"
        if r.risk_band == "Medium":
            return "Email reminder"
        return "No action"

    plan = df.sort_values("p_cancel", ascending=False).head(200).copy()
    plan["suggested_action"] = plan.apply(action, axis=1)
    plan["approved"] = False
    cols = [c for c in ["booking_id", "arrival_date", value_col, "p_cancel", "risk_band",
                        "suggested_action", "approved"] if c and c in plan.columns]
    edited = st.data_editor(plan[cols], use_container_width=True, disabled=[c for c in cols if c != "approved"])
    st.write(f"Approved: {int(edited['approved'].sum())} bookings (prototype - chua gui sang n8n)")

# ---------- Tab 4 ----------
with tab4:
    y = df["is_canceled"] if "is_canceled" in df.columns else None
    if y is not None:
        ok = y.notna()
        y, p = y[ok].astype(int), df.loc[ok, "p_cancel"]
    if y is not None and y.nunique() == 2:
        a, b = st.columns(2)
        a.metric("ROC-AUC", f"{roc_auc_score(y, p):.3f}")
        b.metric("PR-AUC", f"{average_precision_score(y, p):.3f}")
        cal = pd.DataFrame({"p": p, "y": y})
        cal = cal.assign(bin=pd.qcut(cal.p, 10, duplicates="drop")).groupby("bin", observed=True).agg(
            predicted=("p", "mean"), actual=("y", "mean")).reset_index(drop=True)
        st.plotly_chart(px.line(cal, y=["predicted", "actual"], markers=True,
                                title="Calibration by probability decile"), use_container_width=True)
    else:
        st.info("File khong co cot nhan that is_canceled (hoac chi co 1 lop), nen khong tinh duoc metric.")
    st.warning("Cac gia tri tai chinh tu cot syn_* la du lieu mo phong, khong phai du lieu that.")