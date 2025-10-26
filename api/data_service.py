"""
Serviço de dados para a API
Consome dados processados pelo HiperfaturamentoTracker
"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.casos_file = self.data_dir / "casos_processados.json"
        self.analises_file = self.data_dir / "analises.json"
    
    def _carregar_casos(self) -> List[Dict[str, Any]]:
        """Carrega casos processados do arquivo JSON"""
        try:
            if self.casos_file.exists():
                with open(self.casos_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar casos: {e}")
            return []
    
    def _carregar_analises(self) -> List[Dict[str, Any]]:
        """Carrega análises do arquivo JSON"""
        try:
            if self.analises_file.exists():
                with open(self.analises_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar análises: {e}")
            return []

    def get_noticias(self, limit: int = 10, filtro_risco: str = None) -> List[Dict[str, Any]]:
        """Retorna casos formatados como notícias"""
        casos = self._carregar_casos()
        
        # Aplica filtro de risco se especificado
        if filtro_risco:
            casos = [caso for caso in casos if caso.get("nivel_risco", "").lower() == filtro_risco.lower()]
        
        # Limita resultados
        casos = casos[:limit]
        
        # Converte para formato de notícias
        noticias = []
        for caso in casos:
            noticia = {
                "titulo": f"🚨 ALERTA: {caso['titulo']}",
                "resumo": f"Detectado superfaturamento de {caso['diferenca_percentual']:.0f}% em licitação de {caso['produto']}. Valor estimado: R$ {caso['valor_estimado']:,.2f}",
                "data": caso["data_abertura"],
                "orgao": caso["orgao"],
                "valor": f"R$ {caso['valor_estimado']:,.2f}",
                "risco": caso["nivel_risco"],
                "risk_level": caso["nivel_risco"],
                "risk_score": caso["risk_score"],
                "valor_superfaturado": caso.get("valor_superfaturado", caso.get("economia_potencial", 0)),
                "status": caso["status"],
                "empresa": caso["empresa_vencedora"],
                "empresa_vencedora": caso["empresa_vencedora"],
                "cnpj": caso["cnpj"],
                "produto": caso["produto"],
                "valor_estimado": caso["valor_estimado"],
                "diferenca_percentual": caso["diferenca_percentual"],
                # Campos adicionais para o modal
                "preco_edital": caso.get("preco_edital", 0),
                "preco_mercado": caso.get("preco_mercado", 0),
                "quantidade": caso.get("quantidade", 0),
                "priority_level": caso.get("priority_level", "Média"),
                "evidencias": caso.get("evidencias", []),
                "envolvidos": caso.get("envolvidos", {})
            }
            noticias.append(noticia)
        
        return noticias

    def get_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do sistema"""
        casos = self._carregar_casos()
        analises = self._carregar_analises()
        
        if not analises:
            return {
                "total_licitacoes_analisadas": 0,
                "casos_suspeitos": 0,
                "valor_superfaturado_total": 0,
                "taxa_suspeicao": 0
            }
        
        # Total de licitações analisadas (todas as análises)
        total_licitacoes_analisadas = len(analises)
        
        # Casos suspeitos (apenas os que foram processados como casos)
        casos_suspeitos = len(casos)
        
        # Valor superfaturado total (apenas dos casos suspeitos)
        valor_superfaturado_total = sum(max(0, c.get("valor_superfaturado", c.get("economia_potencial", 0))) for c in casos)
        
        # Taxa de suspeição real (casos suspeitos / total analisado)
        taxa_suspeicao = (casos_suspeitos / total_licitacoes_analisadas * 100) if total_licitacoes_analisadas > 0 else 0
        
        return {
            "total_licitacoes_analisadas": total_licitacoes_analisadas,
            "casos_suspeitos": casos_suspeitos,
            "valor_superfaturado_total": valor_superfaturado_total,
            "taxa_suspeicao": taxa_suspeicao
        }

    def get_casos_por_orgao(self) -> List[Dict[str, Any]]:
        """Retorna casos agrupados por órgão"""
        casos = self._carregar_casos()
        
        # Agrupa por órgão
        orgaos = {}
        for caso in casos:
            orgao = caso["orgao"]
            if orgao not in orgaos:
                orgaos[orgao] = {"casos": 0, "economia": 0}
            orgaos[orgao]["casos"] += 1
            orgaos[orgao]["economia"] += caso.get("economia_potencial", 0)
        
        # Converte para lista
        resultado = []
        for orgao, dados in orgaos.items():
            resultado.append({
                "orgao": orgao,
                "casos": dados["casos"],
                "economia": dados["economia"]
            })
        
        return resultado

    def get_caso_detalhado(self, caso_id: str) -> Dict[str, Any]:
        """Retorna detalhes de um caso específico"""
        casos = self._carregar_casos()
        
        for caso in casos:
            if caso.get("id") == caso_id:
                return caso
        
        return {}

    def get_tipos_cartel(self) -> List[str]:
        """Retorna tipos de cartel detectados"""
        return [
            "Same Winner Always",
            "Price Bending", 
            "Tailored Specifications",
            "Last Minute Bidders"
        ]
