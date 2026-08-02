from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import our custom services
from github_service import GitHubService
from ai_service import AIService

app = FastAPI(title="Git-Chat AI Backend")

# Enable CORS so our frontend can securely talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development; narrow this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Models ---
class QueryRequest(BaseModel):
    repo_name: str
    question: str
    openai_key: str

# --- Endpoints ---

@app.get("/api/repositories")
def get_repositories(x_github_token: Optional[str] = Header(None, alias="X-GitHub-Token")):
    """
    Fetches the user's GitHub repositories using the provided token passed via headers.
    """
    if not x_github_token:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Token header.")
    
    try:
        gh_service = GitHubService(token=x_github_token)
        repos = gh_service.get_user_repositories()
        return {"repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/chat")
def chat_with_repo(request: QueryRequest, x_github_token: Optional[str] = Header(None, alias="X-GitHub-Token")):
    """
    Ingests repository context and queries the AI model with the user's question.
    """
    if not x_github_token:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Token header.")
    
    try:
        # 1. Initialize the GitHub Service and pull the context
        gh_service = GitHubService(token=x_github_token)
        repo_context = gh_service.get_repo_context(request.repo_name)
        
        if not repo_context.strip():
            raise HTTPException(status_code=400, detail="The selected repository appears to be empty or contains no readable text files.")
        
        # 2. Pass that context along to the AI Service
        ai_service = AIService(api_key=request.openai_key)
        ai_response = ai_service.query_repo(repo_context=repo_context, user_question=request.question)
        
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    """Simple status check endpoint."""
    return {"status": "healthy"}