#!/usr/bin/env python3
"""
Production deployment script for Google Cloud BigQuery Conversational Analytics Data Agents.
Features Automatic Package Bootstrapping, Semantic Table Classification, and LLM question generation.
"""

import os
import sys
import subprocess

# ------------------------------------------------------------------------------
# 🚀 Programmatic Dependency Bootstrapper
# ------------------------------------------------------------------------------
def bootstrap_dependencies():
    """Defensively checks and installs package requirements prior to loading modules."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        print("Checking and resolving package dependencies from requirements.txt...")
        try:
            # Executes standard pip module installer in quiet mode
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", req_path])
            print("Dependency check complete: All packages verified!")
        except Exception as e:
            print(f"Warning: Dependency bootstrapper failed: {e}. Launching using active global packages.", file=sys.stderr)

# Resolve package installation tasks first
bootstrap_dependencies()

# Proceed to load resolved packages safely
import re
import yaml
import logging
import argparse
import time
from typing import Dict, Any, List

try:
    from google.cloud import geminidataanalytics
    from google.api_core import client_options
    from google.api_core.exceptions import GoogleAPICallError
    from google.protobuf import field_mask_pb2
except ImportError:
    print("Error: Missing google-cloud-geminidataanalytics after bootstrap check. Please manually run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# Configure elegant logger output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def load_and_validate_config(config_path: str) -> Dict[str, Any]:
    """Loads and validates the YAML configuration schema."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
        
    required_keys = [
        'gcp_project_id', 'gcp_project_number', 'dataset_id',
        'catalog_table_id', 'events_table_id', 'agent_display_name',
        'agent_description', 'sql_directory', 'instructions_file', 'schema_type'
    ]
    
    missing = [key for key in required_keys if key not in config or config[key] is None]
    if missing:
        raise ValueError(f"Schema violation! Missing configuration parameters: {', '.join(missing)}")
        
    return config

def generate_question_via_llm(filename: str, sql_content: str, project_id: str, location: str) -> str:
    """
    Calls gemini-2.5-flash via Vertex AI to generate a highly professional and tailored
    natural language analytics question based on the SQL filename and content.
    Includes a robust rule-based fallback if API call fails.
    """
    lower_filename = filename.lower()
    
    # Standard prefix determination
    prefix = ""
    if lower_filename.startswith("catalog"):
        prefix = "catalog : "
    elif lower_filename.startswith("user_events") or lower_filename.startswith("events"):
        prefix = "user events: "

    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        logging.info(f"Initializing Vertex AI in {project_id} ({location}) for LLM question generation...")
        vertexai.init(project=project_id, location=location)
        model = GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
Analyze the following BigQuery SQL query filename and its contents to generate a single, highly professional, concise natural language query (question) that a business user would ask to execute this query.

SQL Filename: {filename}
SQL Content:
{sql_content[:1000]}

Guidelines:
1. The question must align with what the SQL checks.
2. If the filename starts with 'catalog', the output MUST start exactly with 'catalog : ' followed by the explanation. E.g., 'catalog_product_duplicate_title_check.sql' -> 'catalog : checks the distribution of products with duplicate titles'.
3. If the filename starts with 'user_events' or 'events', the output MUST start exactly with 'user events: ' followed by the explanation. E.g., 'user_events_detail_page_view_impression_check.sql' -> 'user_events: do deep checks related to impression details in the detail page view event'.
4. Return ONLY the final generated text. Do not include quotes, extra spaces, markdown formatting (like asterisks), or conversational preamble.
"""
        response = model.generate_content(prompt)
        text = response.text.strip().replace('"', '').replace("'", "")
        
        # Validate that the LLM respected the prefix rules; if not, enforce it
        if prefix:
            cleaned_text = re.sub(r'^(catalog\s*:\s*|user\s*events\s*:\s*)', '', text, flags=re.IGNORECASE).strip()
            text = f"{prefix}{cleaned_text}"
            
        logging.info(f"LLM successfully generated question: '{text}'")
        return text

    except Exception as e:
        logging.warning(f"Vertex AI LLM generation failed ({e}). Falling back to robust rule-based fallback logic.")
        
        # Precise exact matches for fallback
        if "duplicate_title" in lower_filename:
            return "catalog : checks the distribution of products with duplicate titles"
        elif "impression" in lower_filename and "detail_page_view" in lower_filename:
            return "user events: do deep checks related to impression details in the detail page view event"
        
        # Generic heuristic logic fallback
        base_name = filename.rsplit('.', 1)[0]
        desc_part = base_name
        for term in ["catalog_product_", "catalog_", "user_events_", "events_"]:
            if desc_part.startswith(term):
                desc_part = desc_part[len(term):]
                break

        spaced = desc_part.replace('_', ' ').replace('-', ' ').strip()
        action = f"do deep checks related to {spaced}" if "check" in lower_filename else f"analyze {spaced}"
        
        if prefix:
            return f"{prefix}{action}"
        return f"{spaced.title()}?"

def parse_and_replace_sql(sql_content: str, project_id: str, dataset_id: str, catalog_table: str, events_table: str) -> str:
    """
    Robust regex search-and-replace to locate inconsistent 3-part fully qualified
    table paths (e.g. project.dataset.table) and semantically replace them with
    the correct user-configured paths.
    """
    # Pattern designed to capture fully-qualified table references in SQL files
    # Consumes optional backticks, single quotes, or double quotes on segments or the full path.
    # Group 2: Project, Group 5: Dataset, Group 8: Table
    pattern = r'([`"\']?)([a-zA-Z0-9\-_]+)([`"\']?)\.([`"\']?)([a-zA-Z0-9\-_]+)([`"\']?)\.([`"\']?)([a-zA-Z0-9\-_]+)([`"\']?)'

    def replace_match(match):
        full_match = match.group(0)
        proj_seg = match.group(2)
        ds_seg = match.group(5)
        table_seg = match.group(8)

        # Confirm we have alphabetical characters (avoid matching things like numeric IP addresses or decimal floats)
        has_alpha = lambda s: any(c.isalpha() for c in s)
        if not (has_alpha(proj_seg) and has_alpha(ds_seg) and has_alpha(table_seg)):
            return full_match

        table_lower = table_seg.lower()

        # Semantic keywords to identify Catalog tables
        catalog_keywords = ["catalog", "product", "sku", "item", "inventory", "price", "colors", "metadata", "attributes", "title", "description"]
        # Semantic keywords to identify User Events tables
        events_keywords = ["event", "session", "visitor", "click", "traffic", "transaction", "behavior", "purchase", "impression", "action", "journey"]

        is_catalog = any(k in table_lower for k in catalog_keywords)
        is_events = any(k in table_lower for k in events_keywords)

        if is_catalog and not is_events:
            return f"`{project_id}.{dataset_id}.{catalog_table}`"
        elif is_events and not is_catalog:
            return f"`{project_id}.{dataset_id}.{events_table}`"
        else:
            # Score-based semantic lookup as fallback
            cat_score = sum(1 for k in catalog_keywords if k in table_lower)
            evt_score = sum(1 for k in events_keywords if k in table_lower)
            
            if cat_score > evt_score:
                return f"`{project_id}.{dataset_id}.{catalog_table}`"
            elif evt_score > cat_score:
                return f"`{project_id}.{dataset_id}.{events_table}`"
            else:
                # Fallback check on string terms
                if "event" in table_lower or "user" in table_lower or "session" in table_lower:
                    return f"`{project_id}.{dataset_id}.{events_table}`"
                return f"`{project_id}.{dataset_id}.{catalog_table}`"

    parsed_sql = re.sub(pattern, replace_match, sql_content)
    return parsed_sql

def create_valid_resource_id(display_name: str) -> str:
    """Derives a safe, lowercase alphanumeric resource ID (max 63 characters) matching AIP conventions."""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '-', display_name.lower())
    cleaned = re.sub(r'-+', '-', cleaned).strip('-')
    return cleaned[:63]

def get_gemini_client(location: str) -> geminidataanalytics.DataAgentServiceClient:
    """Configures regional endpoint overrides for sovereign data residency needs."""
    if not location or location == "global" or location == "us-central1":
        endpoint = "geminidataanalytics.googleapis.com"
    elif "-" in location:
        endpoint = f"geminidataanalytics-{location}.googleapis.com"
    else:
        endpoint = f"geminidataanalytics.{location}.rep.googleapis.com"
        
    logging.info(f"Targeting conversational analytics API endpoint: {endpoint}")
    opts = client_options.ClientOptions(api_endpoint=endpoint)
    return geminidataanalytics.DataAgentServiceClient(client_options=opts)

def main():
    parser = argparse.ArgumentParser(description="Programmatically create or update BigQuery Conversational Analytics Agents.")
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to configuration YAML.')
    parser.add_argument('--force', action='store_true', help='Force delete and recreate the agent if it already exists.')
    args = parser.parse_args()

    try:
        # 1. Loading and Validating Configurations
        config = load_and_validate_config(args.config)
        gcp_project_id = config['gcp_project_id']
        dataset_id = config['dataset_id']
        catalog_table_id = config['catalog_table_id']
        events_table_id = config['events_table_id']
        agent_display_name = config['agent_display_name']
        agent_description = config['agent_description']
        sql_parent_dir = config['sql_directory']
        instructions_file = config['instructions_file']
        location = config.get('location', 'us-central1')
        schema_type = config['schema_type'].lower()

        # Select subfolder based on schema choice
        if "import" in schema_type:
            schema_subfolder = "import_table_camelCase_schema"
        elif "export" in schema_type:
            schema_subfolder = "export_table_snake_case_schema"
        else:
            raise ValueError(f"Invalid schema_type parameter: '{config['schema_type']}'. Must contain 'import' or 'export'.")

        target_sql_dir = os.path.join(sql_parent_dir, schema_subfolder)
        logging.info(f"Selected target schema mode: '{schema_type}' -> folder path: '{target_sql_dir}'")

        if not os.path.exists(target_sql_dir):
            raise FileNotFoundError(f"Selected schema folder does not exist: {target_sql_dir}")

        # 2. Extract System Instructions
        if not os.path.exists(instructions_file):
            raise FileNotFoundError(f"System instructions markdown file not found: {instructions_file}")
        with open(instructions_file, 'r', encoding='utf-8') as f:
            instructions_content = f.read()

        # 3. Traversal, Parsing and verified Example Query mappings
        example_queries = []
        sql_files = [f for f in os.listdir(target_sql_dir) if f.endswith('.sql')]
        logging.info(f"Located {len(sql_files)} SQL verified queries in folder: '{target_sql_dir}'")

        for sql_file in sorted(sql_files):
            file_path = os.path.join(target_sql_dir, sql_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_sql = f.read()

            parsed_sql = parse_and_replace_sql(
                raw_sql,
                project_id=gcp_project_id,
                dataset_id=dataset_id,
                catalog_table=catalog_table_id,
                events_table=events_table_id
            )
            
            # AI-Powered Question Formulation via Gemini 2.5 Flash
            question = generate_question_via_llm(
                filename=sql_file,
                sql_content=raw_sql,
                project_id=gcp_project_id,
                location=location
            )
            
            example_queries.append(
                geminidataanalytics.ExampleQuery(
                    natural_language_question=question,
                    sql_query=parsed_sql
                )
            )
            logging.info(f"Verified query mapped: '{question}'")

        # 4. Assembling protobuf metadata schemas
        catalog_ref = geminidataanalytics.BigQueryTableReference(
            project_id=gcp_project_id, dataset_id=dataset_id, table_id=catalog_table_id
        )
        events_ref = geminidataanalytics.BigQueryTableReference(
            project_id=gcp_project_id, dataset_id=dataset_id, table_id=events_table_id
        )
        
        datasource_references = geminidataanalytics.DatasourceReferences(
            bq=geminidataanalytics.BigQueryTableReferences(
                table_references=[catalog_ref, events_ref]
            )
        )

        published_context = geminidataanalytics.Context(
            system_instruction=instructions_content,
            datasource_references=datasource_references,
            example_queries=example_queries,
            options=geminidataanalytics.ConversationOptions(
                analysis=geminidataanalytics.AnalysisOptions(
                    python=geminidataanalytics.AnalysisOptions.Python(enabled=True)
                )
            )
        )

        # Connect to DataAgent API
        client = get_gemini_client(location)
        parent_resource_path = f"projects/{gcp_project_id}/locations/global"

        # 5. Check-and-Create Idempotency Evaluation
        existing_agent = None
        logging.info("Retrieving list of existing agents to evaluate uniqueness...")
        try:
            agents_page = client.list_data_agents(request=geminidataanalytics.ListDataAgentsRequest(parent=parent_resource_path))
            for agent in agents_page:
                if agent.display_name == agent_display_name:
                    existing_agent = agent
                    break
        except GoogleAPICallError as err:
            logging.error(f"API communication failure while reading existing agents list: {err}")
            raise

        # 6. Managing the Agent Lifecycle
        if existing_agent:
            logging.info(f"Match found! An agent exists with resource name: {existing_agent.name}")
            
            if args.force:
                logging.info(f"Force override requested. Deleting agent '{existing_agent.name}'...")
                client.delete_data_agent(request=geminidataanalytics.DeleteDataAgentRequest(name=existing_agent.name))
                logging.info("Soft delete invoked. Pausing 5 seconds for resource cleanup synchronization...")
                time.sleep(5)
                existing_agent = None  # Reset state so creation is triggered below
            else:
                logging.info("Updating existing Conversational Analytics Data Agent configuration inline...")
                updated_agent_payload = geminidataanalytics.DataAgent(
                    name=existing_agent.name,
                    display_name=agent_display_name,
                    description=agent_description,
                    data_analytics_agent=geminidataanalytics.DataAnalyticsAgent(
                        published_context=published_context
                    )
                )
                
                # Create mask detailing fields to patch
                update_mask = field_mask_pb2.FieldMask(paths=[
                    'display_name',
                    'description',
                    'data_analytics_agent.published_context'
                ])
                
                operation = client.update_data_agent(
                    request=geminidataanalytics.UpdateDataAgentRequest(
                        data_agent=updated_agent_payload,
                        update_mask=update_mask
                    )
                )
                logging.info("Initiated configuration update. Waiting for cloud operation completion...")
                while not operation.done():
                    time.sleep(2)
                
                if operation.exception():
                    raise operation.exception()
                    
                logging.info(f"Update completed successfully! Agent version: {operation.result().name}")
                return

        if not existing_agent:
            agent_id = create_valid_resource_id(agent_display_name)
            logging.info(f"Deploying new Conversational Data Agent resource with ID: '{agent_id}'...")
            
            new_agent_payload = geminidataanalytics.DataAgent(
                display_name=agent_display_name,
                description=agent_description,
                data_analytics_agent=geminidataanalytics.DataAnalyticsAgent(
                    published_context=published_context
                )
            )
            
            operation = client.create_data_agent(
                request=geminidataanalytics.CreateDataAgentRequest(
                    parent=parent_resource_path,
                    data_agent_id=agent_id,
                    data_agent=new_agent_payload
                )
            )
            
            logging.info("Agent registration submitted. Monitoring long-running operation progress...")
            while not operation.done():
                time.sleep(2)
                
            if operation.exception():
                raise operation.exception()
                
            logging.info(f"Deployment completed successfully! Created Agent: {operation.result().name}")

    except Exception as e:
        logging.error(f"Execution terminated unexpectedly: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
