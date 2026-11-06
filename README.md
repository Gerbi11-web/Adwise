# AdWise

AdWise is an advertising strategy planner. Users enter budget, country, city, adult age range, product/service, objective and optional platform preference. No user dataset upload is required.

## Backend
Open `AdWise_Backend_Training.ipynb` in Google Colab, upload the supplied `advertising.csv`, run all cells, and download `adwise_model.joblib`.

The backend keeps Age, Country, Area Income, Daily Internet Usage, Daily Time Spent on Site and derived timestamp features. It excludes City, Male (gender), and Ad Topic Line from model features.

## Streamlit
Place `app.py`, `requirements.txt`, and (after Colab training) `adwise_model.joblib` in the GitHub repository. Deploy `app.py` through Streamlit Community Cloud.

The recommendation engine uses transparent campaign-objective and product-category heuristics. The supplied dataset has no ad platform, campaign objective, spend, or conversion fields, so it cannot train a true platform-ranking or budget-optimization model. Budget splits are explicitly starting-test allocations, not empirical performance predictions.
