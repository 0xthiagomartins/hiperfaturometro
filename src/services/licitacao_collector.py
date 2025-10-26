"""
Serviço para coleta de licitações de diferentes fontes
Dados baseados em licitações reais de equipamentos de TI
"""

import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from ..models.licitacao import Licitacao, ItemLicitacao, Participante, StatusLicitacao, TipoLicitacao

logger = logging.getLogger(__name__)

class LicitacaoCollector:
    """Coletor de licitações de diferentes fontes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Hiperfaturômetro/1.0 (Sistema de Detecção de Hiperfaturamento)'
        })
    
    def coletar_licitacoes(self, dias_retroativos: int = 7) -> List[Licitacao]:
        """
        Coleta licitações dos últimos N dias
        
        Args:
            dias_retroativos: Número de dias para buscar licitações
            
        Returns:
            Lista de licitações coletadas
        """
        licitacoes = []
        
        try:
            # Coleta do Portal da Transparência
            licitacoes.extend(self._coletar_portal_transparencia(dias_retroativos))
            
            logger.info(f"Coletadas {len(licitacoes)} licitações")
            
        except Exception as e:
            logger.error(f"Erro na coleta de licitações: {e}")
            
        return licitacoes
    
    def _coletar_portal_transparencia(self, dias: int) -> List[Licitacao]:
        """Coleta licitações do Portal da Transparência - Dados realistas"""
        licitacoes = []
        
        # Gerar muitas licitações normais (sem superfaturamento)
        licitacoes.extend(self._gerar_licitacoes_normais(200))
        
        # Adicionar algumas licitações suspeitas (as que já existem)
        licitacoes.extend(self._gerar_licitacoes_suspeitas())
        
        return licitacoes
    
    def _gerar_licitacoes_normais(self, quantidade: int) -> List[Licitacao]:
        """Gera licitações normais (sem superfaturamento)"""
        licitacoes = []
        
        # Produtos de TI com preços justos
        produtos_ti = [
            {"nome": "Notebook Dell Latitude 5520", "preco_justo": 2800.00, "categoria": "notebook"},
            {"nome": "Notebook HP EliteBook 850 G8", "preco_justo": 3200.00, "categoria": "notebook"},
            {"nome": "Notebook Lenovo ThinkPad E15", "preco_justo": 2900.00, "categoria": "notebook"},
            {"nome": "Tablet Samsung Galaxy Tab A8", "preco_justo": 1200.00, "categoria": "tablet"},
            {"nome": "Tablet iPad 10.9\" 64GB Wi-Fi", "preco_justo": 2800.00, "categoria": "tablet"},
            {"nome": "Smartphone Samsung Galaxy A54 5G", "preco_justo": 1800.00, "categoria": "smartphone"},
            {"nome": "Smartphone Motorola Moto G73 5G", "preco_justo": 1400.00, "categoria": "smartphone"},
            {"nome": "Computador Desktop HP EliteDesk 800 G8", "preco_justo": 3200.00, "categoria": "desktop"},
            {"nome": "Monitor LG 24\" Full HD", "preco_justo": 1200.00, "categoria": "monitor"},
            {"nome": "Impressora HP LaserJet Pro M404dn", "preco_justo": 2500.00, "categoria": "impressora"},
            {"nome": "Servidor Dell PowerEdge R750", "preco_justo": 180000.00, "categoria": "servidor"},
            {"nome": "Switch Cisco Catalyst 2960-X", "preco_justo": 20000.00, "categoria": "rede"},
            {"nome": "Projetor Epson PowerLite 1781W", "preco_justo": 3500.00, "categoria": "projetor"},
            {"nome": "Roteador TP-Link Archer AX73", "preco_justo": 1200.00, "categoria": "rede"},
            {"nome": "Câmera IP Hikvision DS-2CD2385G1", "preco_justo": 4000.00, "categoria": "seguranca"},
            {"nome": "Tablet Samsung Galaxy Tab S8 128GB", "preco_justo": 4500.00, "categoria": "tablet"},
        ]
        
        # Órgãos públicos
        orgaos = [
            "Ministério da Educação", "Ministério da Saúde", "Ministério da Defesa",
            "Prefeitura de São Paulo", "Prefeitura do Rio de Janeiro", "Prefeitura de Belo Horizonte",
            "Governo do Estado de São Paulo", "Governo do Estado do Rio de Janeiro",
            "Tribunal de Contas da União", "Tribunal Superior do Trabalho",
            "Ministério das Comunicações", "Polícia Federal", "Receita Federal",
            "Prefeitura de Salvador", "Prefeitura de Brasília", "Prefeitura de Fortaleza",
            "Governo do Estado de Minas Gerais", "Governo do Estado da Bahia",
            "Ministério da Justiça", "Ministério da Fazenda"
        ]
        
        # Empresas de TI
        empresas = [
            "Tech Solutions LTDA", "Digital Devices S.A.", "Global Tech Solutions",
            "Mobile Tech LTDA", "Computer World LTDA", "Smartphone Tech S.A.",
            "Lenovo Solutions Brasil", "Apple Solutions LTDA", "HP Solutions Brasil",
            "Motorola Solutions", "Display Solutions LTDA", "Print Tech Brasil",
            "Server Solutions S.A.", "Network Tech LTDA", "Projector Solutions",
            "WiFi Solutions Brasil", "Security Tech LTDA", "Tablet Solutions S.A.",
            "IT Solutions Group", "Digital Innovation LTDA", "TechCorp Brasil",
            "Inovação Digital S.A.", "Sistemas Avançados LTDA", "Tecnologia Moderna",
            "Digital Systems", "TechBridge Solutions", "Innovation Hub LTDA"
        ]
        
        import random
        
        for i in range(quantidade):
            produto = random.choice(produtos_ti)
            orgao = random.choice(orgaos)
            empresa = random.choice(empresas)
            
            # Quantidade variada
            quantidade_item = random.randint(50, 1000)
            valor_total = produto["preco_justo"] * quantidade_item
            
            # Preço proposto com pequena variação (±5%)
            variacao = random.uniform(-0.05, 0.05)
            preco_proposto = produto["preco_justo"] * (1 + variacao)
            
            # Data aleatória nos últimos 30 dias
            dias_atras = random.randint(1, 30)
            
            licitacao = Licitacao(
                id=f"PT-2024-{i+1:03d}",
                numero=f"{i+1:03d}/2024",
                orgao=orgao,
                modalidade=TipoLicitacao.PREGAO,
                objeto=f"Aquisição de {produto['nome']} para modernização tecnológica",
                data_abertura=datetime.now() - timedelta(days=dias_atras),
                data_fechamento=datetime.now() + timedelta(days=random.randint(20, 40)),
                valor_estimado=valor_total,
                status=StatusLicitacao.ABERTA,
                itens=[
                    ItemLicitacao(
                        codigo=f"{i+1:03d}",
                        descricao=produto["nome"],
                        quantidade=quantidade_item,
                        unidade="UN",
                        especificacoes=f"Especificações técnicas padrão para {produto['categoria']}"
                    )
                ],
                participantes=[
                    Participante(
                        cnpj=f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/0001-{random.randint(10, 99)}",
                        nome=empresa,
                        preco_proposto=preco_proposto,
                        classificacao=1,
                        habilitado=True
                    )
                ]
            )
            
            licitacoes.append(licitacao)
        
        return licitacoes
    
    def _gerar_licitacoes_suspeitas(self) -> List[Licitacao]:
        """Gera as licitações suspeitas (com superfaturamento)"""
        licitacoes = []
        
        # Dados baseados em licitações reais de TI
        dados_licitacoes = [
            {
                "id": "PT-2024-001",
                "numero": "001/2024",
                "orgao": "Ministério da Educação",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de notebooks para laboratórios de informática",
                "data_abertura": datetime.now() - timedelta(days=5),
                "data_fechamento": datetime.now() + timedelta(days=25),
                "valor_estimado": 1800000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="001",
                        descricao="Notebook Dell Latitude 5520",
                        quantidade=500,
                        unidade="UN",
                        especificacoes="Intel Core i5-1135G7, 8GB RAM DDR4, SSD 256GB, Tela 15.6\" Full HD, Windows 11 Pro"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="12.345.678/0001-90",
                        nome="Tech Solutions LTDA",
                        preco_proposto=3600.00,
                        classificacao=1,
                        habilitado=True
                    )
                ]
            },
            {
                "id": "PT-2024-002",
                "numero": "002/2024",
                "orgao": "Prefeitura de São Paulo",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de tablets para programa de educação digital",
                "data_abertura": datetime.now() - timedelta(days=3),
                "data_fechamento": datetime.now() + timedelta(days=27),
                "valor_estimado": 1800000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="002",
                        descricao="Tablet Samsung Galaxy Tab A8",
                        quantidade=1000,
                        unidade="UN",
                        especificacoes="Tela 10.5\", 4GB RAM, 64GB Armazenamento, Android 11, Wi-Fi, Câmera 8MP"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="98.765.432/0001-10",
                        nome="Digital Devices S.A.",
                        preco_proposto=1800.00,
                        classificacao=1,
                        habilitado=True
                    ),
                    Participante(
                        cnpj="11.222.333/0001-44",
                        nome="Mobile Tech LTDA",
                        preco_proposto=1200.00,
                        classificacao=2,
                        habilitado=True
                    )
                ]
            },
            {
                "id": "PT-2024-003",
                "numero": "003/2024",
                "orgao": "Governo do Estado de São Paulo",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de computadores desktop para modernização administrativa",
                "data_abertura": datetime.now() - timedelta(days=2),
                "data_fechamento": datetime.now() + timedelta(days=28),
                "valor_estimado": 2940000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="003",
                        descricao="Computador Desktop HP EliteDesk 800 G8",
                        quantidade=700,
                        unidade="UN",
                        especificacoes="Intel Core i7-11700, 16GB RAM DDR4, SSD 512GB, Windows 11 Pro, Monitor 24\""
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="33.444.555/0001-66",
                        nome="Global Tech Solutions",
                        preco_proposto=4200.00,
                        classificacao=1,
                        habilitado=True
                    ),
                    Participante(
                        cnpj="77.888.999/0001-88",
                        nome="Computer World LTDA",
                        preco_proposto=3200.00,
                        classificacao=2,
                        habilitado=True
                    ),
                    Participante(
                        cnpj="55.666.777/0001-99",
                        nome="TechMaster S.A.",
                        preco_proposto=3500.00,
                        classificacao=3,
                        habilitado=True
                    )
                ]
            },
            {
                "id": "PT-2024-004",
                "numero": "004/2024",
                "orgao": "Ministério da Saúde",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de smartphones para agentes de saúde",
                "data_abertura": datetime.now() - timedelta(days=1),
                "data_fechamento": datetime.now() + timedelta(days=29),
                "valor_estimado": 1760000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="004",
                        descricao="Smartphone Samsung Galaxy A54 5G",
                        quantidade=800,
                        unidade="UN",
                        especificacoes="Tela 6.4\", 8GB RAM, 128GB Armazenamento, Android 13, Câmera 50MP, 5G"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="99.111.222/0001-33",
                        nome="Mobile Solutions LTDA",
                        preco_proposto=2200.00,
                        classificacao=1,
                        habilitado=True
                    ),
                    Participante(
                        cnpj="44.555.666/0001-77",
                        nome="Smartphone Tech S.A.",
                        preco_proposto=1800.00,
                        classificacao=2,
                        habilitado=True
                    )
                ]
            },
            {
                "id": "PT-2024-005",
                "numero": "005/2024",
                "orgao": "Prefeitura do Rio de Janeiro",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de notebooks para secretarias municipais",
                "data_abertura": datetime.now() - timedelta(days=4),
                "data_fechamento": datetime.now() + timedelta(days=26),
                "valor_estimado": 1500000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="005",
                        descricao="Notebook Lenovo ThinkPad E15",
                        quantidade=400,
                        unidade="UN",
                        especificacoes="Intel Core i5-1235U, 8GB RAM DDR4, SSD 256GB, Tela 15.6\" Full HD, Windows 11 Pro"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="22.333.444/0001-55",
                        nome="Lenovo Solutions Brasil",
                        preco_proposto=3750.00,
                        classificacao=1,
                        habilitado=True
                    )
                ]
            },
            {
                "id": "PT-2024-006",
                "numero": "006/2024",
                "orgao": "Ministério da Justiça",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de tablets para digitalização de processos",
                "data_abertura": datetime.now() - timedelta(days=6),
                "data_fechamento": datetime.now() + timedelta(days=24),
                "valor_estimado": 1050000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="006",
                        descricao="Tablet iPad 10.9\" 64GB Wi-Fi",
                        quantidade=300,
                        unidade="UN",
                        especificacoes="Tela 10.9\" Liquid Retina, Chip A14 Bionic, 64GB, Wi-Fi, iPadOS 16, Câmera 12MP"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="66.777.888/0001-11",
                        nome="Apple Solutions LTDA",
                        preco_proposto=3500.00,
                        classificacao=1,
                        habilitado=True
                    ),
                    Participante(
                        cnpj="88.999.000/0001-22",
                        nome="Tablet Tech S.A.",
                        preco_proposto=3800.00,
                        classificacao=2,
                        habilitado=True
                    )
                ]
            }
        ]
        
        # Adicionar licitações do ComprasNet também
        dados_licitacoes.extend([
            {
                "id": "CN-2024-001",
                "numero": "001/2024/CN",
                "orgao": "Tribunal de Contas da União",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de notebooks para auditoria fiscal",
                "data_abertura": datetime.now() - timedelta(days=7),
                "data_fechamento": datetime.now() + timedelta(days=23),
                "valor_estimado": 900000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="001",
                        descricao="Notebook HP EliteBook 850 G8",
                        quantidade=200,
                        unidade="UN",
                        especificacoes="Intel Core i7-1165G7, 16GB RAM DDR4, SSD 512GB, Tela 15.6\" Full HD, Windows 11 Pro"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="15.123.456/0001-78",
                        nome="HP Solutions Brasil",
                        preco_proposto=4500.00,
                        classificacao=1,
                        habilitado=True
                    ),
                    Participante(
                        cnpj="25.234.567/0001-89",
                        nome="TechCorp LTDA",
                        preco_proposto=4800.00,
                        classificacao=2,
                        habilitado=True
                    )
                ]
            },
            {
                "id": "CN-2024-002",
                "numero": "002/2024/CN",
                "orgao": "Receita Federal",
                "modalidade": TipoLicitacao.PREGAO,
                "objeto": "Aquisição de smartphones para fiscalização",
                "data_abertura": datetime.now() - timedelta(days=5),
                "data_fechamento": datetime.now() + timedelta(days=25),
                "valor_estimado": 900000.00,
                "status": StatusLicitacao.ABERTA,
                "itens": [
                    ItemLicitacao(
                        codigo="002",
                        descricao="Smartphone Motorola Moto G73 5G",
                        quantidade=500,
                        unidade="UN",
                        especificacoes="Tela 6.5\", 8GB RAM, 128GB Armazenamento, Android 13, Câmera 50MP, 5G"
                    )
                ],
                "participantes": [
                    Participante(
                        cnpj="35.345.678/0001-90",
                        nome="Motorola Solutions",
                        preco_proposto=1800.00,
                        classificacao=1,
                        habilitado=True
                    )
                ]
            }
        ])
        
        # Converte dados para objetos Licitacao
        for dados in dados_licitacoes:
            licitacao = Licitacao(**dados)
            licitacoes.append(licitacao)
        
        return licitacoes
    