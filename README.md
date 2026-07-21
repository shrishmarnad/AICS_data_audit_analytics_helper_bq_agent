# BigQuery Conversational Analytics Data Agent Deployment Suite

This package provides a secure, interactive pipeline to deploy and update conversational data agents (built-in to BigQuery Agent Studio) on any target Google Cloud project.

To eliminate setup friction, it features a local web-based, **Tailwind-powered Control Plane Dashboard** that runs on your system. This tool manages credentials, edits system markdown files, inspects queries, and handles deployment from a single, intuitive interface.

The deployment script is built on a highly portable Python engine that programmatically translates and provisions the analytics agent using the **Google Cloud Conversational Analytics API (`geminidataanalytics.googleapis.com`)**.

---

## 📋 Prerequisites & Permissions

### 1. IAM Roles
Ensure the target GCP user or deploying service account is granted the following IAM roles on the target project:

| IAM Role | Description |
| :--- | :--- |
| **`roles/geminidataanalytics.dataAgentCreator`** | Authorizes registration of `DataAgent` and published Context objects on the project. |
| **`roles/aiplatform.user`** | Required to run the Vertex AI Gemini models that generate natural language questions. |
| **`roles/bigquery.dataViewer`** | Allows the Conversational Data Agent to inspect metadata and schemas. |
| **`roles/bigquery.jobUser`** | Permits the agent to execute generated queries on the client's dataset. |

### 2. Enable Google Cloud APIs
Ensure the necessary Google APIs are active in your target GCP project:

```bash
gcloud services enable cloudaicompanion.googleapis.com \
                       geminidataanalytics.googleapis.com \
                       bigquery.googleapis.com \
                       dataform.googleapis.com \
                       aiplatform.googleapis.com
```

---

## 📂 Folder and Code Setup

```text
├── requirements.txt            # Package dependency list
├── app.py                      # Control Plane launcher (Flask)
├── config.yaml                 # Configuration parameters
├── deploy_agent.py             # Auto-bootstrapping agent deployment engine
├── system_instructions.md      # Natural language system instructions
├── README.md                   # Project documentation
└── verified_queries/           # Directory for standardized, validated SQL queries
    ├── import_table_camelCase_schema/
    └── export_table_snake_case_schema/
```

---

## 🚀 Step-by-Step Dashboard Setup

1. **Clone and Install Dependencies**  
   Navigate to the project root and install the required packages. The local web engine automatically sets up your file system:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Dashboard**  
   Execute the local Flask dashboard manager:
   ```bash
   python app.py
   ```
   *The system will automatically open your default browser to **`http://localhost:8080`**.*

3. **Verify gcloud CLI Authentication**  
   Look at the top-right corner of the web interface. If the badge shows **Disconnected**, click **"Authenticate CLI"**. This will launch the standard Google Cloud browser login to securely provision your Application Default Credentials (ADC). Once complete, you will see a green checkmark (**✅ Authenticated**).

4. **Fill In Environment Configurations**  
   Complete the form on the left side of the dashboard, entering your Project ID, Project Number, and target BigQuery table names. Toggle the radio buttons to select either `camelCase` import tables or `snake_case` export tables.

5. **Customize System Instructions**  
   The middle-right editor panel preloads your `system_instructions.md`. Modify specific retail thresholds (e.g., maximum unjoined event rates or character limit validations) directly in this editor, and click **"Save System Instructions"**.

6. **Deploy the Agent**  
   Click the **"install BQ agent"** button at the bottom of the screen. The terminal window will stream real-time logs as it installs packages, translates SQL queries with Gemini, and provisions the agent in BigQuery Agent Studio.

***
