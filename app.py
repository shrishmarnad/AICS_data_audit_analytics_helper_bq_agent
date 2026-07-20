#!/usr/bin/env python3
"""
Control Plane Dashboard for BigQuery Conversational Analytics Agent.
Provides web-based configuration, authentication, SQL viewing, and deployment.
Defensively built with Unbuffered Subprocess logging and advanced UX progress.
"""

import os
import sys
import yaml
import subprocess
import webbrowser
import threading
import logging
from flask import Flask, jsonify, request, Response

# Quiet Flask's default console spam to keep the terminal readable
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
PORT = 8080

def get_config_path():
    return os.path.join(os.path.dirname(__file__), 'config.yaml')

def get_instructions_path():
    return os.path.join(os.path.dirname(__file__), 'system_instructions.md')

def get_requirements_path():
    return os.path.join(os.path.dirname(__file__), 'requirements.txt')

def get_default_config() -> dict:
    """Returns the default fallback parameters for configuration schema."""
    return {
        "gcp_project_id": "my-client-gcp-project",
        "gcp_project_number": "123456789012",
        "location": "us-central1",
        "schema_type": "import table schema",
        "dataset_id": "ecommerce_prod",
        "catalog_table_id": "product_catalog",
        "events_table_id": "user_events",
        "agent_display_name": "E-Commerce Quality & Analytics Agent",
        "agent_description": "Analyzes product catalog and user event quality for production syncs.",
        "sql_directory": "./verified_queries",
        "instructions_file": "./system_instructions.md"
    }

def ensure_directories_and_placeholders():
    """Defensively structures folders, baseline queries, and requirements.txt on app startup."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(get_default_config(), f, default_flow_style=False, sort_keys=False)
            
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}

    # Ensure requirements.txt
    req_path = get_requirements_path()
    if not os.path.exists(req_path):
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write("google-cloud-geminidataanalytics\ngoogle-cloud-aiplatform\npyyaml\nflask\n")
        
    sql_parent_dir = config.get('sql_directory', './verified_queries')
    import_dir = os.path.join(sql_parent_dir, "import_table_camelCase_schema")
    export_dir = os.path.join(sql_parent_dir, "export_table_snake_case_schema")
    
    os.makedirs(import_dir, exist_ok=True)
    os.makedirs(export_dir, exist_ok=True)
    
    # Placeholders to populate tables during first launch
    sql1_content = """SELECT
  'default_branch' AS branch_id,
  CURRENT_TIMESTAMP() AS UpdatedTs,
  COUNT(DISTINCT title) AS total_title_count,
  COUNT(DISTINCT id) AS total_products_count,
  'Products with duplicate titles' AS IssueTitle,
  COUNT(DISTINCT id) - COUNT(DISTINCT title) AS AffectedItemsCount
FROM
  `gcp_project_id.retail_dataset.my_catalog` 
WHERE
  type = "PRIMARY"
GROUP BY
  1 
ORDER BY
  1;"""

    sql2_content = """SELECT
  eventType,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(productDetails) > 0) AS has_product_ids,
  COUNTIF(attributionToken IS NOT NULL AND attributionToken != '') AS has_attribution_token,
  COUNTIF(userInfo.userId IS NOT NULL AND userInfo.userId != '') AS has_user_id,
  COUNTIF(sessionId IS NOT NULL AND sessionId != '') AS has_session_id,
  COUNTIF(userInfo.userAgent IS NOT NULL AND userInfo.userAgent != '') AS has_user_agent,
  0 AS has_ip,
  COUNTIF(ARRAY_LENGTH(experimentIds) > 0) AS has_exp_id
FROM
  `gcp_project_id.retail_dataset.my_events`
GROUP BY
  eventType,
  meta;"""

    # Populate Import Directory files
    f1 = os.path.join(import_dir, "catalog_product_duplicate_title_check.sql")
    f2 = os.path.join(import_dir, "user_events_detail_page_view_impression_check.sql")
    if not os.path.exists(f1):
        with open(f1, 'w', encoding='utf-8') as file:
            file.write(sql1_content)
    if not os.path.exists(f2):
        with open(f2, 'w', encoding='utf-8') as file:
            file.write(sql2_content)

    # Populate Export Directory files
    f1_ex = os.path.join(export_dir, "catalog_product_duplicate_title_check.sql")
    f2_ex = os.path.join(export_dir, "user_events_detail_page_view_impression_check.sql")
    if not os.path.exists(f1_ex):
        with open(f1_ex, 'w', encoding='utf-8') as file:
            file.write(sql1_content)
    if not os.path.exists(f2_ex):
        with open(f2_ex, 'w', encoding='utf-8') as file:
            file.write(sql2_content)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCP Data Agent Control Plane</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .code-font { font-family: 'Fira Code', monospace; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 h-screen flex flex-col overflow-hidden select-none">

    <!-- Top Navigation Header -->
    <header class="h-16 flex-none border-b border-slate-800 bg-slate-950 px-6 py-2 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <div class="bg-blue-600 p-2 rounded-lg text-white">
                <i class="fa-solid fa-robot text-xl"></i>
            </div>
            <div>
                <h1 class="text-sm font-bold tracking-tight text-white uppercase">AI Commerce Search : Data Audit and A/B testing helper agent (config and install)</h1>
                <p class="text-xs text-slate-400">created by : <span class="font-semibold text-blue-400">shrishmarnad@google.com</span></p>
            </div>
        </div>
        <div class="flex items-center space-x-4">
            <!-- Authentication Status Widget -->
            <div id="auth-badge" class="flex items-center space-x-2 bg-slate-900 px-4 py-1.5 rounded-full border border-slate-800 text-xs">
                <span class="text-slate-400">gcloud Auth:</span>
                <i id="auth-status-icon" class="fa-solid fa-spinner fa-spin text-amber-500"></i>
                <span id="auth-status-text" class="font-medium text-slate-300">Checking...</span>
            </div>
            <button onclick="triggerGcloudAuth()" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition duration-150 flex items-center space-x-1.5">
                <i class="fa-solid fa-key"></i>
                <span>Authenticate CLI</span>
            </button>
        </div>
    </header>

    <!-- Main Workspace (Flexible layout ensuring everything fits inside 100vh) -->
    <div class="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 overflow-hidden">
        
        <!-- Left Column: Configurations -->
        <section class="flex flex-col min-h-0">
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-xl flex-1 flex flex-col min-h-0">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3 flex-none">
                    <h2 class="text-sm font-bold flex items-center space-x-2 text-white">
                        <i class="fa-solid fa-sliders text-blue-500"></i>
                        <span>Deployment Environment Configs</span>
                    </h2>
                    <!-- Unsaved changes warning indicator -->
                    <span id="unsaved-indicator" class="hidden bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-bold px-2 py-0.5 rounded animate-pulse">
                        ⚠️ UNSAVED CHANGES PRESENT! CLICK SAVE
                    </span>
                </div>
                
                <form id="config-form" class="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
                    <!-- Project Credentials Row -->
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">GCP Project ID</label>
                            <input type="text" name="gcp_project_id" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">Project Number</label>
                            <input type="text" name="gcp_project_number" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                    </div>

                    <!-- Dataset & Tables Row -->
                    <div class="grid grid-cols-3 gap-3">
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">Dataset ID</label>
                            <input type="text" name="dataset_id" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">Catalog Table</label>
                            <input type="text" name="catalog_table_id" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">Events Table</label>
                            <input type="text" name="events_table_id" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                    </div>

                    <!-- Schema Type Strategy (Radio Buttons) -->
                    <div class="border-t border-slate-800/80 pt-2">
                        <label class="block font-semibold text-slate-400 uppercase mb-2">Database Ingestion Architecture (Schema Mode)</label>
                        <div class="space-y-2">
                            <!-- Import Strategy Option -->
                            <label class="flex items-start p-2.5 bg-slate-900/40 border border-slate-800 rounded-lg cursor-pointer hover:border-slate-700 transition">
                                <input type="radio" name="schema_type" value="import table schema" class="mt-0.5 text-blue-600 focus:ring-blue-500 bg-slate-800 border-slate-700">
                                <div class="ml-2.5 text-[11px] leading-relaxed">
                                    <span class="font-semibold text-slate-200">Import Table Schema</span>
                                    <p class="text-slate-400 text-[10px]">
                                        Choose import table schema if you are using the <a href="https://docs.cloud.google.com/retail/docs/reference/rest/v2/projects.locations.catalogs.branches.products" target="_blank" class="text-blue-400 hover:underline font-semibold">catalog</a> and <a href="https://docs.cloud.google.com/retail/docs/reference/rest/v2/projects.locations.catalogs.userEvents" target="_blank" class="text-blue-400 hover:underline font-semibold">user events</a> table in respective VAIS:Commerce prescribed schema for import via BQ. The column names are in camelCase format.
                                    </p>
                                </div>
                            </label>

                            <!-- Export Strategy Option -->
                            <label class="flex items-start p-2.5 bg-slate-900/40 border border-slate-800 rounded-lg cursor-pointer hover:border-slate-700 transition">
                                <input type="radio" name="schema_type" value="export table schema" class="mt-0.5 text-blue-600 focus:ring-blue-500 bg-slate-800 border-slate-700">
                                <div class="ml-2.5 text-[11px] leading-relaxed">
                                    <span class="font-semibold text-slate-200">Export Table Schema</span>
                                    <p class="text-slate-400 text-[10px]">
                                        Choose export table schema, if you are working with vertex commerce catalog in BQ created using the <a href="https://docs.cloud.google.com/retail/docs/export-data-into-bq" target="_blank" class="text-blue-400 hover:underline font-semibold">export to BQ</a> feature. The column names are in snake case format.
                                    </p>
                                </div>
                            </label>
                        </div>
                    </div>

                    <!-- Meta Information Row -->
                    <div class="grid grid-cols-2 gap-3 border-t border-slate-800/80 pt-2">
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">Agent Display Name</label>
                            <input type="text" name="agent_display_name" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                        <div>
                            <label class="block font-semibold text-slate-400 uppercase mb-1">Region Endpoint Location</label>
                            <input type="text" name="location" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100">
                        </div>
                    </div>

                    <div>
                        <label class="block font-semibold text-slate-400 uppercase mb-1">Agent Description</label>
                        <textarea name="agent_description" rows="2" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none text-slate-100 resize-none"></textarea>
                    </div>

                    <!-- Hidden system parameters -->
                    <input type="hidden" name="sql_directory">
                    <input type="hidden" name="instructions_file">
                </form>
                
                <button type="button" id="save-config-btn" onclick="saveConfig()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 rounded-lg transition duration-150 flex items-center justify-center space-x-2 shadow-lg shadow-emerald-950/20 text-xs mt-3 flex-none">
                    <i class="fa-solid fa-floppy-disk"></i>
                    <span>Save Configuration Settings</span>
                </button>
            </div>
        </section>

        <!-- Right Column: System Instructions + Verified Queries (Stacked vertically) -->
        <section class="flex flex-col gap-4 min-h-0">
            <!-- System Instructions Panel -->
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-xl flex-1 flex flex-col min-h-0">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-3 flex-none">
                    <h2 class="text-sm font-bold flex items-center space-x-2 text-white">
                        <i class="fa-solid fa-scroll text-blue-500"></i>
                        <span>system instructions</span>
                    </h2>
                    <span class="text-[10px] text-slate-500 code-font">system_instructions.md</span>
                </div>
                <div class="flex-1 flex flex-col min-h-0">
                    <textarea id="instructions-editor" class="flex-1 w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs code-font text-slate-300 focus:border-blue-500 focus:outline-none resize-none leading-relaxed min-h-0" placeholder="Loading system instructions..."></textarea>
                </div>
                <button onclick="saveInstructions()" class="mt-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2 rounded-lg transition duration-150 flex items-center justify-center space-x-2 text-xs flex-none">
                    <i class="fa-solid fa-pen-to-square"></i>
                    <span>save system instructions</span>
                </button>
            </div>

            <!-- Verified Query File Viewer Panel -->
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 shadow-xl h-52 flex flex-col min-h-0">
                <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-2 flex-none">
                    <h2 class="text-sm font-bold flex items-center space-x-2 text-white">
                        <i class="fa-solid fa-database text-blue-500"></i>
                        <span>Verified Queries Repository</span>
                    </h2>
                    <button onclick="loadVerifiedQueries()" class="text-slate-400 hover:text-white transition">
                        <i class="fa-solid fa-rotate"></i>
                    </button>
                </div>
                <p class="text-[10px] text-slate-400 mb-2 flex-none">Double-click on any file listed below to open a read-only query inspector.</p>
                <div id="queries-list" class="flex-1 overflow-y-auto space-y-1.5 pr-1 min-h-0">
                    <div class="text-slate-500 text-xs text-center py-4">No verified queries populated yet...</div>
                </div>
            </div>
        </section>

    </div>

    <!-- Bottom Panel: Execution Pipeline (Extremely compact to avoid vertical scrolling of page) -->
    <footer class="h-60 flex-none border-t border-slate-800 bg-slate-950 p-4 flex flex-col min-h-0">
        <div class="flex items-center justify-between gap-4 mb-2 flex-none">
            <div>
                <h2 class="text-sm font-bold text-white flex items-center space-x-2">
                    <i class="fa-solid fa-terminal text-emerald-500"></i>
                    <span>Conversational Agent Deployment Pipeline</span>
                </h2>
                <p class="text-[10px] text-slate-400">Initialize Conversational Analytics Data Agent</p>
            </div>
            <div class="flex items-center space-x-3">
                <button id="install-btn" onclick="runInstallation(false)" class="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-lg font-bold transition duration-150 flex items-center space-x-2 shadow-lg shadow-emerald-950/20 text-xs">
                    <i id="install-btn-icon" class="fa-solid fa-bolt text-sm"></i>
                    <span id="install-btn-text">install BQ agent</span>
                </button>
                <button id="force-install-btn" onclick="runInstallation(true)" class="bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-bold transition duration-150 flex items-center space-x-2 shadow-lg shadow-red-950/20 text-xs">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <span>Force Recreate</span>
                </button>
            </div>
        </div>

        <!-- Terminal-like Console Window -->
        <div class="flex-1 min-h-0 bg-slate-900 border border-slate-800 rounded-lg overflow-hidden shadow-inner flex flex-col">
            <div class="bg-slate-950 px-3 py-1 flex-none border-b border-slate-800 flex items-center justify-between">
                <div class="flex space-x-1">
                    <span class="w-2 h-2 rounded-full bg-red-500/80 inline-block"></span>
                    <span class="w-2 h-2 rounded-full bg-yellow-500/80 inline-block"></span>
                    <span class="w-2 h-2 rounded-full bg-green-500/80 inline-block"></span>
                </div>
                <span class="text-[10px] text-slate-500 code-font">stdout/stderr streaming logs</span>
            </div>
            <pre id="terminal" class="flex-1 p-3 overflow-y-auto text-[11px] code-font text-slate-300 leading-relaxed bg-slate-950/40 select-text min-h-0">Ready to deploy. Click "install BQ agent" above to run deploy_agent.py.</pre>
        </div>
        
        <!-- Connection Warning Caution Callout -->
        <div class="mt-2 text-[10px] text-amber-400 bg-amber-950/40 border border-amber-500/20 px-3 py-1.5 rounded-lg flex items-center space-x-2 flex-none">
            <i class="fa-solid fa-circle-exclamation text-amber-400"></i>
            <span><strong>Caution:</strong> The connection can break, but the registration continues on Google Cloud in the background. Please access the BQ agent console directly after 5-10mins if the stream disconnects.</span>
        </div>
    </footer>

    <!-- Query Inspector Modal -->
    <div id="inspector-modal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center hidden opacity-0 transition-opacity duration-200">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-3xl rounded-xl shadow-2xl flex flex-col max-h-[80vh] m-4 overflow-hidden transform scale-95 transition-transform duration-200">
            <div class="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center justify-between flex-none">
                <div>
                    <h3 id="modal-title" class="text-md font-bold text-white">Query Viewer</h3>
                    <p id="modal-sub" class="text-xs text-slate-400 mt-1">Processed SQL</p>
                </div>
                <button onclick="closeInspectorModal()" class="text-slate-400 hover:text-white transition bg-slate-800/40 p-1.5 rounded-lg">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>
            <div class="p-6 overflow-y-auto bg-slate-950 flex-1 min-h-0">
                <pre id="modal-code" class="code-font text-xs text-blue-400 leading-relaxed select-text"></pre>
            </div>
        </div>
    </div>

    <!-- Interface JavaScript Logics -->
    <script>
        // Track unsaved configuration changes state
        let hasUnsavedChanges = false;

        document.addEventListener('DOMContentLoaded', () => {
            try { loadConfig(); } catch(e) { console.error("Config loader failed:", e); }
            try { loadInstructions(); } catch(e) { console.error("Instructions loader failed:", e); }
            try { checkAuthStatus(); } catch(e) { console.error("CLI authentication verify failed:", e); }

            // Attach input event listeners to the configurations form to track unsaved changes
            const configForm = document.getElementById('config-form');
            configForm.addEventListener('input', () => {
                setUnsavedChanges(true);
            });
        });

        function setUnsavedChanges(changed) {
            hasUnsavedChanges = changed;
            const indicator = document.getElementById('unsaved-indicator');
            const saveBtn = document.getElementById('save-config-btn');
            if (changed) {
                indicator.classList.remove('hidden');
                saveBtn.classList.remove('bg-emerald-600', 'hover:bg-emerald-500');
                saveBtn.classList.add('bg-amber-600', 'hover:bg-amber-500', 'animate-pulse');
            } else {
                indicator.classList.add('hidden');
                saveBtn.classList.remove('bg-amber-600', 'hover:bg-amber-500', 'animate-pulse');
                saveBtn.classList.add('bg-emerald-600', 'hover:bg-emerald-500');
            }
            
            // Re-normalize the install button if configurations are updated
            resetInstallButtonState();
        }

        function resetInstallButtonState() {
            const installBtn = document.getElementById('install-btn');
            const icon = document.getElementById('install-btn-icon');
            const text = document.getElementById('install-btn-text');
            
            installBtn.disabled = false;
            installBtn.className = "bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-lg font-bold transition duration-150 flex items-center space-x-2 shadow-lg shadow-emerald-950/20 text-xs";
            icon.className = "fa-solid fa-bolt text-sm";
            text.innerText = "install BQ agent";
        }

        function checkAuthStatus() {
            const icon = document.getElementById('auth-status-icon');
            const text = document.getElementById('auth-status-text');
            
            fetch('/api/auth-status')
                .then(r => r.json())
                .then(data => {
                    icon.className = 'fa-solid';
                    icon.classList.remove('fa-spin');
                    if (data.authenticated) {
                        icon.classList.add('fa-circle-check', 'text-green-500');
                        text.innerText = 'Authenticated (' + data.project + ')';
                    } else {
                        icon.classList.add('fa-circle-xmark', 'text-red-500');
                        text.innerText = 'Disconnected';
                    }
                }).catch(err => {
                    console.error('Error during auth validation call:', err);
                    icon.className = 'fa-solid fa-circle-xmark text-red-500';
                    text.innerText = 'CLI Check Failure';
                });
        }

        function triggerGcloudAuth() {
            const icon = document.getElementById('auth-status-icon');
            const text = document.getElementById('auth-status-text');
            icon.className = 'fa-solid fa-spinner fa-spin text-amber-500';
            text.innerText = 'Invoking login browser...';
            
            fetch('/api/authenticate', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    setTimeout(checkAuthStatus, 5000);
                });
        }

        function loadConfig() {
            fetch('/api/config')
                .then(r => r.json())
                .then(data => {
                    const form = document.getElementById('config-form');
                    for (const key in data) {
                        const input = form.elements[key];
                        if (input) {
                            if (input.type === 'radio') {
                                const radio = form.querySelector('input[name="' + key + '"][value="' + data[key] + '"]');
                                if (radio) {
                                    radio.checked = true;
                                }
                            } else {
                                input.value = data[key];
                            }
                        }
                    }
                    setUnsavedChanges(false);
                    loadVerifiedQueries();
                });
        }

        function saveConfig() {
            const form = document.getElementById('config-form');
            const data = {};
            const formData = new FormData(form);
            formData.forEach((val, key) => {
                data[key] = val;
            });

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    alert('Configurations written successfully!');
                    setUnsavedChanges(false);
                    loadVerifiedQueries();
                } else {
                    alert('Error writing configs: ' + res.error);
                }
            });
        }

        // Add automatic listener to radio buttons as well for dynamic change tracking
        document.querySelectorAll('input[type="radio"][name="schema_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                setUnsavedChanges(true);
            });
        });

        function loadInstructions() {
            fetch('/api/instructions')
                .then(r => r.text())
                .then(text => {
                    document.getElementById('instructions-editor').value = text;
                });
        }

        function saveInstructions() {
            const text = document.getElementById('instructions-editor').value;
            fetch('/api/instructions', {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain' },
                body: text
            })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    alert('System Instructions saved successfully!');
                } else {
                    alert('Error saving instructions: ' + res.error);
                }
            });
        }

        function loadVerifiedQueries() {
            fetch('/api/queries')
                .then(r => r.json())
                .then(files => {
                    const listContainer = document.getElementById('queries-list');
                    listContainer.innerHTML = '';
                    if (!files || files.length === 0) {
                        listContainer.innerHTML = '<div class="text-slate-500 text-xs text-center py-4">No verified queries matched this schema choice.</div>';
                        return;
                    }
                    files.forEach(file => {
                        const item = document.createElement('div');
                        item.className = 'bg-slate-900 border border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-800/20 rounded-lg px-3 py-2 flex items-center justify-between cursor-pointer transition select-none';
                        item.innerHTML = `
                            <div class="flex items-center space-x-2">
                                <i class="fa-solid fa-file-code text-blue-400 text-xs"></i>
                                <span class="text-[11px] font-semibold text-slate-300 code-font">${file}</span>
                            </div>
                            <span class="text-slate-500 text-[9px] uppercase border border-slate-800/80 rounded px-1.5 py-0.5">Double Click to View</span>
                        `;
                        item.ondblclick = () => openQueryInspector(file);
                        listContainer.appendChild(item);
                    });
                });
        }

        function openQueryInspector(filename) {
            fetch('/api/query-content?filename=' + encodeURIComponent(filename))
                .then(r => r.json())
                .then(data => {
                    document.getElementById('modal-title').innerText = filename;
                    document.getElementById('modal-sub').innerText = 'Processed SQL';
                    document.getElementById('modal-code').innerText = data.content;
                    
                    const modal = document.getElementById('inspector-modal');
                    modal.classList.remove('hidden');
                    setTimeout(() => {
                        modal.classList.remove('opacity-0');
                        modal.querySelector('.transform').classList.remove('scale-95');
                    }, 10);
                });
        }

        function closeInspectorModal() {
            const modal = document.getElementById('inspector-modal');
            modal.classList.add('opacity-0');
            modal.querySelector('.transform').classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 200);
        }

        function runInstallation(force = false) {
            const terminal = document.getElementById('terminal');
            const installBtn = document.getElementById('install-btn');
            const forceBtn = document.getElementById('force-install-btn');
            const installBtnIcon = document.getElementById('install-btn-icon');
            const installBtnText = document.getElementById('install-btn-text');
            
            // 1. Initial State UI Update
            terminal.innerHTML = 'Starting BigQuery Conversational Analytics deployment execution sequence...\\n';
            installBtn.disabled = true;
            forceBtn.disabled = true;
            installBtn.className = "bg-slate-800 border border-slate-700 text-slate-400 px-5 py-2 rounded-lg font-bold transition duration-150 flex items-center space-x-2 text-xs";
            forceBtn.classList.add('opacity-50');
            
            installBtnIcon.className = "fa-solid fa-spinner fa-spin text-sm text-blue-500";
            installBtnText.innerText = "Installing BQ Agent...";

            const eventSource = new EventSource('/api/deploy?force=' + force);
            
            eventSource.onmessage = function(event) {
                if (event.data === "[DONE]") {
                    eventSource.close();
                    terminal.innerHTML += '\\n------------------------------------------\\n[SUCCESS] Execution complete. Agent successfully deployed!';
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    // 2. Success State UI Update - Permanent Green Tick
                    installBtn.disabled = true; // Stay completed
                    forceBtn.disabled = false;
                    forceBtn.classList.remove('opacity-50');
                    
                    installBtn.className = "bg-emerald-950 border border-emerald-500/30 text-emerald-400 px-5 py-2 rounded-lg font-bold transition duration-150 flex items-center space-x-2 text-xs";
                    installBtnIcon.className = "fa-solid fa-circle-check text-sm text-green-400";
                    installBtnText.innerText = "Deployed Successfully!";
                    
                    checkAuthStatus();
                } else {
                    terminal.innerHTML += event.data + '\\n';
                    terminal.scrollTop = terminal.scrollHeight;
                }
            };

            eventSource.onerror = function(err) {
                eventSource.close();
                terminal.innerHTML += '\\n[Error]: Terminal socket connection interrupted.\\nIf deploying on standard schedules, ignore this. Your operation has been successfully submitted to Google Cloud.';
                terminal.scrollTop = terminal.scrollHeight;
                
                // Reset button so they can retry
                resetInstallButtonState();
                forceBtn.disabled = false;
                forceBtn.classList.remove('opacity-50');
            };
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    config_path = get_config_path()
    if request.method == 'GET':
        if not os.path.exists(config_path):
            default_conf = get_default_config()
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_conf, f, default_flow_style=False, sort_keys=False)
            return jsonify(default_conf)
            
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception:
                data = {}
        
        # Merge missing properties dynamically to ensure no null value errors
        default_conf = get_default_config()
        for k, v in default_conf.items():
            if k not in data or data[k] is None:
                data[k] = v
        return jsonify(data)
    else:
        try:
            new_data = request.json
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_data, f, default_flow_style=False, sort_keys=False)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/instructions', methods=['GET', 'POST'])
def api_instructions():
    instructions_path = get_instructions_path()
    if request.method == 'GET':
        if not os.path.exists(instructions_path):
            placeholder = "### Data Source Mapping and Table Usage Rules\\n\\n*   **Always use the `Catalog Product` table**..."
            with open(instructions_path, 'w', encoding='utf-8') as f:
                f.write(placeholder)
            return placeholder, 200, {'Content-Type': 'text/plain'}
        with open(instructions_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    else:
        try:
            text = request.data.decode('utf-8')
            with open(instructions_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth-status', methods=['GET'])
def api_auth_status():
    """Validates local gcloud shell configurations, avoiding path resolution errors."""
    try:
        use_shell = os.name == 'nt'  # True on Windows systems
        
        # Pull selected project name
        proj_result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            capture_output=True, text=True, shell=use_shell, timeout=3
        )
        current_project = proj_result.stdout.strip() if proj_result.returncode == 0 else "Unset"
        
        # Test CLI authentication with token verify
        adc_test = subprocess.run(
            ['gcloud', 'auth', 'application-default', 'print-access-token'],
            capture_output=True, text=True, shell=use_shell, timeout=3
        )
        authenticated = (adc_test.returncode == 0)
        return jsonify({
            "authenticated": authenticated,
            "project": current_project if current_project else "Unset"
        })
    except Exception as e:
        # Prevent exceptions from returning 500
        return jsonify({
            "authenticated": False,
            "project": "Unset",
            "error": str(e)
        })

@app.route('/api/authenticate', methods=['POST'])
def api_authenticate():
    """Triggers standard credential flow in background thread."""
    def run_auth():
        use_shell = os.name == 'nt'
        subprocess.run(['gcloud', 'auth', 'application-default', 'login'], shell=use_shell)
        
    thread = threading.Thread(target=run_auth)
    thread.start()
    return jsonify({"initiated": True})

@app.route('/api/queries', methods=['GET'])
def api_queries():
    """Scans and indexes SQL source assets."""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return jsonify([])
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
        
    schema_type = config.get('schema_type', 'import table schema').lower()
    sql_parent_dir = config.get('sql_directory', './verified_queries')
    
    subfolder = "import_table_camelCase_schema" if "import" in schema_type else "export_table_snake_case_schema"
    target_dir = os.path.join(sql_parent_dir, subfolder)
    
    if not os.path.exists(target_dir):
        return jsonify([])
        
    files = [f for f in os.listdir(target_dir) if f.endswith('.sql')]
    return jsonify(sorted(files))

@app.route('/api/query-content', methods=['GET'])
def api_query_content():
    """Fetches clean SQL data for read-only preview."""
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"error": "filename is required"}), 400
        
    config_path = get_config_path()
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
        
    schema_type = config.get('schema_type', 'import table schema').lower()
    sql_parent_dir = config.get('sql_directory', './verified_queries')
    
    subfolder = "import_table_camelCase_schema" if "import" in schema_type else "export_table_snake_case_schema"
    file_path = os.path.join(sql_parent_dir, subfolder, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return jsonify({"content": f.read()})

@app.route('/api/deploy', methods=['GET'])
def api_deploy():
    """Runs deployment script and pipes stdout streams."""
    force = request.args.get('force', 'false').lower() == 'true'
    
    def generate():
        use_shell = os.name == 'nt'
        # Force Python's stdout to be completely unbuffered inside subprocesses
        unbuffered_env = dict(os.environ)
        unbuffered_env["PYTHONUNBUFFERED"] = "1"
        
        # Step 1: Pre-installation check for Pip dependencies
        yield "data: [PIP] Verifying and installing Python dependencies from requirements.txt...\\n\\n"
        pip_cmd = [sys.executable, '-u', '-m', 'pip', 'install', '-r', 'requirements.txt']
        process_pip = subprocess.Popen(
            pip_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=use_shell,
            env=unbuffered_env
        )
        while True:
            line = process_pip.stdout.readline()
            if not line and process_pip.poll() is not None:
                break
            if line:
                yield f"data: {line.strip()}\\n\\n"
                
        if process_pip.returncode != 0:
            yield "data: [Warning] Dependency pre-installation returned non-zero code. Attempting to proceed...\\n\\n"
        else:
            yield "data: [PIP] Dependency verification successful! Starting deploy_agent.py...\\n\\n"

        # Step 2: Trigger deploy_agent.py
        cmd = [sys.executable, '-u', 'deploy_agent.py', '--config', 'config.yaml']
        if force:
            cmd.append('--force')
            
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=use_shell,
            env=unbuffered_env
        )
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                yield f"data: {line.strip()}\\n\\n"
                
        yield "data: [DONE]\\n\\n"
        
    return Response(generate(), mimetype='text/event-stream')

def start_server():
    ensure_directories_and_placeholders()
    webbrowser.open(f'http://localhost:{PORT}')
    # Set threaded=True to ensure SSE log generation is non-blocking
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)

if __name__ == '__main__':
    start_server()
