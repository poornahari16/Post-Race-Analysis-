# 🏎️ Le Mans Telemetry Semantic Search & RAG Engine

## 🚀 Overview
This project is developed for **Hackathon 2025: The Engineering Advantage**, aimed at providing **Post-Session Analytics & Simulation** tools that transform raw racing telemetry into intelligent insights using modern AI techniques.

We built a semantic search engine that allows engineers to query telemetry data in natural language and receive meaningful, context-aware answers that can influence engineering decisions and race strategies.

---

## 🎯 Problem Statement
Race teams face a **data overload** post-race, with millions of telemetry points (e.g., tire pressure, coolant temperature, etc.) that require deep technical analysis to uncover performance trends. Manual analysis is slow and error-prone.

---

## 💡 Solution
We developed a **semantic search engine** and **RAG (Retrieval-Augmented Generation) system** that enables engineers to ask plain-English questions like:

> _"What tire pressures give high PES?"_

And receive answers such as:

> _"Higher pressures (21.5–22.5 PSI) may improve PES, but at the cost of grip."_  

This makes telemetry analysis fast, accessible, and insightful—even under time constraints.

---

## 🧠 Architecture

- **Telemetry Processing Pipeline**: Loads and transforms telemetry CSV data into descriptive text.
- **Embeddings**: Generated using OpenAI’s `text-embedding-3-small` model.
- **Vector Database**: Qdrant is used to store and search embeddings efficiently.
- **RAG Engine**: GPT-4/GPT-3.5 is used to generate intelligent responses based on semantic search context.

---

## 🧪 Sample Data Fields

- TirePressure_Front / Rear  
- TireSize_Front / Rear  
- Driver Weight (kg)  
- Coolant Temperature (°C)  
- PES (Performance Efficiency Score)  

The **PES** is calculated with:


---

## 📊 Data Visualizations

Included charts help visualize key correlations:
- [PES vs Avg Tire Pressure](./pes_vs_tire_pressure.png)
- [PES vs Avg Tire Size](./pes_vs_tire_size.png)
- [PES vs Coolant Temperature](./pes_vs_coolant_temp.png)
- [PES vs Driver Weight](./pes_vs_driver_weight.png)

These help teams identify which engineering parameters most affect performance.

---

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Libraries**: `pandas`, `openai`, `qdrant-client`, `seaborn`, `matplotlib`
- **Vector DB**: Qdrant (Docker container)
- **Models**: OpenAI Embeddings + GPT-4/3.5

---

## 🌱 Future Directions

- 🔴 Integrate live telemetry data
- 🟢 Build a web dashboard for real-time visualization
- 🔵 Expand to support batch simulations for race strategy planning

---

## 📚 Agentic Development Process (Meta-Challenge)
We used GPT extensively during development for:
- Planning architecture and component flow
- Writing and debugging data pipelines
- Generating synthetic datasets
- Validating our PES formula and visualization logic

This accelerated development and ensured a tighter feedback loop between idea and execution.

---
