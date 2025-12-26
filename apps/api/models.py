"""Pydantic models for request/response validation."""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


class VarianteInput(BaseModel):
    """Input model for a single variant."""

    nome_variante: str = Field(..., description="Nome da variante")
    numero_amostras: int = Field(..., gt=0, description="Tamanho da amostra")
    valor_media: float = Field(..., description="Média ou taxa da métrica")
    desvio_padrao: Optional[float] = Field(
        None, description="Desvio padrão (obrigatório para métricas numéricas)")
    variante_controle: bool = Field(
        False, description="Se esta é a variante de controle")


class ExperimentConfig(BaseModel):
    """Configuration for the experiment."""

    nome_metrica: str = Field(..., description="Nome da métrica alvo")
    tipo_metrica: str = Field(
        ..., description="Tipo: 'numerica', 'media', 'conversao', 'proporcao'")
    tamanho_amostral_calculado: int = Field(...,
                                            gt=0, description="Tamanho amostral planejado")
    intencao_teste: str = Field(
        "detectar_aumento", description="Intenção: 'detectar_aumento', 'detectar_reducao', 'detectar_diferenca'")
    alfa: float = Field(0.05, gt=0, lt=1, description="Nível de significância")
    metodologia: str = Field(
        "frequentista", description="'frequentista' ou 'testes_sequenciais'")
    tipo_correcao: str = Field(
        "Bonferroni", description="Método de correção múltipla")

    # Campos opcionais para testes sequenciais
    data_inicio_experimento: Optional[str] = Field(
        None, description="Data de início (formato: YYYY-MM-DD)")
    data_fim_experimento: Optional[str] = Field(
        None, description="Data de término (formato: YYYY-MM-DD)")
    fator_inflacao: str = Field(
        "Pocock", description="Técnica de inflação amostral")
    funcao_gasto_alfa: str = Field(
        "linear", description="Função de gasto de alfa")
    valor_lambda: Union[int, float] = Field(1, description="Parâmetro lambda")


class AnalyzeRequest(BaseModel):
    """Complete request for experiment analysis."""

    config: ExperimentConfig
    variantes: List[VarianteInput] = Field(
        ..., min_length=2, description="Lista de variantes (mínimo 2)")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
