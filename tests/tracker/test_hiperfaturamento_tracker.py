"""
Testes unitários para o HiperfaturamentoTracker
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.tracker.hiperfaturamento_tracker import HiperfaturamentoTracker
from src.models.licitacao import Licitacao, ItemLicitacao, Participante, StatusLicitacao, TipoLicitacao
from src.models.analise import AnaliseHiperfaturamento, NivelRisco

class TestHiperfaturamentoTracker:
    """Testes para o HiperfaturamentoTracker"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def tracker(self, temp_dir):
        """Cria instância do tracker para testes"""
        return HiperfaturamentoTracker(data_dir=temp_dir)
    
    @pytest.fixture
    def licitacao_mock(self):
        """Cria licitação mock para testes"""
        return Licitacao(
            id="TEST-001",
            numero="001/2024",
            orgao="Teste Orgão",
            modalidade=TipoLicitacao.PREGAO,
            objeto="Aquisição de notebooks",
            data_abertura=datetime.now() - timedelta(days=5),
            data_fechamento=datetime.now() + timedelta(days=25),
            valor_estimado=100000.00,
            status=StatusLicitacao.ABERTA,
            itens=[
                ItemLicitacao(
                    codigo="001",
                    descricao="Notebook Dell Latitude 5520",
                    quantidade=10,
                    unidade="UN",
                    especificacoes="Intel i5, 8GB RAM, SSD 256GB"
                )
            ],
            participantes=[
                Participante(
                    cnpj="12.345.678/0001-90",
                    nome="Tech Solutions LTDA",
                    preco_proposto=12000.00,
                    classificacao=1,
                    habilitado=True
                )
            ]
        )
    
    def test_inicializacao(self, temp_dir):
        """Testa inicialização do tracker"""
        tracker = HiperfaturamentoTracker(data_dir=temp_dir)
        
        assert tracker.data_dir == Path(temp_dir)
        assert tracker.licitacoes_file == Path(temp_dir) / "licitacoes.json"
        assert tracker.analises_file == Path(temp_dir) / "analises.json"
        assert tracker.casos_file == Path(temp_dir) / "casos_processados.json"
        assert tracker.collector is not None
        assert tracker.analyzer is not None
    
    def test_executar_ciclo_completo_sucesso(self, tracker, licitacao_mock):
        """Testa execução completa do ciclo"""
        # Mock do collector
        with patch.object(tracker.collector, 'coletar_licitacoes') as mock_coletar:
            mock_coletar.return_value = [licitacao_mock]
            
            # Mock do analyzer
            analise_mock = AnaliseHiperfaturamento(
                licitacao_id="TEST-001",
                data_analise=datetime.now(),
                score_geral=75.0,
                nivel_risco=NivelRisco.ALTO,
                evidencias=[],
                recomendacoes=["Investigar"],
                confiabilidade=80.0
            )
            
            with patch.object(tracker.analyzer, 'analisar_licitacao') as mock_analisar:
                mock_analisar.return_value = analise_mock
                
                # Executa o ciclo
                relatorio = tracker.executar_ciclo_completo(dias_retroativos=7)
                
                # Verifica resultados
                assert relatorio["licitacoes_coletadas"] == 1
                assert relatorio["licitacoes_analisadas"] == 1
                assert relatorio["casos_suspeitos"] == 1
                assert len(relatorio["erros"]) == 0
        
        # Verifica se arquivos foram criados
        assert tracker.licitacoes_file.exists()
        assert tracker.analises_file.exists()
        assert tracker.casos_file.exists()
    
    def test_salvar_licitacoes(self, tracker, licitacao_mock):
        """Testa salvamento de licitações"""
        licitacoes = [licitacao_mock]
        
        tracker._salvar_licitacoes(licitacoes)
        
        assert tracker.licitacoes_file.exists()
        
        with open(tracker.licitacoes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["id"] == "TEST-001"
        assert data[0]["orgao"] == "Teste Orgão"
    
    def test_salvar_analises(self, tracker):
        """Testa salvamento de análises"""
        analise = AnaliseHiperfaturamento(
            licitacao_id="TEST-001",
            data_analise=datetime.now(),
            score_geral=75.0,
            nivel_risco=NivelRisco.ALTO,
            evidencias=[],
            recomendacoes=["Investigar"],
            confiabilidade=80.0
        )
        
        tracker._salvar_analises([analise])
        
        assert tracker.analises_file.exists()
        
        with open(tracker.analises_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["licitacao_id"] == "TEST-001"
        assert data[0]["score_geral"] == 75.0
        assert data[0]["nivel_risco"] == "Alto"
    
    def test_salvar_casos(self, tracker):
        """Testa salvamento de casos processados"""
        from src.models.analise import CasoProcessado
        
        caso = CasoProcessado(
            id="TEST-001",
            titulo="Teste de caso",
            orgao="Teste Orgão",
            data_abertura="2024-01-01",
            valor_estimado=100000.00,
            empresa_vencedora="Tech Solutions",
            cnpj="12.345.678/0001-90",
            produto="Notebook",
            quantidade=10,
            preco_edital=12000.00,
            preco_mercado=10000.00,
            diferenca_percentual=20.0,
            economia_potencial=20000.00,
            evidencias=["Preço excessivo"],
            status="Em análise",
            nivel_risco=NivelRisco.ALTO,
            risk_score=75,
            priority_level="Alta"
        )
        
        tracker._salvar_casos([caso])
        
        assert tracker.casos_file.exists()
        
        with open(tracker.casos_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["id"] == "TEST-001"
        assert data[0]["nivel_risco"] == "Alto"
        assert data[0]["risk_score"] == 75
    
    def test_obter_estatisticas_com_dados(self, tracker):
        """Testa obtenção de estatísticas com dados"""
        # Cria arquivo de casos
        casos_data = [
            {
                "id": "TEST-001",
                "nivel_risco": "Alto",
                "economia_potencial": 50000.00
            },
            {
                "id": "TEST-002", 
                "nivel_risco": "Baixo",
                "economia_potencial": 10000.00
            },
            {
                "id": "TEST-003",
                "nivel_risco": "Crítico",
                "economia_potencial": 100000.00
            }
        ]
        
        with open(tracker.casos_file, 'w', encoding='utf-8') as f:
            json.dump(casos_data, f)
        
        stats = tracker.obter_estatisticas()
        
        assert stats["total_licitacoes_analisadas"] == 3
        assert stats["casos_suspeitos"] == 2  # Alto + Crítico
        assert stats["economia_potencial_total"] == 160000.00
        assert abs(stats["taxa_suspeicao"] - 66.67) < 0.01  # 2/3 * 100
    
    def test_obter_estatisticas_sem_dados(self, tracker):
        """Testa obtenção de estatísticas sem dados"""
        stats = tracker.obter_estatisticas()
        
        assert stats["total_licitacoes_analisadas"] == 0
        assert stats["casos_suspeitos"] == 0
        assert stats["economia_potencial_total"] == 0
        assert stats["taxa_suspeicao"] == 0
    
    def test_criar_caso_processado(self, tracker, licitacao_mock):
        """Testa criação de caso processado"""
        analise = AnaliseHiperfaturamento(
            licitacao_id="TEST-001",
            data_analise=datetime.now(),
            score_geral=75.0,
            nivel_risco=NivelRisco.ALTO,
            evidencias=[],
            recomendacoes=["Investigar"],
            confiabilidade=80.0
        )
        
        caso = tracker._criar_caso_processado(licitacao_mock, analise)
        
        assert caso.id == "TEST-001"
        assert caso.orgao == "Teste Orgão"
        assert caso.nivel_risco == NivelRisco.ALTO
        assert caso.risk_score == 75
        assert caso.priority_level == "Alta"
        assert caso.empresa_vencedora == "Tech Solutions LTDA"
        assert caso.produto == "Notebook Dell Latitude 5520"
    
    def test_criar_envolvidos(self, tracker, licitacao_mock):
        """Testa criação de dados dos envolvidos"""
        envolvidos = tracker._criar_envolvidos(
            licitacao_mock, 
            "Tech Solutions LTDA", 
            "12.345.678/0001-90"
        )
        
        assert envolvidos["empresa"]["nome"] == "Tech Solutions LTDA"
        assert envolvidos["empresa"]["cnpj"] == "12.345.678/0001-90"
        assert envolvidos["aprovador"]["orgao"] == "Teste Orgão"
        assert "socios" in envolvidos["empresa"]
        assert "cargo" in envolvidos["aprovador"]
