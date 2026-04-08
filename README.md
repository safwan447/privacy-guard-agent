---
title: Privacy Guard Agent
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
---

# 🛡️ Privacy Guard Agent (Meta OpenEnv Hackathon)


## Motivation & Description
The Privacy Guard Agent is a real-world simulation of an automated PII (Personally Identifiable Information) anonymization pipeline. As organizations increasingly use LLMs, the risk of leaking sensitive data like phone numbers and emails is a critical concern. This environment simulates a triage task where an agent must decide whether to redact or keep specific text segments to ensure data privacy before processing.

## Action & Observation Space

### Observation Space
The agent receives a `PrivacyObservation` containing:
* **text_segment:** The current string being evaluated.
* **context_before:** A 30-character prefix for context.
* **context_after:** A 30-character suffix for context.
* **segment_id:** The index of the segment within the document.

### Action Space
The agent can perform one of two actions:
* **REDACT:** Masks the segment as PII.
* **KEEP:** Allows the segment to pass through as safe text.

## Task Descriptions
| Task ID | Name | Difficulty | Description |
| :--- | :--- | :--- | :--- |
| `task_1_simple` | Pattern Matching | Easy | Identifying standard numeric patterns (phone numbers). |
| `task_2_contextual` | Entity Recognition | Medium | Identifying names and entities that require sentence context. |
| `task_3_legal` | High-Stakes Anonymization | Hard | Dealing with mixed legal jargon and alphanumeric IDs. |

## Setup & Usage

### Local Development
1. **Clone the repo:** `git clone https://github.com/safwan447/privacy-guard-agent`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Run the server:** `python server/app.py`
4. **Run inference:** `python inference.py`

### Docker Support
The project is fully containerized. To build and run:
```bash
docker build -t privacy-agent .
docker run -p 8000:8000 privacy-agent