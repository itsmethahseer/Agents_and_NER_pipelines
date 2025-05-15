from langchain_ollama import ChatOllama
from langchain.agents import tool, AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import DuckDuckGoSearchRun
from langchain.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import create_sql_agent
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import SQLDatabaseToolkit
import os

# --- Step 1: Initialize the LLM ---
llm = ChatOllama(model="llama3.1", temperature=0, verbose=True)

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

# Web search tool using DuckDuckGo
web_search_tool = DuckDuckGoSearchRun(name="web_search")

# FAISS tool setup
def load_faiss_tool():
    # Sample FAISS setup (replace with your actual documents)
    docs = TextLoader("details.txt").load()  # Load text file
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs_split = text_splitter.split_documents(docs)
    
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    db = FAISS.from_documents(docs_split, embedding)
    
    @tool
    def faiss_search(query: str) -> str:
        """Search relevant documents using FAISS vector search."""
        results = db.similarity_search(query, k=2)
        return "\n".join([doc.page_content for doc in results])

    return faiss_search

faiss_tool = load_faiss_tool()

def load_sql_tool():
    db = SQLDatabase.from_uri("sqlite:///shop.db")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)
    @tool
    def sql_query(question: str) -> str:
        """Answer questions about shop orders and inventory using the database."""
        try:
            result = sql_agent.run(question)
            return result
        except Exception as e:
            return f"SQL error: {e}"

    return sql_query

sql_tool = load_sql_tool()

tools = [get_word_length, web_search_tool, faiss_tool,sql_tool]

# --- Step 3: Prompt and Agent ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a very powerful assistant."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_tools(tools)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

# --- Step 4: Agent Executor ---
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Step 5: Run Agent ---
query = "Search for the capital of Germany, length of 'education', content about mistral model from document, and get the status of order ID 1 from the shop database."

result = agent_executor.invoke({"input": query})

if result:
    print(f"[Output] --> {result['output']}")
else:
    print("No result.")
