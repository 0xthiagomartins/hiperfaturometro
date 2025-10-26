# 🚀 Hiperfaturômetro Backend

Sistema de detecção de hiperfaturamento em licitações públicas usando inteligência artificial.

## 📁 Estrutura do Projeto

```
backend/
├── api/                    # API FastAPI (comunicação com frontend)
│   ├── main.py            # Aplicação FastAPI
│   ├── models.py          # Modelos Pydantic
│   ├── routes.py          # Endpoints da API
│   └── data_service.py    # Serviço de dados
├── src/                   # Lógica de negócio
│   ├── tracker/           # HiperfaturamentoTracker
│   │   └── hiperfaturamento_tracker.py
│   ├── models/            # Modelos de dados
│   │   ├── licitacao.py
│   │   └── analise.py
│   ├── services/          # Serviços
│   │   ├── licitacao_collector.py
│   │   └── hiperfaturamento_analyzer.py
│   └── utils/             # Utilitários
├── data/                  # Dados processados
│   ├── licitacoes.json
│   ├── analises.json
│   └── casos_processados.json
├── tests/                 # Testes unitários
│   └── tracker/
├── main.py               # Ponto de entrada da API
├── run_tracker.py        # Script para executar o tracker
└── requirements.txt      # Dependências
```

## 🎯 Arquitetura

### **Separação de Responsabilidades:**

1. **API (`/api`)**: Interface para o frontend
   - Endpoints REST
   - Validação de dados
   - Consome dados processados

2. **Tracker (`/src/tracker`)**: Serviço interno
   - Coleta de licitações
   - Análise de hiperfaturamento
   - Processamento de dados

3. **Data (`/data`)**: Armazenamento
   - Dados processados
   - Casos analisados
   - Estatísticas

## 🔧 Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar testes
pytest

# Executar API
python main.py

# Executar tracker
python run_tracker.py
```

## 🚀 Como Usar

### **1. Executar a API**
```bash
python main.py
```
A API estará disponível em: http://localhost:8000

### **2. Executar o Tracker**
```bash
python run_tracker.py
```
O tracker irá:
- Coletar licitações dos últimos 7 dias
- Analisar cada licitação
- Salvar resultados em `/data`

### **3. Endpoints da API**

- `GET /api/statistics` - Estatísticas gerais
- `GET /api/cases` - Lista de casos
- `GET /api/cases/{id}` - Detalhes de um caso
- `GET /api/breaking-news` - Notícias urgentes
- `GET /api/health` - Health check

## 🤖 Algoritmo de Detecção

### **Critérios de Hiperfaturamento:**

1. **Preço Excessivo** (Peso: 40%)
   - Threshold: 30% acima do preço de mercado
   - Comparação com preços de referência

2. **Especificações Tailor-Made** (Peso: 30%)
   - Análise de NLP das especificações
   - Detecção de palavras suspeitas
   - Especificações muito específicas

3. **Empresa Cartel** (Peso: 20%)
   - Histórico de vitórias no órgão
   - Taxa de vitórias > 70%

4. **Baixa Concorrência** (Peso: 10%)
   - Menos de 2 participantes
   - Indica possível conluio

### **Score Final:**
- **0-40**: Baixo risco
- **40-60**: Médio risco  
- **60-80**: Alto risco
- **80-100**: Crítico

## 🧪 Testes

### **Executar Todos os Testes:**
```bash
pytest
```

### **Executar com Coverage:**
```bash
pytest --cov=src
```

### **Executar Testes Específicos:**
```bash
pytest tests/tracker/test_hiperfaturamento_tracker.py
pytest tests/tracker/test_hiperfaturamento_analyzer.py
```

## 📊 Dados Processados

### **Arquivos Gerados:**

1. **`licitacoes.json`**: Licitações coletadas
2. **`analises.json`**: Análises de hiperfaturamento
3. **`casos_processados.json`**: Casos formatados para a API

### **Estrutura dos Dados:**

```json
{
  "id": "LIC-2024-001",
  "titulo": "Superfaturamento em Notebooks",
  "orgao": "Ministério da Educação",
  "nivel_risco": "Alto",
  "risk_score": 75,
  "economia_potencial": 50000.00,
  "evidencias": ["Preço 60% acima do mercado"]
}
```

## 🔄 Fluxo de Dados

1. **Coleta**: `LicitacaoCollector` busca licitações
2. **Análise**: `HiperfaturamentoAnalyzer` analisa cada licitação
3. **Processamento**: `HiperfaturamentoTracker` processa resultados
4. **Armazenamento**: Dados salvos em JSON
5. **API**: `DataService` consome dados processados

## 🎯 Próximos Passos

### **Melhorias Planejadas:**

1. **Fontes Reais de Dados**
   - Integração com APIs oficiais
   - Web scraping de fornecedores
   - Base de dados histórica

2. **IA Avançada**
   - Modelos de ML reais
   - Treinamento com dados históricos
   - Validação cruzada

3. **Validação**
   - Parcerias com órgãos de controle
   - Sistema de feedback
   - Auditoria externa

## 🚨 Limitações Atuais

- **Dados Mockados**: Fontes simuladas
- **Preços de Mercado**: Base de dados limitada
- **Análise de NLP**: Implementação básica
- **Validação**: Sem verificação externa

## 📝 Logs

Os logs são salvos em:
- **Console**: Saída padrão
- **Arquivo**: `tracker.log`

Níveis de log:
- **INFO**: Operações normais
- **WARNING**: Situações suspeitas
- **ERROR**: Erros de processamento

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente testes
4. Execute `pytest`
5. Abra um Pull Request

## 📄 Licença

Este projeto é parte do Hackathon Devs de Impacto 2025.