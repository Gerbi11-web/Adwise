
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

st.set_page_config(page_title="AdWise | Advertising Strategy", page_icon="🎯", layout="wide")

st.title("🎯 AdWise")
st.subheader("Make smarter advertising decisions before you spend.")
st.write("Tell AdWise about your business, budget and intended adult audience. It will build a practical starting strategy.")

MODEL_PATH = Path(__file__).parent / "adwise_model.joblib"
PROFILE_PATH = Path(__file__).parent / "adwise_country_reference.csv"

OBJECTIVES = {
    "Brand awareness": ["Meta Ads", "TikTok Ads", "YouTube Ads", "Google Display"],
    "Website traffic": ["Google Search Ads", "Meta Ads", "TikTok Ads", "Pinterest Ads"],
    "Engagement": ["Meta Ads", "TikTok Ads", "YouTube Ads"],
    "Lead generation": ["Meta Ads", "Google Search Ads", "LinkedIn Ads"],
    "Sales and conversions": ["Google Search Ads", "Meta Ads", "TikTok Ads"],
    "App promotion": ["Google App Campaigns", "Meta Ads", "TikTok Ads"]
}
PLATFORM_NOTES = {
    "Meta Ads": "Useful for visual discovery, broad reach, retargeting where permitted, and lead or conversion campaigns.",
    "Google Search Ads": "Useful when people actively search for a product, service, or solution.",
    "Google Display": "Useful for visual reach across websites and apps; often more awareness-oriented.",
    "YouTube Ads": "Useful for video storytelling, demonstrations, and awareness.",
    "TikTok Ads": "Useful for short-form video discovery and creative-led awareness or traffic.",
    "Pinterest Ads": "Can suit discovery and planning categories such as home, fashion, food, and lifestyle.",
    "LinkedIn Ads": "Often relevant for B2B services, professional audiences, and business leads.",
    "Google App Campaigns": "Designed to promote app installs and in-app actions across Google's inventory."
}

def score_platforms(objective, product, budget, preference):
    candidates = OBJECTIVES[objective][:]
    p = product.lower()
    # Transparent category fit adjustments; these are strategy heuristics, not learned performance.
    if any(k in p for k in ["business", "software", "saas", "consult", "enterprise", "recruit"]):
        if "LinkedIn Ads" not in candidates and objective in ["Lead generation", "Brand awareness"]:
            candidates.insert(0, "LinkedIn Ads")
    if any(k in p for k in ["fashion", "beauty", "skincare", "food", "home", "decor", "craft"]):
        if "Pinterest Ads" not in candidates and objective in ["Website traffic", "Brand awareness"]:
            candidates.append("Pinterest Ads")
    if preference != "Let AdWise choose":
        candidates = [preference] + [x for x in candidates if x != preference]
    # Keep the recommendation explainable; do not imply a platform is proven best.
    return candidates[:3]

def money(amount, currency):
    return f"{currency}{amount:,.0f}"

with st.form("campaign_form"):
    st.markdown("### 1. Tell us about your campaign")
    a, b = st.columns(2)
    with a:
        business = st.text_input("Business or brand name (optional)")
        product = st.text_input("What product or service are you advertising?", placeholder="e.g. Baby skincare products")
        objective = st.selectbox("What do you want your ads to achieve?", list(OBJECTIVES.keys()))
        budget_currency = st.selectbox("Budget currency", ["₦", "$", "£", "€", "₹", "GH₵", "KSh"])
        budget = st.number_input("Total advertising budget", min_value=1.0, value=100000.0, step=5000.0)
    with b:
        country = st.text_input("Target country", placeholder="e.g. Nigeria")
        city = st.text_input("Target city or area", placeholder="e.g. Lagos")
        min_age, max_age = st.slider("Adult audience age range", min_value=18, max_value=80, value=(25, 45))
        preference = st.selectbox("Platform preference", ["Let AdWise choose"] + sorted(set(sum(OBJECTIVES.values(), [])) | {"LinkedIn Ads", "Pinterest Ads", "YouTube Ads", "Google Display"}))
    submitted = st.form_submit_button("Build my advertising strategy", type="primary", use_container_width=True)

if submitted:
    errors = []
    if not product.strip(): errors.append("Enter the product or service.")
    if not country.strip(): errors.append("Enter a target country.")
    if not city.strip(): errors.append("Enter a target city or area.")
    if budget <= 0: errors.append("Enter a budget greater than zero.")
    if errors:
        for e in errors: st.error(e)
        st.stop()

    # Simple planning allocation; label explicitly as a starting test split, not a performance forecast.
    platforms = score_platforms(objective, product, budget, preference)
    weights = [0.50, 0.30, 0.20][:len(platforms)]
    weights = [w / sum(weights) for w in weights]
    allocations = [(p, budget*w, w) for p, w in zip(platforms, weights)]

    st.divider()
    st.success("Your starting advertising strategy is ready.")
    st.header("Your AdWise strategy")
    if business.strip(): st.caption(f"Prepared for {business.strip()}")
    st.write(f"**Market:** {city.strip()}, {country.strip()}  ·  **Adult audience:** {min_age}–{max_age}  ·  **Objective:** {objective}")
    st.caption("The recommendations below are planning guidance based on campaign objective and product category. They are not guaranteed results or live auction forecasts.")

    st.subheader("1. Recommended advertising platforms")
    for idx, (platform, amount, weight) in enumerate(allocations, start=1):
        with st.container(border=True):
            st.markdown(f"**{idx}. {platform}**")
            st.write(PLATFORM_NOTES.get(platform, "Potentially suitable depending on your campaign setup and market."))
            st.metric("Suggested test allocation", money(amount, budget_currency), f"{weight:.0%} of budget")

    st.subheader("2. Suggested budget plan")
    st.write("Start with a controlled test allocation, review actual results, then move more budget toward the platform and creative that meet your goal.")
    alloc_df = pd.DataFrame([{"Platform": p, "Suggested test budget": money(v, budget_currency), "Share": f"{w:.0%}"} for p, v, w in allocations])
    st.dataframe(alloc_df, use_container_width=True, hide_index=True)

    st.subheader("3. Campaign setup")
    setup = {
        "Brand awareness": ["Use short, memorable creative that clearly introduces the brand.", "Measure reach, impressions, video views and frequency."],
        "Website traffic": ["Use a clear reason to visit the website and a fast, mobile-friendly landing page.", "Measure landing-page views, link clicks and cost per landing-page view."],
        "Engagement": ["Test creative that invites meaningful interaction.", "Measure engagement rate, saves, shares and relevant comments."],
        "Lead generation": ["Use a focused offer and a short lead form; explain how contact details will be used.", "Measure qualified leads and cost per qualified lead."],
        "Sales and conversions": ["Use clear product information, pricing, trust signals and a friction-light checkout.", "Measure purchases, conversion rate and cost per purchase when tracking is configured."],
        "App promotion": ["Show the app's main value quickly and make the install action clear.", "Measure installs and meaningful in-app actions."]
    }
    for item in setup[objective]:
        st.write("• " + item)

    st.subheader("4. Audience and location guidance")
    st.write(f"Set the campaign's location to **{city.strip()}, {country.strip()}** and use the adult age range **{min_age}–{max_age}** where the platform permits it.")
    st.write("Use audience settings that comply with local law and each platform's policies. For products intended for babies or children, direct advertising toward appropriate adult purchasers such as parents or guardians—not children.")

    st.subheader("5. AdWise audience reference model")
    if MODEL_PATH.exists():
        try:
            artifact = joblib.load(MODEL_PATH)
            model = artifact["model"]
            medians = artifact.get("numeric_medians", {})
            # User-specified city is deliberately not used as a model feature.
            # Use selected age midpoint and country; use dataset medians for fields the form does not ask for.
            row = {
                "Daily Time Spent on Site": medians.get("Daily Time Spent on Site", 0),
                "Age": (min_age + max_age) / 2,
                "Area Income": medians.get("Area Income", 0),
                "Daily Internet Usage": medians.get("Daily Internet Usage", 0),
                "Country": country.strip(),
                "Timestamp_Month": medians.get("Timestamp_Month", 6),
                "Timestamp_DayOfWeek": medians.get("Timestamp_DayOfWeek", 3)
            }
            sample = pd.DataFrame([row])[artifact["feature_columns"]]
            probability = float(model.predict_proba(sample)[0][1])
            st.metric("Dataset-based ad-click propensity estimate", f"{probability:.0%}")
            st.caption("This is a model score for a synthetic audience profile using dataset median values for unprovided fields. It is not a forecast of campaign results, platform performance, or sales. If the selected country was absent from training data, its country feature is treated as previously unseen.")
            with st.expander("View model evaluation"):
                st.json(artifact.get("metrics", {}))
        except Exception as e:
            st.warning(f"The saved model could not be loaded or applied: {e}")
    else:
        st.info("The strategy planner works without the Colab model. After training in Colab, add adwise_model.joblib beside app.py in your GitHub repository to enable the optional audience reference score.")

    report = f"""ADWISE ADVERTISING STRATEGY
Business: {business or 'Not provided'}
Product/service: {product}
Budget: {money(budget, budget_currency)}
Objective: {objective}
Market: {city}, {country}
Adult audience age range: {min_age}-{max_age}

Suggested test allocation:
""" + "\\n".join([f"- {p}: {money(v, budget_currency)} ({w:.0%})" for p,v,w in allocations]) + "\\n\\nNote: Strategy allocations are heuristic starting points, not guaranteed outcomes or live media-price forecasts."
    st.download_button("Download strategy report", report, file_name="adwise_strategy.txt", mime="text/plain")

st.divider()
st.caption("AdWise is a planning assistant, not an advertising platform. Confirm current targeting rules, available objectives, local requirements, and media costs in the platform before launching. No campaign result is guaranteed.")
