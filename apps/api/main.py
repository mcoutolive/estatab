"""FastAPI application wrapping the EstatAB statistical engine."""

from models import AnalyzeRequest, HealthResponse
from estatab import HipoteseSimplificada
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
import numpy as np
import json
from typing import Any, Dict
import sys
from pathlib import Path

# Add the estatab package to the path
estatab_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(estatab_src))


app = FastAPI(
    title="EstatAB API",
    description="API wrapper for EstatAB statistical experimentation engine",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def convert_to_json_serializable(obj: Any) -> Any:
    """Convert numpy types and other non-JSON-serializable types to native Python types."""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.post("/v1/analyze")
async def analyze_experiment(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Execute statistical analysis for an A/B/n experiment.

    This endpoint:
    1. Receives experiment configuration and variant data
    2. Instantiates HipoteseSimplificada from estatab
    3. Adds all variants
    4. Executes hypothesis testing
    5. Returns complete results with all statistical metrics

    Args:
        request: AnalyzeRequest containing config and variants

    Returns:
        Dictionary with complete analysis results including:
        - comparisons (test statistics, p-values, effects)
        - sequential testing info (if applicable)
        - multiple comparison corrections
        - final conclusion
    """
    try:
        # Extract configuration
        config = request.config

        # Instantiate HipoteseSimplificada
        hipotese = HipoteseSimplificada(
            nome_metrica=config.nome_metrica,
            tipo_metrica=config.tipo_metrica,
            tamanho_amostral_calculado=config.tamanho_amostral_calculado,
            intencao_teste=config.intencao_teste,
            alfa=config.alfa,
            metodologia=config.metodologia,
            tipo_correcao=config.tipo_correcao,
            data_inicio_experimento=config.data_inicio_experimento,
            data_fim_experimento=config.data_fim_experimento,
            fator_inflacao=config.fator_inflacao,
            funcao_gasto_alfa=config.funcao_gasto_alfa,
            valor_lambda=config.valor_lambda,
        )

        # Add all variants
        for variante in request.variantes:
            hipotese.adiciona_variante(
                nome_variante=variante.nome_variante,
                numero_amostras=variante.numero_amostras,
                valor_media=variante.valor_media,
                desvio_padrao=variante.desvio_padrao,
                variante_controle=variante.variante_controle,
            )

        # Execute hypothesis testing
        resultado = hipotese.executa_teste_hipotese()

        # Convert all numpy types to JSON-serializable types
        resultado_serializable = convert_to_json_serializable(resultado)

        return resultado_serializable

    except ValueError as e:
        # Handle validation errors from estatab
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500, detail=f"Erro interno ao processar análise: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
