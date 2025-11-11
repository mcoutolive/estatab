"""Módulo com utilitários para testes estatísticos aplicados a experimentos A/B."""

from __future__ import annotations
import json
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from scipy.stats import norm
from scipy.stats import t as t_dist
from .utils import HomocedasticidadeF


class TesteHipoteseBase:
    """
    Classe base para testes de hipótese com cadastro de variantes.

    Fornece:
      - validações gerais (alfa e tipo de métrica),
      - registro de variantes (controle/tratamento),
      - heurísticas para normalidade (CLT),
      - IC normal aproximado para média/proporção.

    Tipos de métrica suportados:
        "media", "numerica", "conversao", "proporcao"
    """

    def __init__(self, tipo_metrica: str, alfa: float = 0.05):
        """
        Args:
            tipo_metrica: um dos valores válidos descritos acima.
            alfa: nível de significância (0 < alfa < 1).
        """
        if not (0 < alfa < 1):
            raise ValueError(
                f"O nível de significância deve estar entre 0 e 1. Valor inserido: {alfa}"
            )
        if tipo_metrica not in ["media", "numerica", "conversao", "proporcao"]:
            raise ValueError(
                "O tipo de métrica deve ser: 'media', 'numerica', 'conversao', 'proporcao'. "
                f"Valor inserido: {tipo_metrica}"
            )

        self.__tipo_metrica = tipo_metrica
        self.__alfa = float(alfa)
        self.__variantes: List[Dict[str, Any]] = []
        self.__variante_controle: Optional[str] = None

    # ----------------- PROPRIEDADES -----------------
    @property
    def tipo_metrica(self) -> str:
        """Tipo de métrica configurado nesta instância."""
        return self.__tipo_metrica

    @property
    def alfa(self) -> float:
        """Nível de significância global configurado para a instância."""
        return self.__alfa

    @property
    def variantes(self) -> str:
        """Lista de variantes em JSON (somente leitura)."""
        return json.dumps(self.__variantes, ensure_ascii=False)

    @property
    def variante_controle(self) -> Optional[str]:
        """Nome da variante definida como controle (se houver)."""
        return self.__variante_controle

    # ----------------- UTILIDADES -----------------
    def adiciona_variante(
        self,
        nome_variante: str,
        numero_amostras: int,
        valor_media: float,
        desvio_padrao: Optional[Union[int, float]],
        variante_controle: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Registra uma variante com estatísticas-resumo.

        Args:
            nome_variante: identificador da variante.
            numero_amostras: tamanho amostral (>= 1).
            valor_media: média (contínua) ou proporção em [0,1] dependendo do tipo.
            desvio_padrao: DP (obrigatório para métricas numéricas; para proporção
                será recalculado via aproximação normal).
            variante_controle: se True, define esta variante como controle.

        Retorna:
            Lista interna de variantes (dicionários), para acompanhamento.
        """
        if numero_amostras < 1:
            raise ValueError("numero_amostras deve ser ≥ 1.")

        if valor_media < 0:
            raise ValueError(f"A média não pode ser negativa. Valor inserido: {valor_media}")

        if self.__tipo_metrica in ["proporcao", "conversao"] and not (0 <= valor_media <= 1):
            raise ValueError(f"Para proporção/conversão, a média deve estar em [0,1]. Valor: {valor_media}")

        if self.__tipo_metrica in ["numerica", "media"]:
            if desvio_padrao is None:
                raise ValueError("Para métrica numérica, desvio_padrao não pode ser None.")
            if desvio_padrao < 0:
                raise ValueError("desvio_padrao não pode ser negativo.")
        else:
            # proporção/conversão: desvio calculado via p*(1-p)/n (erro-padrão da média)
            desvio_padrao = math.sqrt((valor_media * (1 - valor_media)) / max(numero_amostras, 1))

        registro = {
            "nomeVariante": nome_variante,
            "numeroAmostras": int(numero_amostras),
            "valorMedia": float(valor_media),
            "desvioPadrao": float(desvio_padrao),
            "varianteControle": bool(variante_controle),
            "normalidade": self.__verifica_normalidade(valor_media, numero_amostras),
            "intervaloConfianca": None,
        }
        self.__variantes.append(registro)

        if variante_controle:
            if self.__variante_controle is not None:
                raise ValueError("Já existe uma variante de controle definida.")
            self.__variante_controle = nome_variante

        return self.__variantes

    def __verifica_normalidade(self, media: Union[int, float], numero_amostras: int) -> bool:
        """
        Heurística simples baseada na CLT para decidir normalidade aproximada.

        Regras:
            - Métricas numéricas: n >= 30.
            - Proporções: np >= 10 e n(1-p) >= 10.
        """
        if self.__tipo_metrica in ["media", "numerica"]:
            return numero_amostras >= 30
        return (numero_amostras * media >= 10) and (numero_amostras * (1 - media) >= 10)

    def _calcula_intervalo_confianca_normal(
        self,
        media: float,
        desvio_padrao: float,
        numero_amostras: int,
        z_escore: float = 1.96,
    ) -> Tuple[float, float]:
        """
        Intervalo de confiança normal aproximado para a média.

        Args:
            media: média amostral.
            desvio_padrao: DP (amostral/populacional conforme aproximação).
            numero_amostras: tamanho amostral.
            z_escore: quantil z bicaudal (padrão 1.96 ~ 95%).

        Retorna:
            (limite_inferior, limite_superior)
        """
        erro = z_escore * (desvio_padrao / math.sqrt(numero_amostras))
        return media - erro, media + erro

    @staticmethod
    def calcula_media_desvio_metodo_delta(x: List[float], y: List[float]) -> Tuple[int, float, float]:
        """
        Aproximação via método delta para a razão de médias R = mean(x) / mean(y).

        Args:
            x: amostra de numeradores.
            y: amostra de denominadores (mesmo tamanho de x).

        Retorna:
            (n, media_razao, desvio_padrao_razao) onde
            n = len(x) = len(y).

        Observação:
            Var(R) é aproximada via derivadas parciais em relação a mean(x) e mean(y),
            incluindo o termo de covariância entre as médias amostrais.
        """
        if len(x) != len(y):
            raise ValueError("As listas 'x' e 'y' devem ter o mesmo tamanho.")

        n = len(x)
        if n < 2:
            raise ValueError("É preciso n ≥ 2 para estimar variâncias/covariâncias.")

        def media(v: List[float]) -> float:
            return sum(v) / len(v)

        def variancia_amostral(v: List[float], m: float) -> float:
            return sum((vi - m) ** 2 for vi in v) / (len(v) - 1)

        def cov_amostral(a: List[float], ma: float, b: List[float], mb: float) -> float:
            return sum((ai - ma) * (bi - mb) for ai, bi in zip(a, b)) / (len(a) - 1)

        mx = media(x)
        my = media(y)
        vx = variancia_amostral(x, mx)
        vy = variancia_amostral(y, my)
        covxy = cov_amostral(x, mx, y, my)

        R = mx / my
        # Var(R) ≈ (∂R/∂mx)^2 Var(mx) + (∂R/∂my)^2 Var(my) + 2(∂R/∂mx)(∂R/∂my)Cov(mx,my)
        var_mx = vx / n
        var_my = vy / n
        cov_mx_my = covxy / n

        var_R = (1 / (my ** 2)) * var_mx + (mx ** 2 / my ** 4) * var_my - 2 * (mx / (my ** 3)) * cov_mx_my
        dp_R = math.sqrt(max(var_R, 0.0))

        return n, R, dp_R


class HipoteseSimplificada(TesteHipoteseBase):
    """
    Orquestrador que integra cadastro de variantes, testes estatísticos
    (Z de proporções, Z/T para médias) e, opcionalmente, gasto de alfa
    em Testes Sequenciais de Grupos (TSG) com correções múltiplas.
    """

    def __init__(
        self,
        nome_metrica: str,
        tipo_metrica: str,
        tamanho_amostral_calculado: int,
        intencao_teste: str = "detectar_aumento",
        alfa: float = 0.05,
        metodologia: str = "frequentista",
        tipo_correcao: str = "Bonferroni",
        data_inicio_experimento: Optional[str] = None,
        data_fim_experimento: Optional[str] = None,
        fator_inflacao: str = "Pocock",
        funcao_gasto_alfa: str = "linear",
        valor_lambda: Union[int, float] = 1,
    ):
        """
        Configura o orquestrador.

        Args:
            nome_metrica: nome da métrica-alvo (para relatórios).
            tipo_metrica: 'media'|'numerica'|'conversao'|'proporcao'.
            tamanho_amostral_calculado: n planejado do experimento.
            intencao_teste: 'detectar_aumento'|'detectar_reducao'|'detectar_diferenca'.
            alfa: nível de significância global.
            metodologia: 'frequentista'|'testes_sequenciais'.
            tipo_correcao: 'Bonferroni'|'Holm-Bonferroni'|'Sidak'.
            data_inicio_experimento: data inicial (string).
            data_fim_experimento: data final (string).
            fator_inflacao: regra para inflação de amostra (TSG).
            funcao_gasto_alfa: função de gasto de alfa (TSG).
            valor_lambda: parâmetro das funções potência/exponencial (TSG).
        """
        super().__init__(tipo_metrica, alfa)
        # validações resumidas
        if intencao_teste not in ["detectar_aumento", "detectar_reducao", "detectar_diferenca"]:
            raise ValueError("intencao_teste deve ser: detectar_aumento|detectar_reducao|detectar_diferenca")
        if metodologia not in ["frequentista", "testes_sequenciais"]:
            raise ValueError("metodologia deve ser: frequentista|testes_sequenciais")
        if tipo_correcao not in ["Bonferroni", "Holm-Bonferroni", "Sidak"]:
            raise ValueError("tipo_correcao inválido.")
        if fator_inflacao not in ["Pocock", "O'Brien-Fleming"]:
            raise ValueError("fator_inflacao inválido.")
        if funcao_gasto_alfa.lower() not in ["linear", "potencia", "exponencial", "pocock", "o'brien-fleming", "obrien_fleming"]:
            raise ValueError("funcao_gasto_alfa inválida.")
        if valor_lambda <= 0:
            raise ValueError("valor_lambda deve ser > 0.")

        self.__nome_metrica = nome_metrica
        self.__tamanho_amostral_calculado = int(tamanho_amostral_calculado)
        self.__intencao_teste = intencao_teste
        self.__metodologia = metodologia
        self.__tipo_correcao = tipo_correcao
        self.__data_inicio_experimento = data_inicio_experimento
        self.__data_fim_experimento = data_fim_experimento
        self.__fator_inflacao = fator_inflacao
        self.__funcao_gasto_alfa = funcao_gasto_alfa
        self.__valor_lambda = float(valor_lambda)

        # resultados/cache
        self.__informacoes_testes_sequenciais: Optional[Dict[str, Any]] = None
        self.__resultado: Optional[Dict[str, Any]] = None
        self.__variantes_internas: List[Dict[str, Any]] = []

    # -------------- PROPRIEDADES ÚTEIS --------------
    @property
    def informacoes_experimento(self) -> str:
        """Resumo da configuração atual (JSON)."""
        return json.dumps(
            {
                "metodologia": self.__metodologia,
                "intencao": self.__intencao_teste,
                "correcao": self.__tipo_correcao,
                "fatorInflacao": self.__fator_inflacao,
                "funcaoGastoAlfa": self.__funcao_gasto_alfa,
            },
            ensure_ascii=False,
        )

    @property
    def intervalos_confianca(self) -> str:
        """Lista de ICs 95% por variante em JSON (normal aprox.)."""
        if not self.__variantes_internas:
            return json.dumps([], ensure_ascii=False)

        saida = []
        for v in self.__variantes_internas:
            li, ls = self._calcula_intervalo_confianca_normal(
                v["valorMedia"], v["desvioPadrao"], v["numeroAmostras"]
            )
            saida.append({"variante": v["nomeVariante"], "ic95": (li, ls)})
        return json.dumps(saida, ensure_ascii=False)

    @property
    def data_inicio_experimento(self) -> Optional[str]:
        """Data inicial configurada para TSG (se houver)."""
        return self.__data_inicio_experimento

    @property
    def data_fim_experimento(self) -> Optional[str]:
        """Data final configurada para TSG (se houver)."""
        return self.__data_fim_experimento

    # -------------- OVERRIDE: adiciona_variante --------------
    def adiciona_variante(
        self,
        nome_variante: str,
        numero_amostras: int,
        valor_media: Union[int, float],
        desvio_padrao: Optional[Union[int, float]],
        variante_controle: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Encapsula o cadastro da variante e atualiza o cache interno para uso
        no orquestrador (comparações/ICs).
        """
        vari = super().adiciona_variante(
            nome_variante=nome_variante,
            numero_amostras=numero_amostras,
            valor_media=float(valor_media),
            desvio_padrao=None if desvio_padrao is None else float(desvio_padrao),
            variante_controle=variante_controle,
        )
        self.__variantes_internas = json.loads(self.variantes)
        return vari

    @staticmethod
    def __conclusao(decisao: bool, efeito: float, intencao: str) -> str:
        """
        Mapeia (decisão, direção do efeito, intenção) -> texto final.

        Args:
            decisao: True se rejeita H0.
            efeito: diferença (tratamento - controle).
            intencao: 'detectar_aumento'|'detectar_reducao'|'detectar_diferenca'.
        """
        if intencao == "detectar_reducao":
            if decisao and efeito < 0:
                return "redução detectada"
            elif decisao and efeito >= 0:
                return "efeito oposto detectado (aumento)"
            else:
                return "redução não detectada"

        if intencao == "detectar_aumento":
            if decisao and efeito > 0:
                return "aumento detectado"
            elif decisao and efeito <= 0:
                return "efeito oposto detectado (redução)"
            else:
                return "aumento não detectado"

        return "diferença estatística detectada" if decisao else "diferença não detectada"

    # ============================
    # Correções p/ múltiplos testes
    # ============================
    @staticmethod
    def __bonferroni(pvalores: List[float], alfa: float):
        """Ajuste Bonferroni: α/k; p_ajust = min(p*k, 1)."""
        k = max(len(pvalores), 1)
        alfa_limite = alfa / k
        p_ajust = [min(p * k, 1.0) for p in pvalores]
        rejeita = [p <= alfa_limite for p in pvalores]   # ou p_ajust[i] <= alfa
        alfa_corrigido = [alfa_limite] * k
        return {"p_ajustado": p_ajust, "rejeita": rejeita, "alfa_corrigido": alfa_corrigido}

    @staticmethod
    def __sidak(pvalores: List[float], alfa: float):
        """Ajuste Šidák: α' = 1 - (1-α)^(1/k); p_ajust = 1 - (1-p)^k."""
        k = max(len(pvalores), 1)
        alfa_limite = 1.0 - (1.0 - alfa) ** (1.0 / k)
        p_ajust = [1.0 - (1.0 - p) ** k for p in pvalores]
        rejeita = [p <= alfa_limite for p in pvalores]
        alfa_corrigido = [alfa_limite] * k
        return {"p_ajustado": p_ajust, "rejeita": rejeita, "alfa_corrigido": alfa_corrigido}

    @staticmethod
    def __holm_bonferroni(pvalores: List[float], alfa: float):
        """
        Ajuste Holm (step-down). p*_i = max_{j<=i} min{ (k-j+1)*p_(j), 1 }.

        Retorna:
            dict com p_ajustado (reordenado na posição original),
            rejeita (p*_i <= alfa) e alfa_corrigido=None (depende da ordenação).
        """
        k = len(pvalores)
        if k == 0:
            return {"p_ajustado": [], "rejeita": [], "alfa_corrigido": []}

        ordenacao = sorted(range(k), key=lambda i: pvalores[i])   # índices por p crescente
        p_ordenado = [pvalores[i] for i in ordenacao]

        ajust_ordenado = [0.0] * k
        maximo_acumulado = 0.0
        for i, p in enumerate(p_ordenado):
            ajust = min((k - i) * p, 1.0)
            maximo_acumulado = max(maximo_acumulado, ajust)
            ajust_ordenado[i] = maximo_acumulado

        p_ajust = [0.0] * k
        for pos, idx_original in enumerate(ordenacao):
            p_ajust[idx_original] = ajust_ordenado[pos]

        rejeita = [p <= alfa for p in p_ajust]
        return {"p_ajustado": p_ajust, "rejeita": rejeita, "alfa_corrigido": [None] * k}

    def __aplica_correcao_multiplos_testes(
        self, pvalores: List[float], alfa: float, metodo: str
    ):
        """
        Aplica a correção de múltiplas comparações selecionada.

        Args:
            pvalores: lista de p-valores.
            alfa: nível global.
            metodo: 'Bonferroni'|'Sidak'|'Holm-Bonferroni'.

        Retorna:
            dict com chaves: 'p_ajustado', 'rejeita', 'alfa_corrigido'.
        """
        m = metodo.strip().lower()
        if m == "bonferroni":
            return self.__bonferroni(pvalores, alfa)
        if m == "sidak":
            return self.__sidak(pvalores, alfa)
        if m in ("holm-bonferroni", "holm", "holm bonferroni"):
            return self.__holm_bonferroni(pvalores, alfa)
        # fallback: sem correção (não recomendado para produção)
        return {"p_ajustado": pvalores[:], "rejeita": [p < alfa for p in pvalores], "alfa_corrigido": [alfa] * len(pvalores)}

    def executa_teste_hipotese(self) -> Dict[str, Any]:
        """
        Executa as comparações Controle vs. Tratamentos conforme o tipo de métrica.

        Fluxo:
            1) Valida existência de controle único.
            2) (Opcional) Calcula gasto de alfa (TSG) e substitui alfa por alfa_efetivo.
            3) Para cada tratamento:
                - Proporções: Z com p agrupado.
                - Numérica (n1,n2>=30): Z (pooled ou Welch-like via F).
                - Numérica (caso geral): T independente (pooled vs Welch via F).
            4) Aplica correção de múltiplas comparações.
            5) Retorna dicionário com resultados e conclusões.
        """
        if len(self.__variantes_internas) < 2:
            raise ValueError("É necessário ≥ 2 variantes.")

        if sum(1 for v in self.__variantes_internas if v["varianteControle"]) != 1:
            raise ValueError("Deve haver exatamente UMA variante de controle.")

        controle = next(v for v in self.__variantes_internas if v["varianteControle"])
        tratamentos = [v for v in self.__variantes_internas if not v["varianteControle"]]

        # testes sequenciais (se escolhido)
        alfa_efetivo = self.alfa
        if self.__metodologia == "testes_sequenciais":
            tsg = TesteSequencialGrupo(
                tipo_metrica=self.tipo_metrica,
                alfa=self.alfa,
                fator_inflacao=self.__fator_inflacao,
                valor_lambda=self.__valor_lambda,
            )
            info = tsg.executa_tsg(
                data_inicio_experimento=self.__data_inicio_experimento,
                data_fim_experimento=self.__data_fim_experimento,
                tamanho_amostral_calculado=self.__tamanho_amostral_calculado,
                tamanho_amostral_atual=sum(v["numeroAmostras"] for v in self.__variantes_internas),
                funcao_gasto_alfa=self.__funcao_gasto_alfa,
            )
            self.__informacoes_testes_sequenciais = info
            alfa_efetivo = float(info["alfaAcumulado"])

        resultados: List[Dict[str, Any]] = []
        for trat in tratamentos:
            res = self.__seleciona_e_roda_teste(
                controle, trat, alfa_efetivo, self.__intencao_teste
            )
            resultados.append(res)

        # Correção múltipla
        pvalores = [r["pvalor"] for r in resultados]
        correcoes = self.__aplica_correcao_multiplos_testes(pvalores, alfa_efetivo, self.__tipo_correcao)

        for i, r in enumerate(resultados):
            r["pvalorAjustado"] = float(correcoes["p_ajustado"][i])
            r["alfaCorrigido"] = correcoes["alfa_corrigido"][i]   # pode ser None no Holm
            r["rejeitaH0Corrigido"] = bool(correcoes["rejeita"][i])
            r["conclusaoCorrigida"] = self.__conclusao(r["rejeitaH0Corrigido"], r["efeito"], self.__intencao_teste)

        conclusoes_corrigidas = [r["conclusaoCorrigida"] for r in resultados]

        # Conclusão final resumida (corrigida)
        if any(("detectada" in c and "não" not in c) for c in conclusoes_corrigidas):
            if self.__intencao_teste == "detectar_reducao":
                conclusao_final = "redução detectada"
            elif self.__intencao_teste == "detectar_aumento":
                conclusao_final = "aumento detectado"
            else:
                conclusao_final = "diferença estatística detectada"
        else:
            if self.__intencao_teste == "detectar_reducao":
                conclusao_final = "redução não detectada"
            elif self.__intencao_teste == "detectar_aumento":
                conclusao_final = "aumento não detectado"
            else:
                conclusao_final = "diferença não detectada"

        self.__resultado = {
            "nomeMetrica": self.__nome_metrica,
            "intencao": self.__intencao_teste,
            "metodologia": self.__metodologia,
            "alfaEfetivo": alfa_efetivo,
            "comparacoes": resultados,
            "sequenciais": self.__informacoes_testes_sequenciais,
            "correcao": {"metodo": self.__tipo_correcao, "k": len(resultados)},
            "conclusoes": [self.__conclusao(r["rejeitaH0"], r["efeito"], self.__intencao_teste) for r in resultados],
            "conclusoesCorrigidas": conclusoes_corrigidas,
            "conclusao_final": conclusao_final,
        }
        return self.__resultado

    def __seleciona_e_roda_teste(
        self,
        a: Dict[str, Any],
        b: Dict[str, Any],
        alfa: float,
        intencao: str,
    ) -> Dict[str, Any]:
        """
        Seleciona e executa o teste apropriado para a comparação (b vs a).

        Regras:
            - Proporção/Conversão: Z com p agrupado (pooled).
            - Métrica numérica:
                * se n1>=30 e n2>=30 → Z (pooled ou Welch-like via F).
                * caso contrário → t independente (pooled ou Welch).
        """
        nome_b = b["nomeVariante"]

        # (1) PROPORÇÕES → Z
        if self.tipo_metrica in ["proporcao", "conversao"]:
            n1, n2 = a["numeroAmostras"], b["numeroAmostras"]
            p1, p2 = a["valorMedia"], b["valorMedia"]
            z, p = self.__z_duas_proporcoes(p1, n1, p2, n2, intencao)
            decisao = p < alfa
            return {
                "comparacao": f"{nome_b} vs {a['nomeVariante']}",
                "teste": "Teste de Proporção Z",
                "estatistica": z,
                "pvalor": p,
                "alfa": alfa,
                "rejeitaH0": decisao,
                "efeito": p2 - p1,
            }

        # (2) MÉTRICA NUMÉRICA: usa F para escolher pooled vs Welch
        resultado_f = HomocedasticidadeF(
            n1=a["numeroAmostras"], n2=b["numeroAmostras"],
            s1=a["desvioPadrao"], s2=b["desvioPadrao"], alfa=alfa
        ).verifica_homocedasticidade()
        variancia_igual = bool(resultado_f.homocedasticidade)

        n1, n2 = a["numeroAmostras"], b["numeroAmostras"]
        m1, dp1 = a["valorMedia"], a["desvioPadrao"]
        m2, dp2 = b["valorMedia"], b["desvioPadrao"]

        if (n1 >= 30) and (n2 >= 30):
            z_est, p_val = self.__z_duas_medias_resumo(
                m1=m1, s1=dp1, n1=n1, m2=m2, s2=dp2, n2=n2,
                variancia_igual=variancia_igual, intencao=intencao
            )
            decisao = p_val < alfa
            return {
                "comparacao": f"{nome_b} vs {a['nomeVariante']}",
                "teste": "Teste Z",
                "estatistica": z_est,
                "pvalor": p_val,
                "alfa": alfa,
                "rejeitaH0": decisao,
                "efeito": m2 - m1,
                "f": {"pvalor": resultado_f.pvalor, "F": resultado_f.f_stat, "homocedastico": variancia_igual},
            }

        # Caso geral: t independente
        t_est, p_val = self.__t_indep_resumo(
            m1=m1, s1=dp1, n1=n1, m2=m2, s2=dp2, n2=n2,
            variancia_igual=variancia_igual, intencao=intencao
        )
        decisao = p_val < alfa
        return {
            "comparacao": f"{nome_b} vs {a['nomeVariante']}",
            "teste": "Teste T independente",
            "estatistica": t_est,
            "pvalor": p_val,
            "alfa": alfa,
            "rejeitaH0": decisao,
            "efeito": m2 - m1,
            "f": {"pvalor": resultado_f.pvalor, "F": resultado_f.f_stat, "homocedastico": variancia_igual},
        }

    @staticmethod
    def __z_duas_proporcoes(
        p1: float, n1: int, p2: float, n2: int, intencao: str
    ) -> Tuple[float, float]:
        """
        Z de duas proporções com p agrupado (pooled).

        Args:
            p1, n1: proporção e tamanho da amostra do controle.
            p2, n2: proporção e tamanho da amostra do tratamento.
            intencao: 'detectar_diferenca'|'detectar_aumento'|'detectar_reducao'.

        Retorna:
            (z, p) onde p é o p-valor conforme a intenção (bicaudal/uni).
        """
        p_agrupado = (p1 * n1 + p2 * n2) / (n1 + n2)
        erro = math.sqrt(p_agrupado * (1 - p_agrupado) * (1 / n1 + 1 / n2))
        if erro == 0:
            return 0.0, 1.0
        z = (p2 - p1) / erro

        if intencao == "detectar_diferenca":
            p = 2 * min(norm.cdf(z), norm.sf(z))
        elif intencao == "detectar_aumento":
            p = norm.sf(z)       # H1: p2 > p1
        else:  # detectar_reducao
            p = norm.cdf(z)     # H1: p2 < p1
        return float(z), float(min(max(p, 0.0), 1.0))

    @staticmethod
    def __z_duas_medias_resumo(
        m1: float, s1: float, n1: int,
        m2: float, s2: float, n2: int,
        variancia_igual: bool, intencao: str
    ) -> Tuple[float, float]:
        """
        Z para duas amostras independentes (médias) com estatísticas-resumo.

        Args:
            m1, s1, n1: média, DP e tamanho do controle.
            m2, s2, n2: média, DP e tamanho do tratamento.
            variancia_igual: se True, usa pooled; senão, Welch-like.
            intencao: 'detectar_diferenca'|'detectar_aumento'|'detectar_reducao'.
        """
        if variancia_igual:
            gl = n1 + n2 - 2   # usado apenas como referência
            sp2 = ((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / max(gl, 1)
            erro = math.sqrt(sp2 * (1 / n1 + 1 / n2))
        else:
            erro = math.sqrt((s1**2) / n1 + (s2**2) / n2)

        if erro == 0:
            return 0.0, 1.0

        z = (m2 - m1) / erro

        if intencao == "detectar_diferenca":
            p = 2 * min(norm.cdf(z), norm.sf(z))
        elif intencao == "detectar_aumento":
            p = norm.sf(z)       # H1: m2 > m1
        else:  # detectar_reducao
            p = norm.cdf(z)     # H1: m2 < m1

        return float(z), float(min(max(p, 0.0), 1.0))

    @staticmethod
    def __t_indep_resumo(
        m1: float, s1: float, n1: int,
        m2: float, s2: float, n2: int,
        variancia_igual: bool, intencao: str
    ) -> Tuple[float, float]:
        """
        t de duas amostras independentes (pooled ou Welch) com estatísticas-resumo.

        Retorna:
            (t_est, p_val) com p conforme cauda (intencao).
        """
        if variancia_igual:
            gl = n1 + n2 - 2
            sp2 = ((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / gl
            erro = math.sqrt(sp2 * (1 / n1 + 1 / n2))
        else:
            erro = math.sqrt((s1**2) / n1 + (s2**2) / n2)
            # gl de Welch:
            num = ((s1**2) / n1 + (s2**2) / n2) ** 2
            den = ((s1**2) / n1) ** 2 / (n1 - 1) + ((s2**2) / n2) ** 2 / (n2 - 1)
            gl = num / den

        if erro == 0:
            return 0.0, 1.0

        t_est = (m2 - m1) / erro
        
        if intencao == "detectar_diferenca":
            p = 2 * min(t_dist.cdf(t_est, gl), t_dist.sf(t_est, gl))
        elif intencao == "detectar_aumento":
            p = t_dist.sf(t_est, gl)  # H1: m2 > m1
        else:  # detectar_reducao
            p = t_dist.cdf(t_est, gl)  # H1: m2 < m1

        return float(t_est), float(min(max(p, 0.0), 1.0))


# ======================================================================
# Teste Sequencial de Grupo (gasto de alfa simples)
# ======================================================================

class TesteSequencialGrupo(TesteHipoteseBase):
    """
    Implementa o cálculo de gasto de alfa (Lan & DeMets) para TSG,
    além de gerar checkpoints semanais e inflação de amostra.
    """

    def __init__(
        self,
        tipo_metrica: str,
        alfa: float = 0.05,
        fator_inflacao: str = "Pocock",
        valor_lambda: Union[int, float] = 1,
    ):
        """
        Args:
            tipo_metrica: ver TesteHipoteseBase.
            alfa: nível de significância global.
            fator_inflacao: 'Pocock'|'O'Brien-Fleming'.
            valor_lambda: parâmetro para funções potência/exponencial.
        """
        super().__init__(tipo_metrica, alfa)
        if fator_inflacao not in ["Pocock", "O'Brien-Fleming"]:
            raise ValueError("fator_inflacao inválido.")
        if valor_lambda <= 0:
            raise ValueError("valor_lambda deve ser > 0.")

        self.__fator_inflacao = fator_inflacao
        self.__valor_lambda = float(valor_lambda)

    # ---------- Funções de gasto de alfa ----------
    @staticmethod
    def alfa_linear(t: float, alfa: float) -> float:
        """Gasto linear: α(t) = α·t."""
        return alfa * t

    @staticmethod
    def alfa_potencia(t: float, alfa: float, valor_lambda: float = 1) -> float:
        """Gasto potência: α(t) = α·t^λ (λ>0)."""
        return alfa * (t ** valor_lambda)

    @staticmethod
    def alfa_exponencial(t: float, alfa: float, valor_lambda: float = 1) -> float:
        """Gasto exponencial: α(t) = α·(1-e^{-λt})/(1-e^{-λ})."""
        if valor_lambda == 0:
            return 0.0
        return alfa * (1 - math.exp(-valor_lambda * t)) / (1 - math.exp(-valor_lambda))

    @staticmethod
    def alfa_pocock(t: float, alfa: float) -> float:
        """Gasto Pocock: α(t) = α·ln(1 + (e-1)·t)."""
        return alfa * math.log(1 + (math.e - 1) * t)

    @staticmethod
    def alfa_obrien_fleming(t: float, alfa: float) -> float:
        """
        Gasto O'Brien–Fleming via aproximação normal:
        usa limiar z_{α/2}/√t (gasto pequeno no início).
        """
        z_alfa = norm.ppf(1 - alfa / 2)
        z = z_alfa / math.sqrt(max(t, 1e-12))
        return 2 * (1 - norm.cdf(z))

    # ---------- Datas para TSG ----------
    @staticmethod
    def define_datas_sequenciais(
        data_inicio_experimento: str,
        data_fim_experimento: str,
    ) -> Tuple[List[str], datetime, datetime]:
        """
        Cria checkpoints semanais a partir de 2 até no máximo 5 semanas
        (sem ultrapassar data_fim).

        Retorna:
            (lista_datas_str, data_inicial_dt, data_final_dt)
        """
        di = TesteSequencialGrupo._parse_data(data_inicio_experimento)
        df = TesteSequencialGrupo._parse_data(data_fim_experimento)
        if di >= df:
            raise ValueError("data_inicio deve ser anterior a data_fim.")
        if (df - di).days < 14:
            raise ValueError("Período mínimo de 14 dias para TSG.")

        datas = []
        for i in range(2, 6):
            d_i = di + timedelta(weeks=i)
            if d_i >= df:
                break
            datas.append(d_i.strftime("%Y-%m-%d"))
        return datas, di, df

    @staticmethod
    def _parse_data(s: str) -> datetime:
        """
        Faz parsing robusto de datas em formatos comuns.
        Levanta ValueError se nenhum formato for aceito.
        """
        formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d", "%Y.%m.%d"]
        for f in formatos:
            try:
                return datetime.strptime(s, f)
            except Exception:
                continue
        raise ValueError(f"Formato de data inválido: {s}")

    # ---------- Execução ----------
    def executa_tsg(
        self,
        data_inicio_experimento: str,
        data_fim_experimento: str,
        tamanho_amostral_calculado: int,
        tamanho_amostral_atual: int,
        funcao_gasto_alfa: str = "linear",
    ) -> Dict[str, Any]:
        """
        Calcula o gasto de alfa acumulado e estatísticas auxiliares de TSG.

        Args:
            data_inicio_experimento, data_fim_experimento: intervalo do estudo.
            tamanho_amostral_calculado: n planejado (sem inflação).
            tamanho_amostral_atual: n observado até o momento.
            funcao_gasto_alfa: 'linear'|'potencia'|'exponencial'|'pocock'|'o'brien-fleming'.

        Retorna:
            dicionário com número de interinos, alfaAcumulado, fator de inflação,
            tamanhos planejados/atuais e datas dos checkpoints.
        """
        datas, di, df = self.define_datas_sequenciais(
            data_inicio_experimento, data_fim_experimento
        )

        # Nº de análises interinas (checkpoints entre início e fim)
        n_interinos = len(datas)

        # 1) Completude (sem inflação) — vitrine
        n_desenhado = max(tamanho_amostral_calculado, 1)
        t_completude = max(min(tamanho_amostral_atual / n_desenhado, 1.0), 0.0)

        # 2) Fator de inflação pelo nº de interinos
        fator = self.__atualiza_fator_inflacao(n_interinos)

        # 3) Completude para gasto de alfa (com inflação)
        n_desenhado_inflado = n_desenhado * max(fator, 1e-12)
        t_gasto = max(min(tamanho_amostral_atual / n_desenhado_inflado, 1.0), 0.0)

        # 4) Gasto de alfa
        fg = funcao_gasto_alfa.lower()
        if fg == "linear":
            alfa_acumulado = self.alfa_linear(t_gasto, self.alfa)
        elif fg == "potencia":
            alfa_acumulado = self.alfa_potencia(t_gasto, self.alfa, self.__valor_lambda)
        elif fg == "exponencial":
            alfa_acumulado = self.alfa_exponencial(t_gasto, self.alfa, self.__valor_lambda)
        elif fg in ["pocock"]:
            alfa_acumulado = self.alfa_pocock(t_gasto, self.alfa)
        elif fg in ["o'brien-fleming", "obrien_fleming"]:
            alfa_acumulado = self.alfa_obrien_fleming(t_gasto, self.alfa)
        else:
            raise ValueError(f"funcao_gasto_alfa inválida: {funcao_gasto_alfa}")

        return {
            "numeroTestesSequenciaisRealizados": n_interinos,
            "alfaAcumulado": float(min(max(alfa_acumulado, 0.0), self.alfa)),
            "funcaoGastoAlfa": funcao_gasto_alfa,
            "valorFatorInflacao": float(fator),
            "tecnicaFatorInflacao": self.__fator_inflacao,
            "tamanhoAmostralAtual": int(tamanho_amostral_atual),
            "tamanhoAmostralCalculado": int(n_desenhado),
            "tamanhoAmostralPlanejadoInflado": float(n_desenhado_inflado),
            "completudeExperimento": float(t_completude),
            "dataInicioExperimento": di.strftime("%Y-%m-%d"),
            "dataFimExperimento": df.strftime("%Y-%m-%d"),
            "datasTestesSequenciais": datas,
        }

    def __atualiza_fator_inflacao(self, k: int) -> float:
        """
        Calcula o fator de inflação de amostra a partir do nº de interinos.

        Definição:
            K = nº de análises interinas + 1 (análise final).
        Regras:
            - Pocock: aproximação via z* (mais conservadora no início).
            - O'Brien–Fleming: tabela simples por k (interinos).

        Retorna:
            fator de inflação (>= 1).
        """
        K = k + 1  # interinos + análise final

        if self.__fator_inflacao == "Pocock":
            z_alfa = norm.ppf(1 - self.alfa / 2)
            z_beta = norm.ppf(0.8)
            z_estrela = norm.ppf(1 - self.alfa / (2 * math.sqrt(max(K, 1))))
            return float(((z_estrela + z_beta) / (z_alfa + z_beta)) ** 2)

        # O'Brien-Fleming: aproximação simples por k
        tabela = {1: 1.01, 2: 1.02, 3: 1.02, 4: 1.03}
        return float(tabela.get(max(min(k, 4), 1), 1.03))
