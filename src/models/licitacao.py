"""
Modelos de dados para licitações
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StatusLicitacao(str, Enum):
    ABERTA = "Aberta"
    FECHADA = "Fechada"
    CANCELADA = "Cancelada"
    SUSPENSA = "Suspensa"

class TipoLicitacao(str, Enum):
    CONCORRENCIA = "Concorrência"
    TOMADA_PRECOS = "Tomada de Preços"
    PREGAO = "Pregão"
    RDC = "RDC"

@dataclass
class Participante:
    cnpj: str
    nome: str
    preco_proposto: float
    classificacao: int
    habilitado: bool = True

@dataclass
class ItemLicitacao:
    codigo: str
    descricao: str
    quantidade: int
    unidade: str
    especificacoes: str
    preco_estimado: Optional[float] = None

@dataclass
class Licitacao:
    """Modelo principal de uma licitação"""
    id: str
    numero: str
    orgao: str
    modalidade: TipoLicitacao
    objeto: str
    data_abertura: datetime
    data_fechamento: datetime
    valor_estimado: float
    status: StatusLicitacao
    itens: List[ItemLicitacao]
    participantes: List[Participante]
    edital_url: Optional[str] = None
    observacoes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "numero": self.numero,
            "orgao": self.orgao,
            "modalidade": self.modalidade.value,
            "objeto": self.objeto,
            "data_abertura": self.data_abertura.isoformat(),
            "data_fechamento": self.data_fechamento.isoformat(),
            "valor_estimado": self.valor_estimado,
            "status": self.status.value,
            "itens": [
                {
                    "codigo": item.codigo,
                    "descricao": item.descricao,
                    "quantidade": item.quantidade,
                    "unidade": item.unidade,
                    "especificacoes": item.especificacoes,
                    "preco_estimado": item.preco_estimado
                }
                for item in self.itens
            ],
            "participantes": [
                {
                    "cnpj": p.cnpj,
                    "nome": p.nome,
                    "preco_proposto": p.preco_proposto,
                    "classificacao": p.classificacao,
                    "habilitado": p.habilitado
                }
                for p in self.participantes
            ],
            "edital_url": self.edital_url,
            "observacoes": self.observacoes
        }
