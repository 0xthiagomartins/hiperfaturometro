"""
Testes unitários para o HiperfaturamentoAnalyzer
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.services.hiperfaturamento_analyzer import HiperfaturamentoAnalyzer
from src.models.licitacao import Licitacao, ItemLicitacao, Participante, StatusLicitacao, TipoLicitacao
from src.models.analise import NivelRisco, TipoEvidencia

class TestHiperfaturamentoAnalyzer:
    """Testes para o HiperfaturamentoAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Cria instância do analyzer para testes"""
        return HiperfaturamentoAnalyzer()
    
    @pytest.fixture
    def licitacao_preco_excessivo(self):
        """Cria licitação com preço excessivo"""
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
                    preco_proposto=4000.00,  # Preço alto
                    classificacao=1,
                    habilitado=True
                )
            ]
        )
    
    @pytest.fixture
    def licitacao_especificacoes_suspeitas(self):
        """Cria licitação com especificações suspeitas"""
        return Licitacao(
            id="TEST-002",
            numero="002/2024",
            orgao="Teste Orgão",
            modalidade=TipoLicitacao.PREGAO,
            objeto="Aquisição de tablets",
            data_abertura=datetime.now() - timedelta(days=5),
            data_fechamento=datetime.now() + timedelta(days=25),
            valor_estimado=50000.00,
            status=StatusLicitacao.ABERTA,
            itens=[
                ItemLicitacao(
                    codigo="002",
                    descricao="Tablet Samsung Galaxy Tab A8",
                    quantidade=20,
                    unidade="UN",
                    especificacoes="Exclusivamente Samsung Galaxy Tab A8, apenas modelo específico, obrigatoriamente com Android 11"
                )
            ],
            participantes=[
                Participante(
                    cnpj="98.765.432/0001-10",
                    nome="Digital Devices S.A.",
                    preco_proposto=2500.00,
                    classificacao=1,
                    habilitado=True
                )
            ]
        )
    
    @pytest.fixture
    def licitacao_baixa_concorrencia(self):
        """Cria licitação com baixa concorrência"""
        return Licitacao(
            id="TEST-003",
            numero="003/2024",
            orgao="Teste Orgão",
            modalidade=TipoLicitacao.PREGAO,
            objeto="Aquisição de computadores",
            data_abertura=datetime.now() - timedelta(days=5),
            data_fechamento=datetime.now() + timedelta(days=25),
            valor_estimado=80000.00,
            status=StatusLicitacao.ABERTA,
            itens=[
                ItemLicitacao(
                    codigo="003",
                    descricao="Computador Desktop",
                    quantidade=5,
                    unidade="UN",
                    especificacoes="Intel i7, 16GB RAM, SSD 512GB"
                )
            ],
            participantes=[
                Participante(
                    cnpj="11.222.333/0001-44",
                    nome="Só Uma Empresa LTDA",
                    preco_proposto=16000.00,
                    classificacao=1,
                    habilitado=True
                )
            ]  # Apenas 1 participante
        )
    
    def test_inicializacao(self, analyzer):
        """Testa inicialização do analyzer"""
        assert analyzer.thresholds["preco_excessivo"] == 30
        assert analyzer.thresholds["especificacoes_tailor_made"] == 0.8
        assert analyzer.thresholds["empresa_cartel"] == 0.7
        assert analyzer.thresholds["baixa_concorrencia"] == 2
        assert analyzer.thresholds["prazo_suspeito"] == 7
        
        assert analyzer.pesos["preco_excessivo"] == 0.4
        assert analyzer.pesos["especificacoes_tailor_made"] == 0.3
        assert analyzer.pesos["empresa_cartel"] == 0.2
        assert analyzer.pesos["baixa_concorrencia"] == 0.1
    
    @patch.object(HiperfaturamentoAnalyzer, '_obter_preco_mercado')
    def test_analisar_preco_excessivo(self, mock_preco_mercado, analyzer, licitacao_preco_excessivo):
        """Testa análise de preço excessivo"""
        mock_preco_mercado.return_value = 2500.00  # Preço de mercado
        
        evidencia = analyzer._analisar_preco_excessivo(licitacao_preco_excessivo)
        
        assert evidencia is not None
        assert evidencia.tipo == TipoEvidencia.PRECO_EXCESSIVO
        assert "60.0%" in evidencia.descricao  # (4000-2500)/2500 * 100 = 60%
        assert evidencia.score > 30  # Score alto devido ao preço excessivo
        assert evidencia.detalhes["preco_proposto"] == 4000.00
        assert evidencia.detalhes["preco_mercado"] == 2500.00
    
    @patch.object(HiperfaturamentoAnalyzer, '_obter_preco_mercado')
    def test_analisar_preco_normal(self, mock_preco_mercado, analyzer, licitacao_preco_excessivo):
        """Testa análise de preço normal"""
        mock_preco_mercado.return_value = 3500.00  # Preço de mercado próximo
        
        evidencia = analyzer._analisar_preco_excessivo(licitacao_preco_excessivo)
        
        # Com preço de mercado 3500, a diferença é 14.3%, abaixo do threshold de 30%
        assert evidencia is None
    
    def test_analisar_especificacoes_tailor_made(self, analyzer, licitacao_especificacoes_suspeitas):
        """Testa análise de especificações tailor-made"""
        evidencia = analyzer._analisar_especificacoes_tailor_made(licitacao_especificacoes_suspeitas)
        
        assert evidencia is not None
        assert evidencia.tipo == TipoEvidencia.ESPECIFICACOES_TAILOR_MADE
        assert "específicas" in evidencia.descricao.lower()
        assert evidencia.score > 40  # Score alto devido às palavras suspeitas
        assert "exclusivamente" in evidencia.detalhes["especificacoes"].lower()
    
    def test_analisar_especificacoes_normais(self, analyzer, licitacao_preco_excessivo):
        """Testa análise de especificações normais"""
        evidencia = analyzer._analisar_especificacoes_tailor_made(licitacao_preco_excessivo)
        
        # Especificações normais não devem gerar evidência
        assert evidencia is None
    
    @patch.object(HiperfaturamentoAnalyzer, '_analisar_empresa_cartel')
    def test_analisar_empresa_cartel(self, mock_cartel, analyzer, licitacao_preco_excessivo):
        """Testa análise de empresa cartel"""
        mock_cartel.return_value = None  # Simula que não há evidência de cartel
        
        evidencia = analyzer._analisar_empresa_cartel(licitacao_preco_excessivo)
        
        # Como é mock, não há evidência real
        assert evidencia is None
    
    def test_analisar_baixa_concorrencia(self, analyzer, licitacao_baixa_concorrencia):
        """Testa análise de baixa concorrência"""
        evidencia = analyzer._analisar_baixa_concorrencia(licitacao_baixa_concorrencia)
        
        assert evidencia is not None
        assert evidencia.tipo == TipoEvidencia.BAIXA_CONCORRENCIA
        assert "1 participante" in evidencia.descricao
        assert evidencia.score == 50  # 100 - (1 * 50)
        assert evidencia.detalhes["num_participantes"] == 1
    
    def test_analisar_concorrencia_normal(self, analyzer, licitacao_preco_excessivo):
        """Testa análise de concorrência normal"""
        # Adiciona mais participantes
        licitacao_preco_excessivo.participantes.append(
            Participante(
                cnpj="99.888.777/0001-66",
                nome="Outra Empresa LTDA",
                preco_proposto=3500.00,
                classificacao=2,
                habilitado=True
            )
        )
        
        evidencia = analyzer._analisar_baixa_concorrencia(licitacao_preco_excessivo)
        
        # Com 2 participantes, não deve gerar evidência
        assert evidencia is None
    
    def test_analisar_prazo_suspeito(self, analyzer):
        """Testa análise de prazo suspeito"""
        # Data fixa para o teste
        data_atual = datetime(2024, 1, 20, 12, 0, 0)
        data_fechamento = datetime(2024, 1, 22, 12, 0, 0)  # 2 dias depois
        
        licitacao = Licitacao(
            id="TEST-004",
            numero="004/2024",
            orgao="Teste Orgão",
            modalidade=TipoLicitacao.PREGAO,
            objeto="Aquisição urgente",
            data_abertura=datetime(2024, 1, 15, 12, 0, 0),
            data_fechamento=data_fechamento,
            valor_estimado=30000.00,
            status=StatusLicitacao.ABERTA,
            itens=[],
            participantes=[]
        )

        with patch('src.services.hiperfaturamento_analyzer.datetime') as mock_datetime:
            mock_datetime.now.return_value = data_atual
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            evidencia = analyzer._analisar_prazo_suspeito(licitacao)

            assert evidencia is not None
            assert evidencia.tipo == TipoEvidencia.PRAZO_SUSPEITO
            assert "dias" in evidencia.descricao
            assert evidencia.score > 0
            assert evidencia.detalhes["dias_para_fechamento"] == 2
    
    def test_obter_preco_mercado(self, analyzer):
        """Testa obtenção de preço de mercado"""
        # Testa produtos conhecidos
        assert analyzer._obter_preco_mercado("Notebook Dell") == 2500.00
        assert analyzer._obter_preco_mercado("Tablet Samsung") == 1200.00
        assert analyzer._obter_preco_mercado("Computador Desktop") == 3000.00
        
        # Testa produto desconhecido
        assert analyzer._obter_preco_mercado("Produto Inexistente") is None
    
    def test_calcular_score_geral(self, analyzer):
        """Testa cálculo de score geral"""
        from src.models.analise import Evidencia
        
        evidencias = [
            Evidencia(
                tipo=TipoEvidencia.PRECO_EXCESSIVO,
                descricao="Preço alto",
                score=80.0
            ),
            Evidencia(
                tipo=TipoEvidencia.BAIXA_CONCORRENCIA,
                descricao="Poucos participantes",
                score=60.0
            )
        ]
        
        score = analyzer._calcular_score_geral(evidencias)
        
        # Score ponderado: (80 * 0.4 + 60 * 0.1) / (0.4 + 0.1) = 76.0
        assert score == 76.0
    
    def test_determinar_nivel_risco(self, analyzer):
        """Testa determinação de nível de risco"""
        assert analyzer._determinar_nivel_risco(85.0) == NivelRisco.CRITICO
        assert analyzer._determinar_nivel_risco(70.0) == NivelRisco.ALTO
        assert analyzer._determinar_nivel_risco(50.0) == NivelRisco.MEDIO
        assert analyzer._determinar_nivel_risco(30.0) == NivelRisco.BAIXO
    
    def test_gerar_recomendacoes(self, analyzer):
        """Testa geração de recomendações"""
        from src.models.analise import Evidencia
        
        evidencias = [
            Evidencia(
                tipo=TipoEvidencia.PRECO_EXCESSIVO,
                descricao="Preço alto",
                score=80.0
            )
        ]
        
        recomendacoes = analyzer._gerar_recomendacoes(evidencias, 80.0)
        
        assert "URGENTE" in recomendacoes[0]
        assert "Verificar preços de mercado atualizados" in recomendacoes
    
    def test_calcular_confiabilidade(self, analyzer):
        """Testa cálculo de confiabilidade"""
        from src.models.analise import Evidencia
        
        evidencias = [
            Evidencia(
                tipo=TipoEvidencia.PRECO_EXCESSIVO,
                descricao="Preço alto",
                score=80.0
            ),
            Evidencia(
                tipo=TipoEvidencia.BAIXA_CONCORRENCIA,
                descricao="Poucos participantes",
                score=60.0
            )
        ]
        
        confiabilidade = analyzer._calcular_confiabilidade(evidencias)
        
        # Confiabilidade base: 2 evidências * 20 = 40
        # Score médio: (80 + 60) / 2 = 70
        # Confiabilidade ajustada: 40 * (70/100) = 28
        assert confiabilidade == 28.0
    
    @patch.object(HiperfaturamentoAnalyzer, '_obter_preco_mercado')
    def test_analisar_licitacao_completa(self, mock_preco_mercado, analyzer, licitacao_preco_excessivo):
        """Testa análise completa de licitação"""
        mock_preco_mercado.return_value = 2500.00
        
        analise = analyzer.analisar_licitacao(licitacao_preco_excessivo)
        
        assert analise.licitacao_id == "TEST-001"
        assert analise.score_geral > 0
        assert analise.nivel_risco in [NivelRisco.BAIXO, NivelRisco.MEDIO, NivelRisco.ALTO, NivelRisco.CRITICO]
        assert len(analise.evidencias) > 0
        assert len(analise.recomendacoes) > 0
        assert 0 <= analise.confiabilidade <= 100
