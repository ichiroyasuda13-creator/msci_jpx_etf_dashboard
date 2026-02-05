# Deploying MSCI ETF Dashboard to Streamlit Cloud

Since you are already using GitHub, deploying to **Streamlit Community Cloud** is the easiest way to go live. It is free and connects directly to your repository.

## Prerequisites

1. **GitHub Account**: You (presumably) have one.
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/) (use your GitHub account).

## Step 1: Push Code to GitHub

Ensure your latest code is pushed to your GitHub repository.

```bash
git add .
git commit -m "Finalize Ver.1 of MSCI ETF Dashboard"
git push
```

## Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"New app"**.
3. Select **"Use existing repo"**.
4. **Repository**: Select your repository (e.g., `your-username/my-project`).
5. **Branch**: Usually `main` or `master`.
6. **Main file path**: Enter `msci_dashboard/app.py`.
    * *Note: Since your app is in a subdirectory, make sure to specify the full path.*
7. Click **"Deploy!"**.

## Step 3: Verify

Streamlit Cloud will detect your `requirements.txt`, install dependencies (`yfinance`, `plotly`, etc.), and launch the app.

once deployed, you will get a public URL like `https://msci-dashboard-ver1.streamlit.app` that you can share!
