"""
Modelos Pydantic para a API
Define a estrutura de dados e validação
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    ALTO = "Alto"
    MEDIO = "Médio"
    BAIXO = "Baixo"

class PriorityLevel(str, Enum):
    CRITICA = "Crítica"
    ALTA = "Alta"
    MEDIA = "Média"
    BAIXA = "Baixa"

class StatusType(str, Enum):
    EM_INVESTIGACAO = "Em investigação"
    ENCAMINHADO_TCU = "Encaminhado ao TCU"
    ANALISE_TECNICA = "Análise técnica"
    SOB_INVESTIGACAO = "Sob investigação"
    RELATORIO_ENVIADO = "Relatório enviado"

class EmpresaModel(BaseModel):
    nome: str
    cnpj: str
    socios: List[str]
    historico_vitorias: int
    faturamento_anual: float

class AprovadorModel(BaseModel):
    nome: str
    cargo: str
    orgao: str
    historico_licitacoes: int
    tempo_cargo: str

class EnvolvidosModel(BaseModel):
    empresa: EmpresaModel
    aprovador: AprovadorModel

class CaseModel(BaseModel):
    id: str
    titulo: str
    orgao: str
    data_abertura: str
    valor_estimado: float
    empresa_vencedora: str
    cnpj: str
    produto: str
    quantidade: int
    preco_edital: float
    preco_mercado: float
    diferenca_percentual: float
    economia_potencial: float
    evidencias: List[str]
    status: StatusType
    nivel_risco: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    priority_level: PriorityLevel
    envolvidos: Optional[EnvolvidosModel] = None

class StatisticsModel(BaseModel):
    total_licitacoes_analisadas: int
    casos_suspeitos: int
    economia_potencial_total: float
    taxa_suspeicao: float

class CaseByOrgaoModel(BaseModel):
    orgao: str
    casos: int
    economia: float

class BreakingNewsModel(BaseModel):
    title: str
    description: str
    total_cases: int
    total_economy: float
    timestamp: datetime

class CaseFilters(BaseModel):
    limit: Optional[int] = Field(default=10, ge=1, le=100)
    risk_level: Optional[RiskLevel] = None
    orgao: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    priority_level: Optional[PriorityLevel] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
