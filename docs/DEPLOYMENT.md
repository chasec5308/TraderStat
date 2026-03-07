# TraderStat: Zero-Cost Deployment Guide

To launch TraderStat for free and get your public link (e.g., `https://traderstat.streamlit.app`), we will use **Streamlit Community Cloud**. It is 100% free, requires no server management, and deploys directly from GitHub.

---

## Step 1: Prepare Your Local Environment

1. **Create a GitHub Account**: If you don't have one, sign up for free at [github.com](https://github.com).
2. **Install Git**: Ensure Git is installed on your computer.
3. **Organise the Codebase**: The `traderstat` directory provided in the zip file is already perfectly organised. It contains:
   - `Home.py` (The main entry point)
   - `pages/` (The individual tools)
   - `database.py` & `utils.py` (Backend logic)
   - `requirements.txt` (Dependencies)

*Note: The `requirements.txt` is crucial. Streamlit Cloud reads this file to install the necessary packages (pandas, plotly, etc.) before starting your app.*

---

## Step 2: Push the Code to GitHub

1. Open your terminal (or command prompt) and navigate to the extracted `traderstat` folder:
   ```bash
   cd path/to/traderstat
   ```

2. Initialise a new Git repository:
   ```bash
   git init
   ```

3. Add all files to the repository:
   ```bash
   git add .
   ```

4. Commit the files:
   ```bash
   git commit -m "Initial commit for TraderStat launch"
   ```

5. Go to GitHub and click **New Repository** (+ icon in the top right).
   - Name it `traderstat`.
   - Make it **Public** (Streamlit Community Cloud requires public repos for the free tier).
   - Do not initialise with a README, .gitignore, or license (leave them unchecked).

6. Copy the commands under *"…or push an existing repository from the command line"* and paste them into your terminal. It will look like this:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/traderstat.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 3: Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click the **New app** button.
3. Fill in the deployment form:
   - **Repository**: Select `YOUR_USERNAME/traderstat` from the dropdown.
   - **Branch**: `main`
   - **Main file path**: `Home.py`
   - **App URL**: You can customise this to be `traderstat` (if available), which will result in `https://traderstat.streamlit.app`.
4. Click **Deploy!**

### What happens next?
Streamlit will pull your code from GitHub, read `requirements.txt`, install the packages, and launch the app. This usually takes 1–2 minutes. You will see a balloon animation while it's "baking."

Once complete, your app is live on the internet!

---

## Step 4: Add Simple Analytics (Free)

To track your goal of reaching 50 users, we need analytics. Since Streamlit is a Python framework, traditional Google Analytics tracking codes don't work well out of the box.

**The Solution: Streamlit Analytics (Free)**

1. We will use the `streamlit-analytics2` package.
2. Open your `requirements.txt` and add:
   ```text
   streamlit-analytics2
   ```
3. Open `Home.py` and add these two lines:
   ```python
   import streamlit_analytics2 as streamlit_analytics
   
   # Add this right after st.set_page_config()
   with streamlit_analytics.track():
       # ... rest of your Home.py code ...
   ```
4. Commit and push these changes to GitHub:
   ```bash
   git add .
   git commit -m "Add analytics"
   git push
   ```
5. Streamlit Cloud will automatically detect the push and update your live app within seconds.

**To view your analytics:**
Navigate to `https://traderstat.streamlit.app/?analytics=on`.
*(You can set a password in Streamlit secrets so only you can view this page).*
