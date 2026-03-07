# TraderStat: Micro-SaaS Launch & Operations Guide

Welcome to your new AI-built Micro-SaaS business. This document provides the exact steps required to deploy the app, set up monetization, and execute a marketing strategy to reach your goal of 100 paying users ($900/month recurring revenue).

---

## 1. Deployment Instructions

TraderStat is built with Python and Streamlit, making it incredibly fast to deploy. Since our goal is to keep hosting costs under $10/month, we recommend the following options.

### Option A: Streamlit Community Cloud (Recommended — $0/month)
Streamlit Cloud is the easiest and cheapest way to host a Streamlit app. It is entirely free for public repositories.

1. **Push to GitHub**: Commit the `traderstat` directory to a new GitHub repository.
2. **Sign up**: Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. **Deploy**: Click "New app", select your repository, set the branch to `main`, and the main file path to `Home.py`.
4. **Launch**: Click "Deploy". Your app will be live in minutes.
   *Note: Because we use SQLite, data is stored locally in the container. Streamlit Cloud containers can sleep, which may reset local files. For a production SaaS, you should migrate the SQLite connection in `database.py` to a managed PostgreSQL/MySQL database (like Supabase or Railway) before accepting paying users.*

### Option B: Render (Production Ready — ~$7/month)
Render provides persistent disks, which is perfect for keeping our SQLite database intact without needing an external database provider.

1. **Push to GitHub**: Commit your code to GitHub.
2. **Sign up**: Go to [render.com](https://render.com) and create an account.
3. **Create Web Service**: Click "New" -> "Web Service" and connect your GitHub repo.
4. **Configuration**:
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run Home.py --server.port $PORT --server.address 0.0.0.0`
5. **Persistent Disk**: In the Advanced settings, add a persistent disk mounted to `/data` and update the `DB_PATH` in `database.py` to point to this directory.
6. **Deploy**: Select the Starter tier ($7/month) and deploy.

---

## 2. Monetization Setup (Stripe)

To charge $9/month and manage the Free vs. Pro tiers, we will use Stripe Payment Links and Stripe Customer Portal.

### Step 1: Create Products in Stripe
1. Create a free [Stripe](https://stripe.com) account.
2. Navigate to **Products** -> **Add Product**.
3. Name: `TraderStat Pro`.
4. Pricing model: `Standard pricing`, Price: `$9.00`, Billing period: `Monthly`.
5. Save the product.

### Step 2: Create a Payment Link
1. Go to **Payments** -> **Payment Links** -> **New**.
2. Select the `TraderStat Pro` product you just created.
3. Customise the checkout page (add your logo and brand colour `#00D4AA`).
4. Copy the generated Payment Link URL.

### Step 3: Integrate into the App
1. Open `Home.py` and the Landing Page (`index.html`).
2. Replace the placeholder upgrade links (`https://traderstat.io/pricing` or `#pricing`) with your actual Stripe Payment Link.
3. *Authentication Note*: Currently, the app uses a default local user. To implement true multi-tenant SaaS authentication, you can integrate [Streamlit-Authenticator](https://github.com/mkallas/streamlit-authenticator) or a service like Clerk. Once a user pays via Stripe, you can use Stripe Webhooks to update their user role to "Pro" in your database.

---

## 3. User Acquisition & Marketing Strategy

To reach your goal of 100 paying users, you need a focused, low-cost marketing strategy targeting your specific niche: futures, options, and prop firm traders.

### Phase 1: Free Tool Lead Generation (The "Trojan Horse")
Traders love free tools. We will use the **Risk Calculator** as our primary lead magnet.
- **Action**: Create short, punchy screen-recordings of the Risk Calculator in action.
- **Hook**: "Stop blowing funded accounts. Calculate your exact position size in 3 seconds."
- **Call to Action**: "Link in bio to use the calculator for free."
- **Upsell**: Once they are using the free calculator, the app's sidebar naturally upsells them to the $9/mo Pro plan for unlimited journaling and the Prop Firm Tracker.

### Phase 2: Community Engagement
Do not spam links. Provide value first.

| Platform | Strategy | Frequency |
| :--- | :--- | :--- |
| **Twitter / X** | Post daily "End of Day" P&L screenshots using TraderStat's clean charts. Share risk management tips. Reply to large trading accounts (e.g., ICT, Al Brooks traders) with valuable insights. | 2x Daily |
| **Reddit** | Engage in `r/Daytrading`, `r/FuturesTrading`, and `r/propfirms`. Post educational content like "How I passed my FTMO challenge using strict risk management" and mention you built a tool to help track it. | 1x Weekly |
| **YouTube Shorts / TikTok** | Post 30-second videos showing common trading mistakes (e.g., over-leveraging) and how to fix them using TraderStat. Visuals perform incredibly well here. | 3x Weekly |

### Phase 3: Prop Firm Affiliate Leverage
Prop firm traders are your best target audience because they *must* follow strict rules.
- **Action**: Position TraderStat specifically as a "Prop Firm Evaluation Saver."
- **Content**: Write a guide or make a video on "The Math Behind Passing Prop Firm Evaluations."
- **Partnerships**: Once you have 20-30 users, reach out to small/medium trading Discord servers. Offer the server owner free lifetime access to Pro in exchange for them sharing the tool with their community.

---

## 4. The Math to $900/Month

Reaching 100 users at $9/month is highly achievable with consistent effort.

- **Conversion Rate**: Assume a 5% conversion rate from Free to Pro.
- **Free Users Needed**: To get 100 Pro users, you need roughly 2,000 free signups.
- **Traffic Needed**: Assume a 10% conversion rate from landing page visitor to free signup. You need 20,000 targeted website visitors.
- **Actionable Goal**: Generate 600-700 targeted visitors per day through Twitter, Reddit, and short-form video content over a 30-day launch period.

Stick to the plan, keep the app simple, and listen to your early users' feedback. Good luck with the launch!
