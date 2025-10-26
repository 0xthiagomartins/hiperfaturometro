"""
Modelos de dados para análise de hiperfaturamento
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class NivelRisco(str, Enum):
    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"
    CRITICO = "Crítico"

class TipoEvidencia(str, Enum):
    PRECO_EXCESSIVO = "preco_excessivo"
    ESPECIFICACOES_TAILOR_MADE = "especificacoes_tailor_made"
    EMPRESA_CARTEL = "empresa_cartel"
    BAIXA_CONCORRENCIA = "baixa_concorrencia"
    PRAZO_SUSPEITO = "prazo_suspeito"
    HISTORICO_SUSPEITO = "historico_suspeito"

@dataclass
class Evidencia:
    tipo: TipoEvidencia
    descricao: str
    score: float  # 0-100
    detalhes: Optional[Dict[str, Any]] = None

@dataclass
class AnaliseHiperfaturamento:
    """Resultado da análise de hiperfaturamento"""
    licitacao_id: str
    data_analise: datetime
    score_geral: float  # 0-100
    nivel_risco: NivelRisco
    evidencias: List[Evidencia]
    recomendacoes: List[str]
    confiabilidade: float  # 0-100
    analista_responsavel: str = "Sistema IA"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "licitacao_id": self.licitacao_id,
            "data_analise": self.data_analise.isoformat(),
            "score_geral": self.score_geral,
            "nivel_risco": self.nivel_risco.value,
            "evidencias": [
                {
                    "tipo": evidencia.tipo.value,
                    "descricao": evidencia.descricao,
                    "score": evidencia.score,
                    "detalhes": evidencia.detalhes
                }
                for evidencia in self.evidencias
            ],
            "recomendacoes": self.recomendacoes,
            "confiabilidade": self.confiabilidade,
            "analista_responsavel": self.analista_responsavel
        }

@dataclass
class CasoProcessado:
    """Caso processado e armazenado para a API"""
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
    valor_superfaturado: float
    evidencias: List[str]
    status: str
    nivel_risco: NivelRisco
    risk_score: int
    priority_level: str
    envolvidos: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "orgao": self.orgao,
            "data_abertura": self.data_abertura,
            "valor_estimado": self.valor_estimado,
            "empresa_vencedora": self.empresa_vencedora,
            "cnpj": self.cnpj,
            "produto": self.produto,
            "quantidade": self.quantidade,
            "preco_edital": self.preco_edital,
            "preco_mercado": self.preco_mercado,
            "diferenca_percentual": self.diferenca_percentual,
            "valor_superfaturado": self.valor_superfaturado,
            "evidencias": self.evidencias,
            "status": self.status,
            "nivel_risco": self.nivel_risco.value,
            "risk_score": self.risk_score,
            "priority_level": self.priority_level,
            "envolvidos": self.envolvidos
        }
