# Databricks Notebook — Knowledge Library AI Agent
# Requires: databricks-langchain, langchain
# pip install databricks-langchain langchain
#
# This agent uses the UC-registered MCP tools to answer questions
# about your source/target schemas and ERD documents.

# ── Config ─────────────────────────────────────────────────────────────────────
CATALOG  = "main"
SCHEMA   = "knowledge_library"
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"  # or any DBRX / Claude endpoint
WAREHOUSE_ID = "<your-sql-warehouse-id>"                   # from Databricks SQL → Warehouses

# ── Dependencies ───────────────────────────────────────────────────────────────
# %pip install databricks-langchain langchain --quiet

from databricks_langchain import ChatDatabricks
from databricks_langchain.tools import UCFunctionToolkit
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ── Load MCP tools from Unity Catalog ─────────────────────────────────────────
tool_names = [
    f"{CATALOG}.{SCHEMA}.list_resources",
    f"{CATALOG}.{SCHEMA}.get_resource",
    f"{CATALOG}.{SCHEMA}.search_resources",
    f"{CATALOG}.{SCHEMA}.list_by_category",
]

tools = UCFunctionToolkit(warehouse_id=WAREHOUSE_ID).get_tools(tool_names)
print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")

# ── LLM ────────────────────────────────────────────────────────────────────────
llm = ChatDatabricks(endpoint=LLM_ENDPOINT, temperature=0)

# ── Prompt ─────────────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a data migration assistant with access to a knowledge library "
        "containing source database schemas and target Snowflake ERD documents. "
        "Use the available tools to look up schema details, list resources, and "
        "help plan data migrations. Be concise and precise."
    )),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ── Agent ──────────────────────────────────────────────────────────────────────
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ── Example queries ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        "What source schema resources are available in the knowledge library?",
        "Show me the Contracts ERD details.",
        "What tables exist in the OS source schema?",
    ]
    for q in questions:
        print(f"\nQ: {q}")
        result = agent_executor.invoke({"input": q})
        print(f"A: {result['output']}")
