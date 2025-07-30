from fastapi import FastAPI, Body
from sentence_transformers import SentenceTransformer
from db import add_document, search_similar, create_tables

app = FastAPI()
create_tables()
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.post("/add")
def add_doc(content: str = Body(...)):
    embedding = model.encode(content)
    add_document(content, embedding)
    return {"status": "ok"}

@app.post("/query")
def query_rag(question: str = Body(...)):
    #Embed the question
    query_embedding = model.encode(question)
    
    #Retrieve most similar docs
    docs = search_similar(query_embedding)
    
    # concatenate docs as answer
    answer = " ".join(docs)
    return {"answer": answer, "retrieved_docs": docs}