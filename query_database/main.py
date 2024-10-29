import sys
from typing import List
sys.path.append('../')
from constants.constants import (GROQ_CLIENT_LLAMAINDEX, 
                       PINECONE_CLIENT, PINECONE_INDEX_NAME, PINECONE_NAMESPACE, 
                       SIMILARITY_TOP_K, SIMILARITY_CUTOFF,
                       EMBEDDING_MODEL)
from constants.prompts import SYSTEM_PROMPT
from llama_index.core import Settings, VectorStoreIndex, get_response_synthesizer  # noqa: F401
from llama_index.core.retrievers import VectorIndexRetriever
# from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.chat_engine.context import ContextChatEngine
from llama_index.core.llms import ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
import asyncio


pinecone_client = PINECONE_CLIENT
pc_indexname = PINECONE_INDEX_NAME
pc_namespace = PINECONE_NAMESPACE

Settings.embed_model=EMBEDDING_MODEL
Settings.llm = GROQ_CLIENT_LLAMAINDEX

def pinecone_vectorstore():
    index = pinecone_client.Index(pc_indexname)
    pinecone_vector_store = PineconeVectorStore(pinecone_index=index, namespace=pc_namespace,)

    return VectorStoreIndex.from_vector_store(vector_store=pinecone_vector_store)

async def llamaindex_chatbot(query: str, chat_history: List):

    vector_index_retriever = VectorIndexRetriever(
    index=pinecone_vectorstore(),
    namespace=pc_namespace,
    similarity_top_k=SIMILARITY_TOP_K)
    # response_synthesizer = get_response_synthesizer(response_mode='refine', )
    postprocessors = [SimilarityPostprocessor(similarity_cutoff=SIMILARITY_CUTOFF)]

    # query_engine = RetrieverQueryEngine(
    #     retriever=vector_index_retriever,
    #     response_synthesizer=response_synthesizer,
    #     node_postprocessors=postprocessors,
    # )
    chatengine = ContextChatEngine(
        retriever=vector_index_retriever,
        node_postprocessors=postprocessors,
        prefix_messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)],
        llm = Settings.llm,
        memory=ChatMemoryBuffer.from_defaults(chat_history = chat_history, token_limit=5000))
    
    chat_response = await chatengine.achat(query)

    return str(chat_response)

if __name__ == "__main__":
    asyncio.run(llamaindex_chatbot("What was my previous question", []))