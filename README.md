# 🎌 Multi-AI Agent System

A **production-oriented Multi-AI Agent System** that allows users to interact with multiple AI agents through a web interface.
This project focuses not only on AI functionality but also on **backend architecture, containerization, and CI/CD automation**.

---

## 👤 Author

**Abhishek Khopade**

Aspiring **ML Engineer | MLOps | LLMOps**

🔗 GitHub:
[https://github.com/ABHISHEKKHOPADE](https://github.com/ABHISHEKKHOPADE)

---

## 🚀 Features

* Multi-Agent AI interaction
* FastAPI backend APIs
* Streamlit frontend UI
* LangChain / LangGraph orchestration
* Groq LLM integration
* Docker containerization
* Jenkins CI/CD pipeline
* SonarQube static code analysis
* Error handling & modular architecture

---

## 🧱 Tech Stack

### Backend

* Python
* FastAPI
* LangChain / LangGraph
* Groq LLM

### Frontend

* Streamlit

### DevOps & Tools

* Docker
* Jenkins
* SonarQube
* Git & GitHub

---

## 🏗️ Project Architecture

```
User
  ↓
Streamlit UI
  ↓
FastAPI Backend
  ↓
AI Agents (LangChain / LangGraph + Groq)
  ↓
Docker
  ↓
Jenkins CI/CD Pipeline
  ↓
SonarQube Analysis
```

---

## 📂 Project Structure

```
MULTI-AI-AGENT-SYSTEM
│
├── app/
│   ├── core/
│   ├── config/
│   ├── common/
│   └── main.py
│
├── frontend/
│   └── streamlit_app.py
│
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/ABHISHEKKHOPADE/MULTI-AI-AGENT-SYSTEM.git
cd MULTI-AI-AGENT-SYSTEM
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Activate Environment**

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Mac**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.Run code

```bash
python main.py
```


## 🐳 Docker Setup

### Build Image

```bash
docker build -t multi-ai-agent .
```

### Run Container

```bash
docker run -p 8000:8000 multi-ai-agent
```

---

## 🔄 CI/CD Pipeline (Jenkins)

**Pipeline Stages**

* Pull code from GitHub
* Clone repository into Jenkins workspace
* Run SonarQube static code analysis


---

## 🔍 SonarQube Integration

SonarQube helps in:

* Detecting **bugs**
* Identifying **security vulnerabilities**
* Finding **code smells**
* Measuring **code quality metrics**

This ensures **clean, maintainable, and production-ready code**.

---

## 🧪 Future Improvements

* Authentication & Authorization
* Monitoring & Logging
* Automated Testing
* Kubernetes Deployment
* Cloud Deployment

---

## 📚 Key Learnings

* CI/CD automation using Jenkins
* Docker networking & containerization
* Static code analysis with SonarQube
* Multi-agent AI orchestration
* Backend API structuring

---

## 🤝 Contribution

Pull requests are welcome.
For major changes, please open an issue first to discuss what you would like to change.
