"""
Regras de Negócio
Contém toda a lógica de negócio da aplicação
"""

class BusinessRules:
    """Classe contendo as regras de negócio do Hiperfaturômetro"""
    
    @staticmethod
    def calculate_risk_score(caso):
        """Calcula o score de risco baseado nas evidências"""
        score = 0
        
        # Fatores de risco
        if caso.get('diferenca_percentual', 0) > 200:
            score += 40
        elif caso.get('diferenca_percentual', 0) > 100:
            score += 25
        elif caso.get('diferenca_percentual', 0) > 50:
            score += 15
        
        # Histórico de vitórias consecutivas
        if caso.get('historico_vitorias', 0) > 10:
            score += 30
        elif caso.get('historico_vitorias', 0) > 5:
            score += 20
        elif caso.get('historico_vitorias', 0) > 2:
            score += 10
        
        # Número de participantes
        if caso.get('participantes', 0) <= 2:
            score += 20
        elif caso.get('participantes', 0) <= 3:
            score += 10
        
        # Prazo de entrega suspeito
        if caso.get('prazo_entrega_dias', 0) < 15:
            score += 15
        elif caso.get('prazo_entrega_dias', 0) < 30:
            score += 10
        
        return min(score, 100)  # Máximo 100
    
    @staticmethod
    def determine_risk_level(score):
        """Determina o nível de risco baseado no score"""
        if score >= 80:
            return "Alto"
        elif score >= 50:
            return "Médio"
        else:
            return "Baixo"
    
    @staticmethod
    def calculate_potential_savings(valor_edital, preco_mercado, quantidade):
        """Calcula a economia potencial"""
        diferenca_por_unidade = valor_edital - preco_mercado
        return diferenca_por_unidade * quantidade
    
    @staticmethod
    def is_suspicious_case(caso):
        """Determina se um caso é suspeito baseado nas regras"""
        score = BusinessRules.calculate_risk_score(caso)
        return score >= 50
    
    @staticmethod
    def get_priority_level(caso):
        """Determina o nível de prioridade para investigação"""
        score = BusinessRules.calculate_risk_score(caso)
        economia = caso.get('economia_potencial', 0)
        
        if score >= 80 and economia > 1000000:
            return "Crítica"
        elif score >= 60 and economia > 500000:
            return "Alta"
        elif score >= 40:
            return "Média"
        else:
            return "Baixa"
