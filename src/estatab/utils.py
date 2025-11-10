"""Módulo para teste de homocedasticidade usando o teste F (variâncias iguais)."""

from dataclasses import dataclass
from math import isfinite
from typing import Optional
from scipy.stats import f as f_dist


@dataclass
class ResultadoF:
    """
    Resultado do teste F de igualdade de variâncias.

    Atributos:
        pvalor: Valor-p bilateral calculado.
        rejeita_h0: Indica se H0 (variâncias iguais) foi rejeitada.
        homocedasticidade: True se as variâncias forem consideradas iguais.
        excecao: Flag indicando se ocorreu alguma exceção.
        f_stat: Estatística F calculada.
        df_num: Graus de liberdade do numerador.
        df_den: Graus de liberdade do denominador.
        alfa: Nível de significância usado.
    """
    pvalor: Optional[float]
    rejeita_h0: Optional[bool]
    homocedasticidade: Optional[bool]
    excecao: bool
    f_stat: Optional[float] = None
    df_num: Optional[int] = None
    df_den: Optional[int] = None
    alfa: Optional[float] = None


class HomocedasticidadeF:
    """
    Teste F bilateral para verificar igualdade de variâncias (homocedasticidade)
    usando dados resumidos (n e desvios-padrão).

    Hipóteses:
        H0: sigma1² = sigma2²
        H1: sigma1² != sigma2²

    Este teste utiliza:
        F = (maior variância) / (menor variância)

    Parâmetros:
        n1: Tamanho amostral do grupo 1 (>= 2).
        n2: Tamanho amostral do grupo 2 (>= 2).
        s1: Desvio-padrão do grupo 1 (>= 0).
        s2: Desvio-padrão do grupo 2 (>= 0).
        alfa: Nível de significância (default: 0.05).
    """

    def __init__(self, n1: int, n2: int, s1: float, s2: float, alfa: float = 0.05):
        """Inicializa o teste F garantindo consistência nos graus de liberdade."""
        if n1 is None or n2 is None or s1 is None or s2 is None:
            raise ValueError("Parâmetros n1, n2, s1 e s2 são obrigatórios.")

        if n1 < 2 or n2 < 2:
            raise ValueError("n1 e n2 devem ser ≥ 2.")

        if s1 < 0 or s2 < 0:
            raise ValueError("Desvios-padrão não podem ser negativos.")

        self._alfa = float(alfa)

        var1 = s1 ** 2
        var2 = s2 ** 2

        # Garante F ≥ 1 e ajusta os graus de liberdade ao numerador e denominador corretos
        if var1 >= var2:
            self._f_stat = var1 / max(var2, 1e-300)
            self._df_num, self._df_den = (n1 - 1), (n2 - 1)
        else:
            self._f_stat = var2 / max(var1, 1e-300)
            self._df_num, self._df_den = (n2 - 1), (n1 - 1)

    def verifica_homocedasticidade(self) -> ResultadoF:
        """
        Executa o teste F bilateral de igualdade de variâncias.

        Método:
            p = 2 * min( cdf(F), sf(F) )

        Onde:
            - cdf  = Prob(F <= f_stat)
            - sf   = Prob(F >= f_stat) = survival function

        Retorna:
            Objeto ResultadoF com estatísticas do teste.
        """
        cdf_val = f_dist.cdf(self._f_stat, self._df_num, self._df_den)
        sf_val = f_dist.sf(self._f_stat, self._df_num, self._df_den)

        pvalor = 2.0 * min(cdf_val, sf_val)

        if not isfinite(pvalor):
            pvalor = 1.0

        pvalor = min(max(pvalor, 0.0), 1.0)

        rejeita_h0 = pvalor < self._alfa
        homocedasticidade = not rejeita_h0

        return ResultadoF(
            pvalor=pvalor,
            rejeita_h0=rejeita_h0,
            homocedasticidade=homocedasticidade,
            excecao=False,
            f_stat=self._f_stat,
            df_num=self._df_num,
            df_den=self._df_den,
            alfa=self._alfa,
        )
