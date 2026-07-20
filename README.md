# BigQuery Conversational Analytics Data Agent Deployment Suite

This package provides a secure, interactive pipeline to deploy and update conversational data agents (built-in to BigQuery Agent Studio) on any target Google Cloud project.

It features a **Tailwind-powered Control Plane Dashboard** that runs locally on your system to manage configuration parameters, authenticate credentials, examine verified queries, and execute the installation pipeline.

---

## 🛠️ Quick Start Guide

### 1. Provision IAM Roles
Confirm your executing identity has been assigned the following roles:
*   `roles/geminidataanalytics.dataAgentCreator` (To register context variables and conversational agents)
*   `roles/aiplatform.user` (To call Vertex AI Gemini models to formulate questions)
*   `roles/bigquery.dataViewer` (To view table schemas and structures)
*   `roles/bigquery.jobUser` (To run agent validation tasks)

### 2. Enable Google Cloud APIs
Ensure the necessary Google APIs are active in your project:
```bash
gcloud services enable cloudaicompanion.googleapis.com \
                       geminidataanalytics.googleapis.com \
                       bigquery.googleapis.com \
                       dataform.googleapis.com \
                       aiplatform.googleapis.com
