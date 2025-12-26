# estatab API

FastAPI wrapper for the estatab statistical experimentation engine.

## Overview

This API provides HTTP endpoints to execute statistical analyses for A/B/n experiments using the estatab package. It handles:

- Sequential group testing with alpha spending functions
- Multiple comparison corrections (Bonferroni, Holm-Bonferroni, Šidák)
- Both fixed and sequential methodologies
- Numeric and conversion metrics

## Endpoints

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

### POST /v1/analyze

Execute statistical analysis for an experiment.

**Request Body:**

```json
{
  "config": {
    "nome_metrica": "latencia_ms",
    "tipo_metrica": "numerica",
    "tamanho_amostral_calculado": 10000,
    "intencao_teste": "detectar_reducao",
    "alfa": 0.05,
    "metodologia": "testes_sequenciais",
    "tipo_correcao": "Holm-Bonferroni",
    "data_inicio_experimento": "2025-03-01",
    "data_fim_experimento": "2025-05-01",
    "fator_inflacao": "O'Brien-Fleming",
    "funcao_gasto_alfa": "obrien_fleming",
    "valor_lambda": 1
  },
  "variantes": [
    {
      "nome_variante": "Controle",
      "numero_amostras": 5000,
      "valor_media": 220,
      "desvio_padrao": 45,
      "variante_controle": true
    },
    {
      "nome_variante": "Tratamento B",
      "numero_amostras": 5000,
      "valor_media": 210,
      "desvio_padrao": 42,
      "variante_controle": false
    }
  ]
}
```

**Response:**

```json
{
  "nomeMetrica": "latencia_ms",
  "intencao": "detectar_reducao",
  "metodologia": "testes_sequenciais",
  "alfaEfetivo": 0.04,
  "comparacoes": [
    {
      "comparacao": "Tratamento B vs Controle",
      "teste": "Teste Z",
      "estatistica": -2.45,
      "pvalor": 0.014,
      "pvalorAjustado": 0.014,
      "efeito": -10,
      "rejeitaH0Corrigido": true,
      "conclusaoCorrigida": "redução detectada"
    }
  ],
  "sequenciais": {
    "alfaAcumulado": 0.04,
    "valorFatorInflacao": 1.15,
    "completudeExperimento": 1.0
  },
  "conclusao_final": "redução detectada"
}
```

## Development

### Local Setup

```bash
# Install dependencies
pip install -e ".[test]"

# Run server
python main.py
```

Server will be available at `http://localhost:8000`

### Testing

```bash
# Run tests
pytest tests/ -v

# Test health endpoint
curl http://localhost:8000/health

# Test analyze endpoint
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

## Docker

```bash
# Build image
docker build -t estatab-api .

# Run container
docker run -p 8000:8000 estatab-api
```
