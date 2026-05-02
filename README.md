# 🥬 SmartFresh AI — Operations Intelligence Platform

## 🌐 Live Demo
https://smartfresh-insalata-dashboard-q7kkr8vgaj2zfgggkra8sf.streamlit.app

## 🚀 Overview
SmartFresh AI is a full-stack **AI-powered operations intelligence platform** for fresh produce operations.

It combines **Business Intelligence, Machine Learning, FastAPI backend scoring, AI Copilot assistance, autonomous agent monitoring, Slack/email alerts, and ERP-style production planning** into one decision-support system.

## 🎯 Problem
Fresh produce companies must coordinate production, inventory, quality, supplier performance, and logistics under strict time and freshness constraints.

Traditional dashboards show what happened. SmartFresh AI helps answer:

- What is going wrong?
- Which batches are risky?
- Which suppliers need attention?
- Which orders should be prioritized?
- What actions should be taken now?

## 💡 Solution
SmartFresh AI transforms operational data into decisions by combining:

- Real-time KPI monitoring
- ML-based batch risk prediction
- Revenue drop detection
- Supplier quality analysis
- Multi-agent AI recommendations
- Slack/email alerts for critical risks
- FastAPI backend risk scoring
- ERP-style production planning

## 🧩 Core Features

### 📊 Executive Dashboard
- Strategic production, sales, stock, waste, defects, revenue, and delivery KPIs
- Supplier risk overview
- Executive recommendations

### 📈 Business Intelligence
- Revenue trends and revenue drop intelligence
- Client dependency analysis
- Supplier quality scoring
- Feedback sentiment analysis
- Quality and business trend monitoring

### 🥬 Operations Control
- Inventory and expiry monitoring
- Delivery status tracking
- Delayed delivery analysis
- Stock by product

### 🏭 ERP Production Planner
Simulates production planning logic:

- Colli → Buste → Kg → Incoming cases → Pedane
- Machine assignment
- Shift allocation
- Production timeline
- Deadline and slack-time optimization

### 🤖 AI Copilot
An AI assistant for operational questions:

- Uses real calculation tools
- Maintains conversation memory
- Generates business recommendations
- Provides charts and multi-agent summaries

### 🧠 AI Production Agent
Autonomous risk monitoring layer:

- Detects waste, defects, cold-chain risk, delivery delay, and schedule risk
- Uses ML risk probability in alert prioritization
- Creates trackable actions
- Sends Slack/email notifications
- Simulates Kafka-style streaming events
- Connects to FastAPI backend for risk scoring

### 🧪 Machine Learning Risk Model
- XGBoost-style risk prediction pipeline
- Feature engineering for waste rate, defect rate, stock pressure, sell-through rate, and revenue per unit
- Batch-level risk probability
- ML-driven alert priority boosting
- Feature importance display

## 🏗 Architecture
---
User
↓
Streamlit Frontend
↓
Business Intelligence + AI Copilot + AI Production Agent
↓
Machine Learning Risk Model
↓
FastAPI Backend Risk Engine
↓
CSV / Database Layer
↓
Slack + Email Notification Layer


## ⚙️ Tech Stack

- Python  
- Streamlit  
- FastAPI  
- Pandas  
- NumPy  
- Plotly  
- Scikit-learn  
- XGBoost  
- Google Gemini  
- SQLite  
- Slack Webhooks  
- SMTP Email Alerts  



## 👥 Role-Based Access

- **Admin**: Full access to all modules  
- **Manager**: Strategic dashboards and AI control  
- **Operations**: Operations monitoring and planning  
- **Quality**: Quality analysis and AI Copilot  
- **Logistics**: Delivery tracking and execution  



## 🗂 Dataset

The project uses a realistic SmartFresh dataset including:

- Orders and clients  
- Products and suppliers  
- Production quantity  
- Quantity sold  
- Stock remaining  
- Waste quantity  
- Defect count  
- Temperature  
- Delivery status  
- Revenue  
- Feedback text and ratings  
- Expiry and logistics data  



## 🚀 Run Locally

Install dependencies:


pip install -r requirements.txt

Run Streamlit:

streamlit run app.py

Run FastAPI backend:

uvicorn api:app –reload


## 🔐 Environment Variables

Add these in your deployment:

GEMINI_API_KEY_1=your_key
SLACK_WEBHOOK_URL=your_webhook
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_app_password
ALERT_EMAIL_TO=receiver_email


## 🎯 Vision

SmartFresh AI transforms operations:

- From dashboards → decision systems  
- From alerts → actions  
- From analysis → automation  



## 👤 Author

**Abdoulie J Bah**  
AI Engineer • Data Scientist • Business Intelligence Developer  

🔗 LinkedIn: https://www.linkedin.com/in/abdoulie-j-bah-b71263244  
💻 GitHub: https://github.com/AbdoulieJBah  


## 🔥 Key Idea

> “This project models real production workflows and builds an AI system that supports operational decision-making — not just reporting.”

