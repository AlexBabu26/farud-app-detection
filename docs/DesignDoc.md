# Design Document: Fraud App Detection System
**Project Title:** Fraud App Detection using Sentiment Analysis  
**Design Inspiration:** Modern Industrial SaaS / Prodmast Aesthetic  
**Status:** Design Phase  

---

## 1. Executive Summary
**Objective:** To create a high-performance, data-driven platform that identifies fraudulent mobile applications by analyzing user reviews and sentiments. The design balances "Security/Trust" with "Advanced Analytics," using a clean, professional UI to make complex NLP (Natural Language Processing) data easily digestible for security analysts.

---

## 2. Visual Identity & Brand Guidelines

### 2.1 Color Palette (Security & Trust)
The palette is derived from the "Prodmast" industrial blue, which conveys stability and technological authority.
* **Primary Action:** `#0061FF` (Electric Blue) – Used for "Run Analysis" buttons and high-risk alerts.
* **Deep Background:** `#0F1113` (Ebony) – Used for sidebars and dark-mode dashboard cards to ground the interface.
* **Surface White:** `#FFFFFF` – Used for the main workspace to ensure maximum readability of sentiment text.
* **Sentiment Indicators:**
    * *Fraudulent/Negative:* `#FF4D4D` (Vivid Red)
    * *Legitimate/Positive:* `#00C853` (Emerald Green)
    * *Neutral/Suspicious:* `#FFAB00` (Amber)

### 2.2 Typography
* **Headings:** `Plus Jakarta Sans` (Bold, -0.02em tracking). This provides a modern, "tech-first" feel.
* **Body/Data:** `Inter` or `Roboto Mono`. Monospaced fonts are used for technical metadata (App IDs, Developer Keys) to improve scanning accuracy.

### 2.3 Iconography & Visual Assets
* **Icon Style:** 2px stroke width, rounded terminals.
* **Imagery:** Abstract 3D visualizations of "connected nodes" or "scanning glass" effects, replacing the industrial machinery from the inspiration shot.
* **Data Visualization:** Clean, thin-line area charts for sentiment trends over time.

---

## 3. Layout Structure (The "Prodmast" Flow)

### Section 1: The Command Center (Hero)
* **Headline:** "Detect Deception Before It Spreads."
* **Sub-headline:** "Harnessing advanced Sentiment Analysis to identify fraudulent patterns in app store reviews with 98% accuracy."
* **Main Action:** A prominent input field where users can paste an **App Store URL** or **Package ID** to begin an instant scan.
* **Visual:** A dashboard mockup showing an "In-Progress" scan animation.

### Section 2: Real-time Sentiment Metrics
* **KPI Cards:** Four high-level metric cards:
    1.  *Total Reviews Analyzed*
    2.  *Fraud Probability Score (%)*
    3.  *Dominant Sentiment (Negative/Angry)*
    4.  *Bot/Spam Detection Flag*

### Section 3: The Analysis Engine (Feature Breakdown)
Using the alternating layout from the design:
* **NLP Processing:** Showcasing how the system breaks down "Keywords" (e.g., 'scam', 'fake', 'stole').
* **Review Clustering:** A visual map of grouped reviews that share suspicious linguistic patterns.
* **Developer History:** A secondary check on the app creator’s past reputation.

### Section 4: Deep-Dive Review Table
* A clean, paginated list of reviews.
* Each row features a **Sentiment Tag** (Red/Green) and a **Weight Score** indicating how much that specific review contributed to the "Fraud" verdict.

---

## 4. Interaction Design (UI/UX)

| Component | Interaction |
| :--- | :--- |
| **Search Bar** | Auto-suggests apps as the user types the name. |
| **Sentiment Toggle** | Allows users to filter the dashboard to show *only* negative/suspicious reviews. |
| **Analysis Cards** | Hovering over a "Risk Score" reveals a tooltip explaining the logic (e.g., "High frequency of 'refund' mentions"). |
| **Transitions** | Smooth "skeleton screen" loading states while the NLP engine processes the data. |

---

## 5. Technical Requirements for Implementation

### Frontend (The Look)
* **Framework:** React.js or Vue.js.
* **Styling:** Tailwind CSS (for the Prodmast-style spacing and utility classes).
* **Charts:** Recharts or Chart.js for the sentiment distribution graphs.

### Backend (The Logic)
* **NLP Engine:** Python (using NLTK, Spacy, or Transformers/BERT).
* **Scraper:** Fast API or Selenium to fetch real-time reviews.
* **Database:** PostgreSQL for storing app history and fraud signatures.

---

## 6. Design Principles
1.  **Clarity over Decoration:** Every visual element must serve the goal of identifying risk.
2.  **Immediate Feedback:** Users should know within 3 seconds if an app is "High Risk."
3.  **Clean Density:** Provide a lot of data (reviews, scores, dates) without making the interface feel cluttered, using generous whitespace (16px - 24px padding).