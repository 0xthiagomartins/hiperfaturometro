"""
Serviços de Backend
Contém toda a lógica de processamento e integração com APIs
"""

import json
import os
from typing import List, Dict, Any
from src.business_rules import BusinessRules

class BackendServices:
    """Classe contendo os serviços de backend"""
    
    def __init__(self):
        self.data_path = "data/examples"
        self.business_rules = BusinessRules()
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Carrega arquivo JSON dos dados mockados"""
        try:
            file_path = os.path.join(self.data_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado")
            return {}
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON do arquivo {filename}")
            return {}
    
    def process_licitacao_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados brutos de licitação aplicando regras de negócio"""
        # Aplicar regras de negócio
        processed_data = raw_data.copy()
        
        # Calcular score de risco
        processed_data['risk_score'] = self.business_rules.calculate_risk_score(raw_data)
        processed_data['risk_level'] = self.business_rules.determine_risk_level(processed_data['risk_score'])
        
        # Calcular economia potencial
        if all(key in raw_data for key in ['preco_edital', 'preco_mercado', 'quantidade']):
            processed_data['economia_potencial'] = self.business_rules.calculate_potential_savings(
                raw_data['preco_edital'], 
                raw_data['preco_mercado'], 
                raw_data['quantidade']
            )
        
        # Determinar se é suspeito
        processed_data['is_suspicious'] = self.business_rules.is_suspicious_case(raw_data)
        
        # Determinar prioridade
        processed_data['priority_level'] = self.business_rules.get_priority_level(processed_data)
        
        return processed_data
    
    def get_processed_cases(self) -> List[Dict[str, Any]]:
        """Retorna casos processados com regras de negócio aplicadas"""
        dados = self._load_json_file("casos_reais.json")
        casos_brutos = dados.get("casos_investigacao", [])
        
        casos_processados = []
        for caso in casos_brutos:
            caso_processado = self.process_licitacao_data(caso)
            casos_processados.append(caso_processado)
        
        return casos_processados
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas baseadas nos dados processados"""
        casos = self.get_processed_cases()
        
        total_casos = len(casos)
        casos_suspeitos = sum(1 for caso in casos if caso.get('is_suspicious', False))
        economia_total = sum(caso.get('economia_potencial', 0) for caso in casos)
        taxa_suspeicao = (casos_suspeitos / total_casos * 100) if total_casos > 0 else 0
        
        return {
            'total_licitacoes_analisadas': total_casos,
            'casos_suspeitos': casos_suspeitos,
            'economia_potencial_total': economia_total,
            'taxa_suspeicao': round(taxa_suspeicao, 1)
        }
    
    def get_cases_by_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa casos por nível de prioridade"""
        casos = self.get_processed_cases()
        
        by_priority = {
            'Crítica': [],
            'Alta': [],
            'Média': [],
            'Baixa': []
        }
        
        for caso in casos:
            priority = caso.get('priority_level', 'Baixa')
            by_priority[priority].append(caso)
        
        return by_priority
    
    def get_cases_by_risk_level(self) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa casos por nível de risco"""
        casos = self.get_processed_cases()
        
        by_risk = {
            'Alto': [],
            'Médio': [],
            'Baixo': []
        }
        
        for caso in casos:
            risk_level = caso.get('risk_level', 'Baixo')
            by_risk[risk_level].append(caso)
        
        return by_risk
