"""
Serviço PNCP - Consulta de Licitações
"""

import requests
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any, Optional


class PNCPCompleto:
    """Consulta COMPLETA: Licitação + Itens + Vencedor + Empresa + Sócios"""
    
    def __init__(self):
        self.base_url = "https://pncp.gov.br/api/consulta/v1"
        self.headers = {'Accept': 'application/json'}
    
    def buscar_contratacoes(self, dias_atras=90):
        """Busca contratações usando endpoint e todos os parâmetros corretos"""
        print("\n🔍 Buscando licitações de tecnologia...")
        
        data_final = datetime.now()
        data_inicial = data_final - timedelta(days=dias_atras)
        
        hoje = datetime.now()
        if data_final > hoje:
            data_final = hoje
        if data_inicial > hoje:
            data_inicial = hoje - timedelta(days=dias_atras)
        
        url = f"{self.base_url}/contratacoes/publicacao"
        
        params = {
            'dataInicial': data_inicial.strftime('%Y%m%d'),
            'dataFinal': data_final.strftime('%Y%m%d'),
            'codigoModalidadeContratacao': 5,
            'pagina': 1,
            'tamanhoPagina': 50
        }
        
        print(f"   Período: {data_inicial.strftime('%d/%m/%Y')} até {data_final.strftime('%d/%m/%Y')}")
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            
            print(f"   URL da Requisição: {response.request.url}")
            
            if response.status_code == 400:
                print(f"\n❌ ERRO 400 - Requisição inválida")
                print(f"   Resposta da API: {response.text[:500]}")
                return []
            
            response.raise_for_status()
            
            dados = response.json()
            
            if dados and 'data' in dados:
                items = dados['data']
                
                items_tech = [
                    item for item in items
                    if any(termo in str(item.get('objetoCompra', '')).lower()
                          for termo in ['notebook', 'computador', 'tablet', 'equipamento', 'software'])
                ]
                
                print(f"✅ {len(items_tech)} licitações de tecnologia encontradas (na modalidade Pregão)")
                return items_tech[:5]
                
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ Erro HTTP: {http_err} - {response.text}")
        except Exception as e:
            print(f"❌ Erro ao buscar contratações: {e}")
        
        return []

    def obter_detalhes_completos(self, contratacao):
        """Obtém TODOS os detalhes de uma contratação"""
        ano = contratacao.get('anoCompra')
        sequencial = contratacao.get('sequencialCompra')
        cnpj = contratacao.get('orgaoEntidade', {}).get('cnpj')
        
        if not all([ano, sequencial, cnpj]):
            print(f"⚠️  Dados incompletos para buscar detalhes")
            return contratacao
        
        print(f"\n🔍 Buscando detalhes completos para {cnpj}-{ano}-{sequencial}...")
        
        url = f"{self.base_url}/orgaos/{cnpj}/compras/{ano}/{sequencial}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            detalhes = response.json()
            print(f"✅ Detalhes obtidos")
            
            contratacao.update(detalhes)
            return contratacao
            
        except Exception as e:
            print(f"⚠️  Detalhes não disponíveis: {str(e)[:100]}")
            return contratacao
    
    def obter_itens(self, contratacao):
        """Obtém itens da contratação"""
        print(f"📦 Buscando itens...")
        
        ano = contratacao.get('anoCompra')
        sequencial = contratacao.get('sequencialCompra')
        cnpj = contratacao.get('orgaoEntidade', {}).get('cnpj')
        
        if not all([ano, sequencial, cnpj]):
            print(f"⚠️  Dados incompletos para buscar itens")
            return []
        
        url = f"{self.base_url}/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            itens_data = response.json()
            itens = itens_data.get('data', []) if isinstance(itens_data, dict) else itens_data
            
            print(f"✅ {len(itens)} itens encontrados")
            return itens
            
        except Exception as e:
            print(f"⚠️  Itens não disponíveis: {e}")
            return []
    
    def obter_resultado(self, contratacao, numero_item):
        """Obtém resultado/vencedor de um item"""
        ano = contratacao.get('anoCompra')
        sequencial = contratacao.get('sequencialCompra')
        cnpj = contratacao.get('orgaoEntidade', {}).get('cnpj')
        
        if not all([ano, sequencial, cnpj]):
            return []
        
        url = f"{self.base_url}/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numero_item}/resultados"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            resultados_data = response.json()
            return resultados_data.get('data', []) if isinstance(resultados_data, dict) else resultados_data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"      ℹ️  Nenhum resultado de vencedor encontrado para o item {numero_item}.")
            else:
                print(f"      ⚠️  Erro HTTP ao buscar resultado: {e}")
        except Exception:
            pass 

        return []
    
    def consultar_empresa(self, cnpj):
        """Consulta dados da empresa via ReceitaWS"""
        print(f"🏢 Consultando empresa {cnpj}...")
        
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        try:
            time.sleep(20) 
            
            url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                if dados.get('status') != 'ERROR':
                    print(f"✅ Dados da empresa obtidos")
                    return {
                        'razao_social': dados.get('nome'),
                        'situacao': dados.get('situacao'),
                        'capital_social': dados.get('capital_social'),
                        'socios': [
                            {
                                'nome': s.get('nome'),
                                'qualificacao': s.get('qual')
                            }
                            for s in dados.get('qsa', [])
                        ]
                    }
            elif response.status_code == 429:
                print("⚠️  Limite de requisições da ReceitaWS atingido. Aguardando...")
                time.sleep(60)
                return self.consultar_empresa(cnpj) 

        except Exception as e:
            print(f"      ⚠️  Erro ao consultar empresa: {e}")
        
        print(f"⚠️  Dados da empresa não disponíveis")
        return None
    
    def analisar_licitacao_completa(self, contratacao, idx):
        """Análise COMPLETA de uma licitação"""
        print(f"\n{'='*75}")
        print(f"LICITAÇÃO {idx} - ANÁLISE COMPLETA")
        print(f"{'='*75}")
        
        contratacao = self.obter_detalhes_completos(contratacao)
        
        print(f"\n📋 DADOS DA LICITAÇÃO:")
        print(f"   Número PNCP: {contratacao.get('numeroControlePNCP', 'N/D')}")
        print(f"   Ano/Número: {contratacao.get('anoCompra')}/{contratacao.get('numeroCompra')}")
        print(f"   Modalidade: {contratacao.get('modalidadeNome', 'N/D')}")
        print(f"   Objeto: {contratacao.get('objetoCompra', 'N/D')[:120]}...")
        
        print(f"\n💰 VALORES:")
        valor_total = contratacao.get('valorTotalEstimado', 0)
        print(f"   Estimado: R$ {valor_total:,.2f}")
        
        if contratacao.get('valorTotalHomologado'):
            print(f"   Homologado: R$ {contratacao.get('valorTotalHomologado', 0):,.2f}")
        
        orgao = contratacao.get('orgaoEntidade', {})
        print(f"\n🏛️  ÓRGÃO:")
        print(f"   {orgao.get('razaoSocial', 'N/D')}")
        print(f"   CNPJ: {orgao.get('cnpj', 'N/D')}")
        print(f"   UF: {orgao.get('uf', 'N/D')}")
        
        itens = self.obter_itens(contratacao)
        
        if itens:
            print(f"\n📦 ITENS DA CONTRATAÇÃO (exibindo até 3 de {len(itens)}):")
            for i, item in enumerate(itens[:3], 1):
                print(f"\n   {i}. {item.get('descricao', 'N/D')[:80]}")
                print(f"      Quantidade: {item.get('quantidade', 0)}")
                print(f"      Valor Unitário Estimado: R$ {item.get('valorUnitarioEstimado', 0):,.2f}")
                print(f"      Valor Total Estimado: R$ {item.get('valorTotal', 0):,.2f}")
                
                numero_item = item.get('numeroItem')
                if numero_item:
                    resultados = self.obter_resultado(contratacao, numero_item)
                    
                    if resultados:
                        for fornecedor in resultados[:1]: 
                                print(f"\n      🏆 VENCEDOR DO ITEM:")
                                print(f"         {fornecedor.get('nomeRazaoSocialFornecedor', 'N/D')}")
                                print(f"         CNPJ/CPF: {fornecedor.get('niFornecedor', 'N/D')}")
                                print(f"         Valor Ofertado: R$ {fornecedor.get('valorTotal', 0):,.2f}")
                                
                                cnpj_fornecedor = fornecedor.get('niFornecedor')
                                if cnpj_fornecedor and len(cnpj_fornecedor) == 14:
                                    empresa = self.consultar_empresa(cnpj_fornecedor)
                                    
                                    if empresa and empresa.get('socios'):
                                        print(f"\n         👥 SÓCIOS (até 3):")
                                        for socio in empresa['socios'][:3]:
                                            print(f"            • {socio.get('nome', 'N/D')} ({socio.get('qualificacao', '')})")
        
        return contratacao
