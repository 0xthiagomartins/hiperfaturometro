# 🚀 API PNCP - Guia para Frontend

## 📍 Endpoint Disponível

```
GET http://localhost:8000/api/pncp/analisar
```

## 📥 Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `dias_atras` | number | 90 | Quantos dias voltar na busca (1-365) |

## 📤 Resposta

```json
{
  "success": true,
  "message": "5 licitações analisadas com sucesso",
  "data": {
    "licitacoes": [
      {
        "numeroControlePNCP": "00038.000001/2024-19",
        "anoCompra": 2024,
        "numeroCompra": "00001",
        "modalidadeNome": "Pregão Eletrônico",
        "objetoCompra": "Aquisição de notebooks para a administração pública",
        "valorTotalEstimado": 150000.00,
        "valorTotalHomologado": 142000.00,
        "orgaoEntidade": {
          "cnpj": "00394460005887",
          "razaoSocial": "Prefeitura Municipal",
          "uf": "SP"
        }
      }
    ],
    "total": 5
  },
  "timestamp": "2025-10-26T10:30:00"
}
```

## 💻 Exemplos de Uso

### JavaScript / React

```javascript
// Função para buscar licitações
async function buscarLicitacoes(diasAtras = 90) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/pncp/analisar?dias_atras=${diasAtras}`
    );
    
    const data = await response.json();
    
    if (data.success) {
      console.log(`Total: ${data.data.total} licitações`);
      return data.data.licitacoes;
    } else {
      console.error(data.message);
      return [];
    }
  } catch (error) {
    console.error('Erro:', error);
    return [];
  }
}

// Usar
const licitacoes = await buscarLicitacoes(30); // últimos 30 dias
```

### React Component

```jsx
import { useState, useEffect } from 'react';

function LicitacoesPNCP() {
  const [licitacoes, setLicitacoes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dias, setDias] = useState(90);

  const buscarLicitacoes = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/pncp/analisar?dias_atras=${dias}`
      );
      const data = await response.json();
      
      if (data.success) {
        setLicitacoes(data.data.licitacoes);
      }
    } catch (error) {
      console.error('Erro ao buscar licitações:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Licitações PNCP</h1>
      
      <div>
        <input 
          type="number" 
          value={dias} 
          onChange={(e) => setDias(e.target.value)}
          placeholder="Dias"
        />
        <button onClick={buscarLicitacoes} disabled={loading}>
          {loading ? 'Buscando...' : 'Buscar Licitações'}
        </button>
      </div>

      {loading && <p>Carregando...</p>}

      <div>
        {licitacoes.map((lic, index) => (
          <div key={index} className="licitacao-card">
            <h3>{lic.objetoCompra}</h3>
            <p>Órgão: {lic.orgaoEntidade.razaoSocial}</p>
            <p>Valor: R$ {lic.valorTotalEstimado?.toLocaleString('pt-BR')}</p>
            <p>UF: {lic.orgaoEntidade.uf}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LicitacoesPNCP;
```

### Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

// Buscar licitações
async function buscarLicitacoes(diasAtras = 90) {
  try {
    const { data } = await api.get('/pncp/analisar', {
      params: { dias_atras: diasAtras }
    });
    
    return data.data.licitacoes;
  } catch (error) {
    console.error('Erro:', error.response?.data || error.message);
    return [];
  }
}

// Usar
const licitacoes = await buscarLicitacoes(60);
```

### Fetch com async/await

```javascript
async function getLicitacoes(dias = 90) {
  const url = `http://localhost:8000/api/pncp/analisar?dias_atras=${dias}`;
  
  const response = await fetch(url);
  const json = await response.json();
  
  return json.data.licitacoes;
}

// Usar
getLicitacoes(30).then(licitacoes => {
  console.log(licitacoes);
});
```

## 🎨 Estrutura dos Dados

### Licitação
```javascript
{
  numeroControlePNCP: string,        // "00038.000001/2024-19"
  anoCompra: number,                 // 2024
  numeroCompra: string,              // "00001"
  sequencialCompra: number,          // 1
  modalidadeNome: string,            // "Pregão Eletrônico"
  objetoCompra: string,              // Descrição da licitação
  valorTotalEstimado: number,        // 150000.00
  valorTotalHomologado: number,      // 142000.00 (pode ser null)
  orgaoEntidade: {
    cnpj: string,                    // "00394460005887"
    razaoSocial: string,             // Nome do órgão
    uf: string                       // "SP"
  }
}
```

## ⚠️ Observações Importantes

### Tempo de Resposta
- A API pode demorar **30 segundos a 5 minutos** dependendo do número de licitações
- Configure timeout adequado no frontend (ex: 300000ms = 5min)

### Loading State
Sempre mostre um loading indicator:
```javascript
setLoading(true);
// fazer requisição
setLoading(false);
```

### Tratamento de Erros
```javascript
try {
  const response = await fetch(url);
  const data = await response.json();
  
  if (!data.success) {
    // Mostrar mensagem de erro
    alert(data.message);
  }
} catch (error) {
  // Erro de conexão
  alert('Erro ao conectar com o servidor');
}
```

### CORS
Se tiver problema de CORS, o backend já está configurado para aceitar requisições de qualquer origem.

## 🚀 Exemplo Completo React + TypeScript

```typescript
import { useState } from 'react';

interface Licitacao {
  numeroControlePNCP: string;
  anoCompra: number;
  objetoCompra: string;
  valorTotalEstimado: number;
  valorTotalHomologado?: number;
  orgaoEntidade: {
    razaoSocial: string;
    cnpj: string;
    uf: string;
  };
}

interface APIResponse {
  success: boolean;
  message: string;
  data: {
    licitacoes: Licitacao[];
    total: number;
  };
}

export function LicitacoesPNCP() {
  const [licitacoes, setLicitacoes] = useState<Licitacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const buscarLicitacoes = async (dias: number = 90) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/pncp/analisar?dias_atras=${dias}`,
        { 
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        }
      );

      const data: APIResponse = await response.json();

      if (data.success) {
        setLicitacoes(data.data.licitacoes);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Erro ao buscar licitações');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Licitações PNCP</h1>

      <button 
        onClick={() => buscarLicitacoes(30)}
        disabled={loading}
        className="btn-primary"
      >
        {loading ? 'Buscando...' : 'Buscar Últimos 30 dias'}
      </button>

      {error && <div className="error">{error}</div>}

      {loading && <div className="spinner">Carregando...</div>}

      <div className="licitacoes-grid">
        {licitacoes.map((lic, idx) => (
          <div key={idx} className="card">
            <h3>{lic.objetoCompra}</h3>
            <div className="info">
              <p><strong>Órgão:</strong> {lic.orgaoEntidade.razaoSocial}</p>
              <p><strong>UF:</strong> {lic.orgaoEntidade.uf}</p>
              <p><strong>Valor Estimado:</strong> R$ {lic.valorTotalEstimado.toLocaleString('pt-BR')}</p>
              {lic.valorTotalHomologado && (
                <p><strong>Valor Homologado:</strong> R$ {lic.valorTotalHomologado.toLocaleString('pt-BR')}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 📊 Dicas de UX

### 1. Loading com progresso
```javascript
<div className="loading">
  <p>Buscando licitações...</p>
  <p>Isso pode levar alguns minutos</p>
  <div className="spinner"></div>
</div>
```

### 2. Mensagem quando não há resultados
```javascript
{licitacoes.length === 0 && !loading && (
  <p>Nenhuma licitação de tecnologia encontrada no período</p>
)}
```

### 3. Formatação de valores
```javascript
// Formatar moeda
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

<p>{formatarMoeda(licitacao.valorTotalEstimado)}</p>
```

### 4. Filtro por período
```javascript
<select onChange={(e) => buscarLicitacoes(Number(e.target.value))}>
  <option value="7">Últimos 7 dias</option>
  <option value="30">Últimos 30 dias</option>
  <option value="90">Últimos 90 dias</option>
  <option value="180">Últimos 6 meses</option>
</select>
```

## 🔧 Testando

### 1. Iniciar o servidor
```bash
cd /home/arthur/Downloads/hackaton/hiperfaturometro
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Testar no navegador
```
http://localhost:8000/api/pncp/analisar?dias_atras=30
```

### 3. Testar com cURL
```bash
curl "http://localhost:8000/api/pncp/analisar?dias_atras=30"
```

## 📝 Resumo Rápido

**URL:** `http://localhost:8000/api/pncp/analisar?dias_atras=90`

**Método:** GET

**Retorna:** JSON com lista de licitações de tecnologia

**Tempo:** 30s a 5min (mostre loading!)

**Dados principais:**
- `objetoCompra` - Descrição da licitação
- `valorTotalEstimado` - Valor em reais
- `orgaoEntidade.razaoSocial` - Nome do órgão
- `orgaoEntidade.uf` - Estado

Pronto para usar! 🚀
