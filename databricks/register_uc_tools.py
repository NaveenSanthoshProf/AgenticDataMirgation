# Databricks Notebook
# Run this once to register the Knowledge Library MCP server as Unity Catalog AI functions.
# Replace APP_URL with your deployed Databricks App URL.
# Replace CATALOG and SCHEMA with your target Unity Catalog namespace.

APP_URL   = "https://<your-databricks-app-url>"   # e.g. https://my-app.azuredatabricks.net
CATALOG   = "main"
SCHEMA    = "knowledge_library"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

# ── Tool 1: list all resources ─────────────────────────────────────────────────
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.list_resources()
RETURNS STRING
COMMENT 'Returns a JSON list of all available knowledge library resources (schemas, ERDs).'
LANGUAGE PYTHON
AS $$
  import urllib.request
  with urllib.request.urlopen("{APP_URL}/api/v1/resources") as r:
    return r.read().decode()
$$
""")

# ── Tool 2: get a single resource by ID ────────────────────────────────────────
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.get_resource(resource_id STRING)
RETURNS STRING
COMMENT 'Returns metadata and content for a knowledge library resource by its ID.'
LANGUAGE PYTHON
AS $$
  import urllib.request
  url = "{APP_URL}/api/v1/resources/" + resource_id + "?content=true"
  with urllib.request.urlopen(url) as r:
    return r.read().decode()
$$
""")

# ── Tool 3: search resources ───────────────────────────────────────────────────
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.search_resources(query STRING)
RETURNS STRING
COMMENT 'Searches knowledge library resources by name or ID keyword.'
LANGUAGE PYTHON
AS $$
  import urllib.request
  url = "{APP_URL}/api/v1/search?q=" + query
  with urllib.request.urlopen(url) as r:
    return r.read().decode()
$$
""")

# ── Tool 4: list by category ───────────────────────────────────────────────────
spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.list_by_category(category STRING)
RETURNS STRING
COMMENT 'Lists knowledge library resources filtered by category (e.g. source_schema, target_schema).'
LANGUAGE PYTHON
AS $$
  import urllib.request
  url = "{APP_URL}/api/v1/resources/category/" + category
  with urllib.request.urlopen(url) as r:
    return r.read().decode()
$$
""")

print(f"Registered 4 UC functions under {CATALOG}.{SCHEMA}")
