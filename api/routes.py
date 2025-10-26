"""
Rotas da API FastAPI
Define todos os endpoints da aplicação
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from .models import (
    CaseModel, StatisticsModel, CaseByOrgaoModel, 
    BreakingNewsModel, CaseFilters, APIResponse, RiskLevel, PriorityLevel
)
from .data_service import DataService

# Inicializar roteador
router = APIRouter()

# Inicializar serviço de dados
data_service = DataService()

@router.get("/", response_model=APIResponse)
async def root():
    """Endpoint raiz da API"""
    return APIResponse(
        success=True,
        message="Hiperfaturômetro API - Medindo a Corrupção em Licitações Públicas",
        data={
            "version": "1.0.0",
            "description": "API para análise de licitações públicas suspeitas",
            "endpoints": {
                "statistics": "/api/statistics",
                "cases": "/api/cases",
                "case_detail": "/api/cases/{case_id}",
                "cases_by_orgao": "/api/cases/by-orgao",
                "cartel_types": "/api/cartel-types"
            }
        }
    )

@router.get("/statistics", response_model=APIResponse)
async def get_statistics():
    """Retorna estatísticas gerais do sistema"""
    try:
        stats = data_service.get_estatisticas()
        return APIResponse(
            success=True,
            message="Estatísticas recuperadas com sucesso",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

@router.get("/cases", response_model=APIResponse)
async def get_cases(
    limit: int = Query(default=10, ge=1, le=100, description="Número máximo de casos a retornar"),
    risk_level: Optional[RiskLevel] = Query(default=None, description="Filtrar por nível de risco"),
    orgao: Optional[str] = Query(default=None, description="Filtrar por órgão"),
    priority_level: Optional[PriorityLevel] = Query(default=None, description="Filtrar por nível de prioridade")
):
    """Retorna lista de casos com filtros opcionais"""
    try:
        # Aplicar filtros
        filtro_risco = risk_level.value if risk_level else None
        
        cases = data_service.get_noticias(limit=limit, filtro_risco=filtro_risco)
        
        # Filtros adicionais
        if orgao:
            cases = [case for case in cases if orgao.lower() in case.get('orgao', '').lower()]
        
        return APIResponse(
            success=True,
            message=f"Recuperados {len(cases)} casos",
            data=cases
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar casos: {str(e)}")

@router.get("/cases/{case_id}", response_model=APIResponse)
async def get_case_detail(case_id: str):
    """Retorna detalhes de um caso específico"""
    try:
        case = data_service.get_caso_detalhado(case_id)
        
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")
        
        return APIResponse(
            success=True,
            message="Caso recuperado com sucesso",
            data=case
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar caso: {str(e)}")

@router.get("/cases/by-orgao", response_model=APIResponse)
async def get_cases_by_orgao():
    """Retorna casos agrupados por órgão"""
    try:
        cases_by_orgao = data_service.get_casos_por_orgao()
        
        return APIResponse(
            success=True,
            message="Casos por órgão recuperados com sucesso",
            data=cases_by_orgao
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar casos por órgão: {str(e)}")

@router.get("/cartel-types", response_model=APIResponse)
async def get_cartel_types():
    """Retorna tipos de cartel detectados"""
    try:
        cartel_types = data_service.get_tipos_cartel()
        
        return APIResponse(
            success=True,
            message="Tipos de cartel recuperados com sucesso",
            data=cartel_types
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de cartel: {str(e)}")


@router.get("/health", response_model=APIResponse)
async def health_check():
    """Endpoint de health check"""
    return APIResponse(
        success=True,
        message="API funcionando corretamente",
        data={
            "status": "healthy",
            "version": "1.0.0"
        }
    )
