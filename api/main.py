"""
Aplicação principal FastAPI
Configuração e inicialização da API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from .routes import router

# Criar aplicação FastAPI
app = FastAPI(
    title="Hiperfaturômetro API",
    description="API para análise de licitações públicas suspeitas - Medindo a Corrupção em Licitações Públicas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(router, prefix="/api", tags=["Hiperfaturômetro"])

# Handler de exceções globais
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erro interno do servidor",
            "data": None
        }
    )

# Endpoint de informações da API
@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Hiperfaturômetro API",
        "description": "API para análise de licitações públicas suspeitas",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "statistics": "/api/statistics",
            "cases": "/api/cases",
            "case_detail": "/api/cases/{case_id}",
            "cases_by_orgao": "/api/cases/by-orgao",
            "cartel_types": "/api/cartel-types",
            "breaking_news": "/api/breaking-news",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
