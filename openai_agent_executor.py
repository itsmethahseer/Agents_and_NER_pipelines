from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.chat_models import ChatOpenAI
from langchain_community.tools.serpapi.tool import SerpAPIWrapper
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

# --- 1. OpenAI Chat Model ---
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

# --- 2. SerpAPI Search Tool ---
search = SerpAPIWrapper()
search_tool = Tool.from_function(
    func=search.run,
    name="Search",
    description="Useful for answering questions about current events or general knowledge."
)

# --- 3. PDF Tool + FAISS ---
def load_pdf_to_vectorstore(path):
    loader = PyPDFLoader(path)
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(chunks, embeddings)
    return vectordb

vectordb = load_pdf_to_vectorstore("sample.pdf")

def search_pdf(query: str) -> str:
    docs = vectordb.similarity_search(query, k=2)
    return "\n".join([doc.page_content for doc in docs])

pdf_tool = Tool.from_function(
    func=search_pdf,
    name="PDFSearch",
    description="Searches relevant info from a PDF document"
)

# --- 4. Custom Python Function ---
def word_length(word: str) -> int:
    return len(word)

length_tool = Tool.from_function(
    func=word_length,
    name="WordLength",
    description="Returns the number of characters in a word"
)

# --- 5. Create Agent with Tools ---
tools = [search_tool, pdf_tool, length_tool]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# --- 6. Test Agent ---
response = agent.run("Search who is the CEO of Google, then search the PDF for any mention of 'AI', and tell me how many letters are in 'technology'")
print(response)
