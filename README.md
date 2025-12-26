# EstatAB

![Last release](https://img.shields.io/badge/release-0.1.0-green.svg "Latest release: 0.1.0")
![Python](https://img.shields.io/badge/Python-3.11-blue.svg "Python")

**Plataforma corporativa de experimentação estatística** com testes sequenciais, controle rigoroso de significância e decisões auditáveis.

## Visão Geral

O **estatab** é uma plataforma completa para execução e análise de experimentos A/B/n com rigor estatístico adequado para ambientes corporativos e regulados. A solução combina:

- **Motor estatístico Python** (`src/estatab`) - Pacote core com implementação de testes de hipótese
- **API REST** (`apps/api`) - Wrapper FastAPI para acesso via HTTP
- **Interface Web** (`apps/web`) - Frontend Next.js + TypeScript + Bootstrap

### Características Principais

- ✅ **Testes sequenciais em grupo** com funções de gasto de alfa (O'Brien-Fleming, Pocock, Linear)
- ✅ **Correções para múltiplas comparações** (Bonferroni, Holm-Bonferroni, Šidák)
- ✅ **Métricas numéricas e de conversão** com testes apropriados (Z, T)
- ✅ **Resultados auditáveis** com p-valores brutos e ajustados
- ✅ **Interface corporativa** em português formal

## Arquitetura

```
estatab/
├── src/estatab/              # Pacote Python core
│   ├── core.py              # HipoteseSimplificada, TesteSequencialGrupo
│   └── utils.py             # Utilitários estatísticos
├── apps/
│   ├── api/                 # FastAPI wrapper
│   │   ├── main.py         # Endpoints REST
│   │   ├── models.py       # Modelos Pydantic
│   │   └── Dockerfile
│   └── web/                 # Next.js frontend
│       ├── app/            # Páginas e layouts
│       ├── utils/          # Tipos, UX, storage
│       └── Dockerfile
└── docker-compose.yml       # Orquestração
```

## Quick Start

### Pré-requisitos

- Docker e Docker Compose instalados
- Portas 3000 e 8000 disponíveis

### Execução

```bash
# Clone o repositório
cd c:\Users\mcout\Projetos\estatab

# Inicie os serviços
docker-compose up --build

# Acesse a interface web
# http://localhost:3000
```

### Uso

1. **Criar experimento** - Configure métrica, metodologia e parâmetros estatísticos
2. **Inserir dados** - Adicione variantes com suas estatísticas agregadas
3. **Executar análise** - Obtenha resultados com testes, p-valores e conclusões
4. **Revisar resultados** - Visualize comparações, efeitos e informações sequenciais

## Exemplo de Requisição API

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
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
      "fator_inflacao": "O'\''Brien-Fleming",
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
  }'
```

## Desenvolvimento Local

### Backend (API)

```bash
cd apps/api
pip install -e ".[test]"
python main.py
# API disponível em http://localhost:8000
```

### Frontend (Web)

```bash
cd apps/web
npm install
npm run dev
# Interface disponível em http://localhost:3000
```

### Pacote Core

```bash
pip install -e ".[test]"
pytest tests/ -v
```

## Documentação

- [API Documentation](apps/api/README.md) - Endpoints e exemplos
- [Frontend Documentation](apps/web/README.md) - Páginas e componentes

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.
