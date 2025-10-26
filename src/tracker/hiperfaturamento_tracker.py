"""
HiperfaturamentoTracker - Serviço principal de coleta e análise
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models.licitacao import Licitacao
from ..models.analise import AnaliseHiperfaturamento, CasoProcessado, NivelRisco
from ..services.licitacao_collector import LicitacaoCollector
from ..services.hiperfaturamento_analyzer import HiperfaturamentoAnalyzer

logger = logging.getLogger(__name__)

class HiperfaturamentoTracker:
    """Serviço principal para tracking de hiperfaturamento"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Inicializa serviços
        self.collector = LicitacaoCollector()
        self.analyzer = HiperfaturamentoAnalyzer()
        
        # Arquivos de dados
        self.licitacoes_file = self.data_dir / "licitacoes.json"
        self.analises_file = self.data_dir / "analises.json"
        self.casos_file = self.data_dir / "casos_processados.json"
        
        logger.info("HiperfaturamentoTracker inicializado")
    
    def executar_ciclo_completo(self, dias_retroativos: int = 7) -> Dict[str, Any]:
        """
        Executa o ciclo completo de coleta e análise
        
        Args:
            dias_retroativos: Número de dias para buscar licitações
            
        Returns:
            Relatório do ciclo executado
        """
        logger.info(f"Iniciando ciclo completo - últimos {dias_retroativos} dias")
        
        relatorio = {
            "data_execucao": datetime.now().isoformat(),
            "dias_retroativos": dias_retroativos,
            "licitacoes_coletadas": 0,
            "licitacoes_analisadas": 0,
            "casos_suspeitos": 0,
            "erros": []
        }
        
        try:
            # 1. Coleta de licitações
            logger.info("Coletando licitações...")
            licitacoes = self.collector.coletar_licitacoes(dias_retroativos)
            relatorio["licitacoes_coletadas"] = len(licitacoes)
            
            if licitacoes:
                # Salva licitações coletadas
                self._salvar_licitacoes(licitacoes)
                
                # 2. Análise de hiperfaturamento
                logger.info("Analisando licitações...")
                analises = self._analisar_licitacoes(licitacoes)
                relatorio["licitacoes_analisadas"] = len(analises)
                
                if analises:
                    # Salva análises
                    self._salvar_analises(analises)
                    
                    # 3. Processamento de casos
                    logger.info("Processando casos...")
                    casos = self._processar_casos(licitacoes, analises)
                    relatorio["casos_suspeitos"] = len([c for c in casos if c.nivel_risco in [NivelRisco.ALTO, NivelRisco.CRITICO]])
                    
                    if casos:
                        # Salva casos processados
                        self._salvar_casos(casos)
            
            logger.info(f"Ciclo completo finalizado: {relatorio}")
            
        except Exception as e:
            error_msg = f"Erro no ciclo completo: {e}"
            logger.error(error_msg)
            relatorio["erros"].append(error_msg)
        
        return relatorio
    
    def _analisar_licitacoes(self, licitacoes: List[Licitacao]) -> List[AnaliseHiperfaturamento]:
        """Analisa lista de licitações"""
        analises = []
        
        for licitacao in licitacoes:
            try:
                analise = self.analyzer.analisar_licitacao(licitacao)
                analises.append(analise)
                logger.debug(f"Análise concluída para licitação {licitacao.id}")
                
            except Exception as e:
                logger.error(f"Erro na análise da licitação {licitacao.id}: {e}")
        
        return analises
    
    def _processar_casos(self, licitacoes: List[Licitacao], analises: List[AnaliseHiperfaturamento]) -> List[CasoProcessado]:
        """Processa licitações e análises em casos para a API"""
        casos = []
        
        # Cria mapa de análises por ID da licitação
        analises_map = {a.licitacao_id: a for a in analises}
        
        for licitacao in licitacoes:
            try:
                analise = analises_map.get(licitacao.id)
                if not analise:
                    continue
                
                # Processa apenas casos com risco médio ou superior
                if analise.nivel_risco in [NivelRisco.MEDIO, NivelRisco.ALTO, NivelRisco.CRITICO]:
                    caso = self._criar_caso_processado(licitacao, analise)
                    casos.append(caso)
                    
            except Exception as e:
                logger.error(f"Erro ao processar caso da licitação {licitacao.id}: {e}")
        
        return casos
    
    def _criar_caso_processado(self, licitacao: Licitacao, analise: AnaliseHiperfaturamento) -> CasoProcessado:
        """Cria caso processado a partir de licitação e análise"""
        
        # Calcula economia potencial
        valor_superfaturado = 0
        diferenca_percentual = 0
        
        if licitacao.participantes:
            menor_preco = min(p.preco_proposto for p in licitacao.participantes)
            preco_mercado = self.analyzer._obter_preco_mercado(licitacao.itens[0].descricao)
            
            if preco_mercado:
                diferenca_percentual = ((menor_preco - preco_mercado) / preco_mercado) * 100
                valor_superfaturado = (menor_preco - preco_mercado) * licitacao.itens[0].quantidade
        
        # Determina empresa vencedora
        empresa_vencedora = "N/A"
        cnpj = "N/A"
        if licitacao.participantes:
            vencedor = min(licitacao.participantes, key=lambda p: p.preco_proposto)
            empresa_vencedora = vencedor.nome
            cnpj = vencedor.cnpj
        
        # Determina prioridade baseada no score
        priority_level = "Baixa"
        if analise.score_geral >= 80:
            priority_level = "Crítica"
        elif analise.score_geral >= 60:
            priority_level = "Alta"
        elif analise.score_geral >= 40:
            priority_level = "Média"
        
        return CasoProcessado(
            id=licitacao.id,
            titulo=f"Superfaturamento em {licitacao.itens[0].descricao}",
            orgao=licitacao.orgao,
            data_abertura=licitacao.data_abertura.strftime("%Y-%m-%d"),
            valor_estimado=licitacao.valor_estimado,
            empresa_vencedora=empresa_vencedora,
            cnpj=cnpj,
            produto=licitacao.itens[0].descricao,
            quantidade=licitacao.itens[0].quantidade,
            preco_edital=menor_preco if licitacao.participantes else 0,
            preco_mercado=preco_mercado or 0,
            diferenca_percentual=diferenca_percentual,
            valor_superfaturado=valor_superfaturado,
            evidencias=[e.descricao for e in analise.evidencias],
            status=analise.recomendacoes[0] if analise.recomendacoes else "Em análise",
            nivel_risco=analise.nivel_risco,
            risk_score=int(analise.score_geral),
            priority_level=priority_level,
            envolvidos=self._criar_envolvidos(licitacao, empresa_vencedora, cnpj)
        )
    
    def _criar_envolvidos(self, licitacao: Licitacao, empresa: str, cnpj: str) -> Dict[str, Any]:
        """Cria dados dos envolvidos"""
        return {
            "empresa": {
                "nome": empresa,
                "cnpj": cnpj,
                "socios": ["João Silva", "Maria Santos"],  # Simulado
                "historico_vitorias": 15,  # Simulado
                "faturamento_anual": 5000000.00  # Simulado
            },
            "aprovador": {
                "nome": "Carlos Oliveira",  # Simulado
                "cargo": "Diretor de Compras",
                "orgao": licitacao.orgao,
                "historico_licitacoes": 50,  # Simulado
                "tempo_cargo": "3 anos"
            }
        }
    
    def _salvar_licitacoes(self, licitacoes: List[Licitacao]):
        """Salva licitações em arquivo JSON"""
        try:
            data = [lic.to_dict() for lic in licitacoes]
            with open(self.licitacoes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Salvas {len(licitacoes)} licitações em {self.licitacoes_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar licitações: {e}")
    
    def _salvar_analises(self, analises: List[AnaliseHiperfaturamento]):
        """Salva análises em arquivo JSON"""
        try:
            data = [analise.to_dict() for analise in analises]
            with open(self.analises_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Salvas {len(analises)} análises em {self.analises_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar análises: {e}")
    
    def _salvar_casos(self, casos: List[CasoProcessado]):
        """Salva casos processados em arquivo JSON"""
        try:
            data = [caso.to_dict() for caso in casos]
            with open(self.casos_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Salvos {len(casos)} casos em {self.casos_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar casos: {e}")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        try:
            # Carrega casos processados
            if self.casos_file.exists():
                with open(self.casos_file, 'r', encoding='utf-8') as f:
                    casos = json.load(f)
                
                total_casos = len(casos)
                casos_suspeitos = len([c for c in casos if c.get('nivel_risco') in ['Alto', 'Crítico']])
                valor_superfaturado_total = sum(max(0, c.get('valor_superfaturado', 0)) for c in casos)
                taxa_suspeicao = (casos_suspeitos / total_casos * 100) if total_casos > 0 else 0
                
                return {
                    "total_licitacoes_analisadas": total_casos,
                    "casos_suspeitos": casos_suspeitos,
                    "valor_superfaturado_total": valor_superfaturado_total,
                    "taxa_suspeicao": taxa_suspeicao
                }
            
            return {
                "total_licitacoes_analisadas": 0,
                "casos_suspeitos": 0,
                "valor_superfaturado_total": 0,
                "taxa_suspeicao": 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                "total_licitacoes_analisadas": 0,
                "casos_suspeitos": 0,
                "valor_superfaturado_total": 0,
                "taxa_suspeicao": 0
            }
