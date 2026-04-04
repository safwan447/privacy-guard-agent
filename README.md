---
title: Privacy Guard Agent
emoji: 🛡️
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 8000
pinned: false
---

# 🛡️ Privacy Guard Agent
**An OpenEnv Reinforcement Learning Environment for PII Redaction**

Developed for the **Meta OpenEnv Hackathon (April 2026)**. This repository contains a spec-compliant environment designed to evaluate agents on their ability to detect and redact Personally Identifiable Information (PII) from sensitive legal and medical documents.

---

## 🚀 Quick Start
This environment is built to be **multi-mode**, supporting both local execution and containerized deployment.

### 🔗 Live Deployment
The environment is live and graded at:
**[Hugging Face Space](https://huggingface.co/spaces/safwan447/privacy-guard-agent)**

### 🛠️ Tech Stack
* **Runtime:** Python 3.10+
* **Framework:** FastAPI (Uvicorn)
* **Deployment:** Docker (Hugging Face Spaces)
* **Standard:** OpenEnv Multi-mode Spec

---

## 📊 Environment Specification
This environment implements the following mandatory endpoints for the OpenEnv leaderboard:

* `GET /tasks`: Lists available redaction challenges.
* `POST /reset`: Restarts the document stream for a specific task.
* `POST /step`: Processes an agent's action (`KEEP` or `REDACT`) and returns rewards.
* `GET /state`: Returns the current progress within a document.

### 💰 Reward Structure
To ensure safe data handling, the reward system is strictly calibrated:
* **Correct Redaction:** `+1.0`
* **Correct Keep:** `+1.0`
* **Data Leak (PII Kept):** `0.0` (Critical Failure)
* **Over-Redaction:** `0.0`

---

## 📂 Project Structure
```text
├── server/             # FastAPI implementation
├── env.py              # RL Environment logic & Reward system
├── models.py           # Pydantic data models
├── inference.py        # Baseline LLM inference script
├── docs.json           # Encrypted/Mock PII dataset
└── Dockerfile          # Container configuration