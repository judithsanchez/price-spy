# Price Spy User Guide

## What is Price Spy?

Price Spy is your personal price tracking assistant. It automatically monitors product prices on online stores and alerts you when prices drop to your target.

**How it works:**
1. You tell it what products you want to track and at what price you'd buy
2. It takes screenshots of product pages (like a human would)
3. AI reads the screenshot and extracts the current price
4. It stores the price history and shows you trends
5. When a price hits your target, you see a "DEAL" alert

**Why screenshots?** Many websites block traditional price scrapers. By using a real browser and reading screenshots with AI, Price Spy works on virtually any website without getting blocked.

---

## Quick Start (5 Minutes)

### 1. Start the Service

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

### 2. Open the Dashboard

Go to `http://localhost:8000` in your browser.

### 3. Add Sample Data (Optional)

Want to see how it looks with data first?

```bash
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli seed-test-data
```

Refresh the page - you'll see sample products with prices and deals.

---

## The Dashboard

When you open Price Spy, you see the main dashboard:

```
+------------------------------------------------------------------+
|  Dashboard                                                        |
|  Track and monitor product prices                                 |
+------------------------------------------------------------------+
|  DEAL ALERT! Eucerin is at target price! EUR 14.99               |
+------------------------------------------------------------------+
| Product     | Store  | Price  | Unit    | Target | Status | Action|
|-------------|--------|--------|---------|--------|--------|-------|
| Eucerin     | Amazon | 14.99  | 3.00/L  | 15.00  | DEAL   | [Spy] |
| Coca-Cola   | Bol    | 8.99   | 0.75/L  | 7.50   | Above  | [Spy] |
+------------------------------------------------------------------+
|  Scheduled Spy                    |  API Usage (Today)           |
|  Next: Tomorrow 08:00             |  gemini-flash: 5/250         |
|  Last: Completed (2 ok, 0 fail)   |  gemini-lite: 0/1000         |
|  [Run Now] [Pause]                |                              |
+------------------------------------------------------------------+
```

### What Each Column Means

| Column | Description |
|--------|-------------|
| **Product** | The product name you're tracking |
| **Store** | Which online store this link is from |
| **Price** | Current price (last extracted) |
| **Unit Price** | Price per liter/kg for easy comparison |
| **Target** | Your target price (what you'd pay) |
| **Status** | "DEAL" (at/below target) or "Above target" |
| **Screenshot** | Click to see the captured page |
| **Spy Now** | Manually trigger price extraction |

---

## Setting Up Your Own Tracking

### Step 1: Add Products

Go to **Products** page (`/products`).

Click **Add Product** and fill in:
- **Name**: What you call this product (e.g., "Eucerin Urea Repair")
- **Category**: Optional grouping (e.g., "Skincare", "Groceries")
- **Target Price**: The price at which you'd buy (triggers DEAL alert)
- **Purchase Type**: "Recurring" (buy regularly) or "One-time"

**Example:**
```
Name: Coca-Cola Zero 12-pack
Category: Beverages
Target Price: 7.50
Purchase Type: Recurring
```

### Step 2: Add Stores

Go to **Stores** page (`/stores`).

Click **Add Store** and fill in:
- **Name**: Store name (e.g., "Amazon.nl", "Bol.com")
- **Standard Shipping**: Shipping cost if you don't hit free threshold
- **Free Shipping Threshold**: Order amount for free shipping

**Example:**
```
Name: Amazon.nl
Standard Shipping: 3.99
Free Shipping Threshold: 50.00
```

### Step 3: Track Items

Go to **Tracked Items** page (`/tracked-items`).

Click **Add Tracked Item** and fill in:
- **Product**: Select from your products
- **Store**: Select from your stores
- **URL**: The exact product page URL
- **Quantity**: Package size (e.g., 330 for a 330ml bottle)
- **Unit**: ml, L, g, kg, or "unit" for countable items
- **Items per Lot**: How many items in the package (e.g., 12 for a 12-pack)

**Example:**
```
Product: Coca-Cola Zero 12-pack
Store: Amazon.nl
URL: https://www.amazon.nl/dp/B08XYZ123
Quantity: 330
Unit: ml
Items per Lot: 12
```

### Step 4: Test It

Go back to the **Dashboard** and click **Spy Now** on your new item.

Wait about 10-15 seconds. The button will show "Extracting..." then either:
- **Success**: Shows the extracted price, page reloads
- **Error**: Shows what went wrong

---

## Automatic Price Checking

### How the Scheduler Works

Price Spy automatically checks all your tracked items once per day:

| Setting | Default | Description |
|---------|---------|-------------|
| **Time** | 8:00 AM | When the daily check runs |
| **Frequency** | Daily | Runs once per day |
| **Smart Skip** | Enabled | Skips items you manually checked today |

### What Happens Each Day

```
08:00 AM - Scheduler wakes up
         - Finds all active items NOT checked today
         - Processes them (max 10 at a time to respect API limits)
         - Saves prices to history
         - Marks items as checked
         - Done until tomorrow
```

### The "Smart Skip" Feature

If you manually click "Spy Now" at 10:00 AM, and the scheduler runs at 8:00 AM the next day, that item will be checked.

But if you click "Spy Now" at 10:00 AM, and the scheduler was supposed to run at 8:00 PM the same day, it will **skip** that item (already checked today).

This prevents wasting API quota on duplicate checks.

### Checking Scheduler Status

On the dashboard, the "Scheduled Spy" panel shows:
- **Items to Spy**: How many items will be checked
- **Next Scheduled Spy**: When the next automatic run happens
- **Last Run**: Status of the most recent run

### Manual Controls

- **Run Now**: Trigger an immediate extraction of all due items
- **Pause**: Stop automatic scheduling (manual still works)
- **Resume**: Restart automatic scheduling

---

## Understanding Prices

### Unit Prices

Price Spy calculates unit prices for easy comparison:

| Product | Price | Size | Unit Price |
|---------|-------|------|------------|
| Soda 12x330ml | 8.99 | 12 x 330ml = 3.96L | 2.27/L |
| Soda 6x500ml | 5.99 | 6 x 500ml = 3L | 2.00/L |

The 6-pack is actually cheaper per liter!

### Deal Detection

A "DEAL" badge appears when:
```
Current Price <= Target Price
```

You set the target price when creating a product. Set it to the price at which you'd definitely buy.

---

## API Usage & Rate Limits

Price Spy uses Google's Gemini AI to read screenshots. The free tier has limits:

| Model | Daily Limit | Used For |
|-------|-------------|----------|
| gemini-2.5-flash | 250/day | Primary extraction |
| gemini-2.5-flash-lite | 1000/day | Fallback when flash exhausted |

### What Happens When Limits Are Hit

1. Flash model hits 250 requests → Automatically switches to Lite
2. Lite model hits 1000 requests → Extractions fail until midnight PT
3. Limits reset at midnight Pacific Time

### Checking Your Usage

The dashboard shows current usage in the "API Usage" panel:
```
gemini-2.5-flash: 45/250
gemini-2.5-flash-lite: 0/1000
```

### Tips to Stay Within Limits

- Don't click "Spy Now" repeatedly on the same item
- Let the scheduler do its job (once per day per item)
- With 250 requests/day, you can track ~250 items daily

---

## Viewing History & Logs

### Logs Page

Go to **Logs** (`/logs`) to see:

**Extraction Logs**: Every price check attempt
- Status (success/error)
- Price extracted
- Which AI model was used
- How long it took

**Error Logs**: Detailed error information when things fail

### Filtering Logs

You can filter by:
- Status: Success only, Errors only
- Item: Specific tracked item
- Date range: Last 7 days, etc.

---

## Troubleshooting

### "Spy Now" Shows Error

**Common causes:**
1. **GEMINI_API_KEY not configured** - Check your `.env` file
2. **API quota exceeded** - Wait until midnight PT or use fewer requests
3. **Page couldn't load** - The URL might be wrong or site is down
4. **AI couldn't read price** - Some pages have complex layouts

**What to try:**
1. Check the screenshot (click the thumbnail) - did it capture correctly?
2. Look at the Logs page for detailed error messages
3. Try the URL in your browser - does it work?

### Prices Look Wrong

The AI reads what's visible in the screenshot. Issues can happen when:
- The page shows a different price after cookies/login
- There's a sale price vs regular price confusion
- The currency symbol wasn't recognized

**Fix:** Check the screenshot to see what the AI saw.

### Scheduler Isn't Running

Check the "Scheduled Spy" panel:
- Is it "Paused"? Click Resume
- Is "SCHEDULER_ENABLED" set to false in environment?

### Screenshots Are Missing

Make sure the `screenshots/` directory exists and is writable:
```bash
docker compose -f infrastructure/docker-compose.yml exec price-spy ls -la screenshots/
```

---

## Best Practices

### Naming Products

Be specific:
- Good: "Eucerin Urea Repair Plus 450ml"
- Bad: "Lotion"

### Setting Target Prices

Set realistic targets:
- Check the product's price history on the store
- Set target to a price you've seen it at during sales
- Too low = never triggers, too high = always triggers

### Organizing Stores

Create one store entry per website:
- "Amazon.nl" and "Amazon.de" should be separate stores
- Include shipping costs for accurate total cost comparison

### Managing Many Items

- Use categories to group products
- Disable alerts for items you're not actively watching
- Mark items as inactive instead of deleting (keeps history)

---

## Keyboard Shortcuts (Web UI)

Currently the web UI doesn't have keyboard shortcuts, but you can use browser shortcuts:
- **Ctrl+R** / **Cmd+R**: Refresh dashboard
- **Ctrl+Click**: Open link in new tab

---

## Getting Help

If something isn't working:

1. Check the **Logs** page for error details
2. Look at Docker logs: `docker compose -f infrastructure/docker-compose.yml logs`
3. Check your API key is valid at [Google AI Studio](https://aistudio.google.com/)
4. Report issues at the project's GitHub page

---

## Summary

| Task | How |
|------|-----|
| Add a product | Products page → Add Product |
| Add a store | Stores page → Add Store |
| Track a URL | Tracked Items → Add Tracked Item |
| Check price now | Dashboard → Spy Now button |
| See when next auto-check | Dashboard → Scheduled Spy panel |
| View price history | Logs page |
| Stop auto-checking | Dashboard → Pause button |
