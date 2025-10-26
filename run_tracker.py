"""
Script para executar o HiperfaturamentoTracker
Pode ser executado manualmente ou via cron job
"""

import logging
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.tracker.hiperfaturamento_tracker import HiperfaturamentoTracker

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal para executar o tracker"""
    try:
        logger.info("Iniciando HiperfaturamentoTracker...")
        
        # Inicializa o tracker
        tracker = HiperfaturamentoTracker()
        
        # Executa o ciclo completo (últimos 7 dias)
        relatorio = tracker.executar_ciclo_completo(dias_retroativos=7)
        
        # Exibe relatório
        logger.info("=== RELATÓRIO DE EXECUÇÃO ===")
        logger.info(f"Data de execução: {relatorio['data_execucao']}")
        logger.info(f"Licitações coletadas: {relatorio['licitacoes_coletadas']}")
        logger.info(f"Licitações analisadas: {relatorio['licitacoes_analisadas']}")
        logger.info(f"Casos suspeitos: {relatorio['casos_suspeitos']}")
        
        if relatorio['erros']:
            logger.warning(f"Erros encontrados: {len(relatorio['erros'])}")
            for erro in relatorio['erros']:
                logger.error(f"  - {erro}")
        
        # Exibe estatísticas finais
        stats = tracker.obter_estatisticas()
        logger.info("=== ESTATÍSTICAS ATUAIS ===")
        logger.info(f"Total de licitações analisadas: {stats['total_licitacoes_analisadas']}")
        logger.info(f"Casos suspeitos: {stats['casos_suspeitos']}")
        logger.info(f"Valor superfaturado total: R$ {stats['valor_superfaturado_total']:,.2f}")
        logger.info(f"Taxa de suspeição: {stats['taxa_suspeicao']:.1f}%")
        
        logger.info("HiperfaturamentoTracker finalizado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro fatal no HiperfaturamentoTracker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
