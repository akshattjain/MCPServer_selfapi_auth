from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

from src.configs.db import init_db, validate_api_key
from src.routes.admin import router as admin_router
from src.routes.mcp import mpc

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Make sure the tables are created if not already created
    init_db()
    yield
    # Database connection is closed automatically by SQLAlchemy session lifecycle.

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    """
    Middleware to intercept incoming HTTP requests and validate API key.
    
    Excludes the route `/admin/generate-key` which is used to generate keys.
    """
    path = request.url.path
    
    # 1. Skip authentication for public endpoints
    if path == "/admin/generate-key":
        return await call_next(request)
        
    # 2. Skip authentication for CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)
        
    # 3. Skip authentication for MCP message posts with valid session_id.
    # FastMCP's SSE transport internally validates the session_id UUID.
    # The session_id can only be obtained via a successful /mcp/sse connection.
    if path.rstrip("/") == "/mcp/messages" and request.query_params.get("session_id"):
        return await call_next(request)
        
    # 4. Extract the API key from Headers or Query Parameters
    api_key = None
    
    # Header check
    x_api_key = request.headers.get("x-api-key")
    authorization = request.headers.get("authorization")
    
    if x_api_key:
        api_key = x_api_key
    elif authorization:
        if authorization.lower().startswith("bearer "):
            api_key = authorization[7:]
        else:
            api_key = authorization
            
    # Query parameter check (fallback)
    if not api_key:
        api_key = request.query_params.get("api_key")
        
    # 5. Validate key against the database
    if api_key:
        user = await validate_api_key(api_key)
        if user:
            # Add user details to request state
            request.state.user = user
            return await call_next(request)
            
    # 6. Reject if not authenticated
    return JSONResponse(
        {"detail": "Unauthorized: Invalid or missing X-API-Key"}, 
        status_code=401
    )

# Mount the routes
app.include_router(admin_router)
app.mount("/mcp", mpc.sse_app())