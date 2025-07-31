from fastapi import FastAPI, HTTPException, Body
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import requests
import json
import os
from db import add_document, search_similar, create_tables, get_documents_count


class DocumentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Document content")

class DocumentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Updated document content")

class DocumentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to search for")
    k: Optional[int] = Field(default=3, ge=1, le=20, description="Number of documents to retrieve")
    use_local_llm: Optional[bool] = Field(default=True, description="Use local LLM for answer generation")

class QueryResponse(BaseModel):
    answer: str
    retrieved_docs: List[str]
    document_count: int
    search_method: str
    generation_method: str

class HealthResponse(BaseModel):
    status: str
    total_documents: int
    model_loaded: bool
    database_type: str
    local_llm_available: bool
    embedding_model: str
    ollama_url: str
    deployment_mode: str


class DockerLLMClient:
    def __init__(self, base_url: str = None, model: str = "llama3.2:1b"):
        
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model
        self.deployment_mode = "docker" if "ollama:" in self.base_url else "host"
    
    def is_available(self) -> bool:
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"LLM availability check failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        
        try:
            if not self.is_available():
                return []
            
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except:
            return []
    
    def ensure_model_available(self) -> bool:
        
        available_models = self.get_available_models()
        
        if self.model in available_models:
            return True
        
        
        try:
            print(f"Attempting to pull model: {self.model}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=300  
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to pull model {self.model}: {e}")
            return False
    
    def generate_answer(self, context: str, question: str) -> str:
        
        if not self.is_available():
            return f"LLM server not available at {self.base_url}. Please ensure Ollama Docker container is running."
        
        
        if not self.ensure_model_available():
            available = self.get_available_models()
            return f"Model '{self.model}' not available. Available models: {available}"
        
        prompt = f"""Based on the following context, answer the question concisely and accurately.

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_ctx": 2048,  # Context window
                        "num_predict": 300  # Max response tokens
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                return f"Error generating response: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Request timed out. The model might be busy or the context is too long."
        except Exception as e:
            return f"Error connecting to LLM server: {str(e)}"


app = FastAPI(title="RAG API", version="3.1.0")


create_tables()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

llm_client = DockerLLMClient()

@app.get("/", response_model=dict)
def root():
    return {
        "message": "RAG API", 
        "version": "3.1.0",
        "documentation": "/docs",
        "total_documents": get_documents_count(),
        "llm_status": {
            "url": llm_client.base_url,
            "available": llm_client.is_available(),
            "deployment": llm_client.deployment_mode,
            "configured_model": llm_client.model
        },
        "endpoints": [
            "/add - Add documents",
            "/query - Query with optional LLM generation", 
            "/health - System health",
            "/llm-status - Detailed LLM info",
            "/models - Available models"
        ],
        "docker_commands": {
            "start_ollama": "docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama",
            "pull_model": "docker exec -it ollama ollama pull llama3.2:1b",
            "full_stack": "docker-compose up -d"
        }
    }
    
@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        total_documents=get_documents_count(),  
        model_loaded=True,
        database_type="PostgreSQL with pgvector",
        local_llm_available=llm_client.is_available(),
        embedding_model="all-MiniLM-L6-v2",
        ollama_url=llm_client.base_url,
        deployment_mode=llm_client.deployment_mode
    )

@app.get("/models")
def get_models():
    return {
        "configured_model": llm_client.model,
        "available_models": llm_client.get_available_models(),
        "server_available": llm_client.is_available(),
        "server_url": llm_client.base_url
    }

@app.post("/add")
def add_document_modern(document: DocumentCreate):
    try:
        embedding = embedding_model.encode(document.content)
        add_document(document.content, embedding)
        return {
            "status": "success",
            "message": "Document added successfully",
            "content": document.content[:100] + "..." if len(document.content) > 100 else document.content,
            "embedding_model": "all-MiniLM-L6-v2"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@app.post("/query", response_model=QueryResponse)
def query_documents_modern(query: QueryRequest):
    try:
        query_embedding = embedding_model.encode(query.question)
        docs = search_similar(query_embedding, k=query.k)  
        
        if not docs:
            return QueryResponse(
                answer="No relevant documents found.",
                retrieved_docs=[],
                document_count=0,
                search_method="vector_similarity",
                generation_method="none"
            )
        
        doc_contents = [doc.content for doc in docs]
        context = "\n\n".join(doc_contents)
        
        if query.use_local_llm and llm_client.is_available():
            answer = llm_client.generate_answer(context, query.question)
            generation_method = f"docker_llm_{llm_client.model}"
        else:
            answer = f"Based on the retrieved documents: {context[:500]}..."
            generation_method = "simple_concatenation"
        
        return QueryResponse(
            answer=answer,
            retrieved_docs=doc_contents,
            document_count=len(docs),
            search_method="vector_similarity",
            generation_method=generation_method
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

@app.get("/llm-status")
def llm_status():
    is_available = llm_client.is_available()
    available_models = llm_client.get_available_models()
    
    status = {
        "server_running": is_available,
        "server_url": llm_client.base_url,
        "deployment_mode": llm_client.deployment_mode,
        "configured_model": llm_client.model,
        "available_models": available_models,
        "model_ready": llm_client.model in available_models if available_models else False
    }
    
    if not is_available:
        status["troubleshooting"] = {
            "docker_check": "docker ps | grep ollama",
            "docker_logs": "docker logs ollama",
            "restart_container": "docker restart ollama",
            "start_new": "docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama"
        }
    elif not available_models:
        status["next_steps"] = [
            f"docker exec -it ollama ollama pull {llm_client.model}",
            "docker exec -it ollama ollama list"
        ]
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
