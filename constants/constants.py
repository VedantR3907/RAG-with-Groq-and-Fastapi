import os
from groq import AsyncGroq
from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from llama_index.llms.groq import Groq
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

load_dotenv()

PINECONE_CLIENT = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
PINECONE_INDEX_NAME = 'groqappchatbot'
PINECONE_NAMESPACE = 'vedant'
GROQ_CLIENT = AsyncGroq(api_key = os.environ.get("GROQ_API_KEY"))
GROQ_CLIENT_LLAMAINDEX = Groq(model="llama3-groq-70b-8192-tool-use-preview", api_key=os.environ.get("GROQ_API_KEY"),)
EMBEDDING_MODEL = FastEmbedEmbeddings()

SIMILARITY_TOP_K = 10
SIMILARITY_CUTOFF = 0.0