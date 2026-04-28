# 🥬 SmartFresh AI — Operations Intelligence Platform

## 🚀 Overview
SmartFresh AI is an end-to-end **operations intelligence and AI-powered decision support system** designed for fresh produce companies like *Insalata dell’Orto*.

It combines:
- 📊 Data analytics  
- 🏭 ERP-style production planning  
- 🤖 AI Copilot  
- 🧠 Autonomous AI Agent  

to transform raw operational data into **actionable insights and optimized production decisions**.

---

## 🎯 Problem
Fresh produce operations are complex and require coordination across:

- Orders (client demand)
- Packaging (colli, buste, weight)
- Raw materials (cases, kg)
- Production (machines, shifts)
- Logistics (delivery deadlines)
- Quality (waste, defects, temperature)

Most systems focus on reporting, not **decision-making**.

---

## 💡 Solution
SmartFresh AI acts as a **digital operations layer** that:

- Simulates real production workflows  
- Optimizes resource usage  
- Detects risks automatically  
- Supports decisions with AI  

---

## 🧩 Features

### 📊 Executive Dashboard
- Production, sales, stock KPIs  
- Waste and defect tracking  
- Delivery performance  

---

### 🥬 Operations Control
- Real-time operational monitoring  
- Inventory and expiry tracking  

---

### ✅ Quality & Sentiment
- Waste & defect analysis  
- Supplier feedback sentiment analysis  

---

### 🔎 Traceability & Risk
- Batch-level traceability  
- Backend risk scoring via FastAPI  

---

### 🏭 ERP Production Planner
Simulates real production logic:

- Colli → Buste → Kg → Cases → Pedane  
- Machine assignment  
- Shift allocation  
- Deadline optimization  

Supports:
- Forward calculations (orders → resources)  
- Reverse calculations (resources → output)  

---

### 🤖 AI Copilot
Natural language assistant that:
- Answers operational questions  
- Uses real calculation functions  
- Provides recommendations  

---

### 🧠 AI Production Agent
Autonomous layer that:
- Monitors operations continuously  
- Detects risks (waste, delays, temperature, defects)  
- Recommends actions  
- Simulates decision-making  

---

## 🗂 Dataset

The system uses a **realistic synthetic dataset aligned with production workflows**, including:

- Orders (client, product, colli)
- Packaging (buste, grams per unit)
- Raw materials (cases, kg)
- Logistics (delivery, delays, departure time)
- Production (machines, shifts)
- Quality (waste, defects, temperature)
- Supplier feedback (text + rating)

---

## 🏗 Architecture

Frontend (Streamlit)
↓
AI Layer (Gemini / LLM)
↓
Logic Layer (Production Functions)
↓
Backend API (FastAPI Risk Engine)
↓
Data Source (CSV / Database)

---

## ⚙️ Tech Stack

- Python  
- Streamlit (Frontend UI)  
- FastAPI (Backend API)  
- Pandas (Data Processing)  
- Plotly (Visualization)  
- Google Gemini (AI)  

---

## 🔌 Future Integration

This system can be connected to:

- SQL databases (PostgreSQL, SQL Server, MySQL)
- ERP systems
- Internal production APIs

via:
- secure API layer  
- read-only database access  

---

## 🚀 Deployment

### Run locally

```bash

streamlit run app.py

 Backend API

python -m uvicorn api:app --reload

📱 UI Notes
	•	Optimized for desktop dashboards
	•	Mobile supported with responsive layout
	•	Light theme for readability in operations environments

⸻

🎯 Vision

SmartFresh AI is designed as a foundation for an AI-driven operations system:
	•	From dashboards → decision systems
	•	From Copilot → AI Agent
	•	From analysis → automation

⸻

👤 Author

Abdoulie J Bah
AI Engineer | Data Scientist | Operations Intelligence

⸻

🔥 Key Idea

“This project models real production workflows and builds a system that supports operational decision-making, not just reporting.”
