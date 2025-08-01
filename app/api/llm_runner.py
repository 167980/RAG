import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
import json



load_dotenv()

client = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="moonshotai/kimi-k2-instruct"  
)

def safe_load_metadata(meta_raw):
    if not meta_raw:
        return None
    if isinstance(meta_raw, dict):
        return meta_raw
    try:
        return json.loads(meta_raw)
    except Exception:
        return None 
    
# def preprocess_query_with_llm(query: str) -> str:
#     """
#     Corrects spelling and rephrases the query using LLM.
#     """
#     prompt = f"Correct any spelling mistakes and rephrase this query naturally if there is no need for change return as it is:\n\n{query}"
#     corrected_query = ask_groq_llm(query=prompt, context_chunks=[])  # pass empty list
#     return corrected_query

# def preprocess_query_with_llm(query: str) -> str:
#     """
#     Corrects spelling and rephrases the query using LLM.
#     Only modifies if there is an actual mistake; else returns original query as is.
#     """
#     prompt = f"""Check the following query for any spelling or grammar mistakes.
# If mistakes exist, correct and rephrase naturally.
# If no mistakes, respond with the exact same query.

# Query:
# {query}
# """
#     corrected_query = ask_groq_llm(query=prompt, context_chunks=[])
    
#     # Normalize for comparison
#     if corrected_query.strip().lower() == query.strip().lower():
#         return query
#     return corrected_query


def preprocess_query_with_llm(query: str) -> str:
    """
    Fixes spelling and grammar only. If query is already correct, returns as is.
    Does NOT check context or add 'not available'.
    """
    grammar_prompt = f"""
Correct only obvious spelling mistakes. Do not rephrase or interpret. Return the corrected query only.

Text: "{query}"
Corrected:
"""
    response = client.invoke(grammar_prompt)
    corrected = response.content.strip()
    

    # Ensure empty or irrelevant responses fall back to original query
    if not corrected:
        return query

    return corrected



def ask_groq_llm(query: str, context_chunks: list[str]) -> str:
   if context_chunks:
    context_text ="\n\n".join([
        f"(Page {row[3]}, Title: {meta.get('title')}, Uploader: {meta.get('uploader')}, "
        f"Uploaded At: {meta.get('uploaded_at')}, File Path: {meta.get('file_path')}):\n{row[1]}"""
        for row in context_chunks
        for meta in [safe_load_metadata(row[4])]
        if meta is not None
    ])
   else:
         context_text=""

   prompt = f""" Give me correct answer 

Context(with page number included):
{context_text} , {context_chunks}


Question: {query}
Answer(include page number references with bullet points):"""

   response = client.invoke(prompt)
   return response.content.strip()  
