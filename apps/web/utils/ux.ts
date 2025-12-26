/**
 * UX Dictionary - Corporate language for the EstatAB platform
 * 
 * This module contains all user-facing text, tooltips, validation messages,
 * and result interpretations in professional, formal Portuguese suitable
 * for corporate and regulated environments.
 */

export const UX = {
    // Page titles and headlines
    titles: {
        home: "EstatAB: Plataforma corporativa de experimentação estatística",
        homeSubtitle: "Testes sequenciais, controle rigoroso de significância estatística e decisões auditáveis.",
        newExperiment: "Configuração do experimento",
        runExperiment: "Inserção de dados das variantes",
        results: "Painel de resultados",
    },

    // Field labels
    labels: {
        nomeMetrica: "Nome da métrica",
        tipoMetrica: "Tipo de métrica",
        intencaoTeste: "Hipótese alternativa",
        metodologia: "Metodologia estatística",
        alfa: "Nível de significância global (α)",
        tamanhoAmostral: "Tamanho amostral planejado",
        tipoCorrecao: "Correção para múltiplas comparações",
        dataInicio: "Data de início do experimento",
        dataFim: "Data de término do experimento",
        funcaoGastoAlfa: "Função de gasto de alfa",
        fatorInflacao: "Técnica de inflação amostral",
        valorLambda: "Parâmetro lambda (λ)",
        nomeVariante: "Nome da variante",
        numeroAmostras: "Tamanho da amostra (n)",
        valorMedia: "Média",
        desvioPadrao: "Desvio padrão",
        taxa: "Taxa (proporção)",
        varianteControle: "Variante de controle",
    },

    // Tooltips and help text
    tooltips: {
        tipoMetrica: "Define como a métrica é medida e qual teste estatístico será aplicado.",
        intencaoTeste: "Define a direção da hipótese alternativa que será testada.",
        metodologiaSequencial: "Permite análises interinas mantendo controle rigoroso do erro tipo I por meio de funções de gasto de alfa.",
        correcaoHolm: "Correção step-down para múltiplas comparações, com maior poder estatístico que Bonferroni.",
        funcaoOBrienFleming: "Abordagem conservadora no início do experimento, amplamente utilizada em contextos regulados.",
        varianteControle: "Exatamente uma variante deve ser marcada como controle. As demais serão comparadas contra ela.",
    },

    // Validation messages
    validation: {
        required: "Este campo é obrigatório.",
        mustBePositive: "O valor deve ser maior que zero.",
        exactlyOneControl: "É obrigatória a definição de exatamente uma variante de controle.",
        atLeastTwoVariants: "É necessário cadastrar no mínimo duas variantes (uma de controle e uma de tratamento).",
        sequentialMinDays: "Testes sequenciais exigem um período mínimo de 14 dias entre as datas de início e término.",
        desvioPadraoRequired: "Desvio padrão é obrigatório para métricas numéricas.",
    },

    // Result interpretation messages
    results: {
        evidenciaFavoravel: "Evidência estatística favorável ao tratamento.",
        evidenciaDesfavoravel: "Não foi detectada evidência estatística suficiente ao nível de significância configurado.",
        reducaoDetectada: "Redução detectada",
        reducaoNaoDetectada: "Redução não detectada",
        aumentoDetectado: "Aumento detectado",
        aumentoNaoDetectado: "Aumento não detectado",
        diferencaDetectada: "Diferença estatística detectada",
        diferencaNaoDetectada: "Diferença não detectada",
    },

    // Button labels
    buttons: {
        createExperiment: "Criar experimento",
        next: "Próximo",
        addVariant: "Adicionar variante",
        removeVariant: "Remover",
        executeAnalysis: "Executar análise",
        newExperiment: "Novo experimento",
    },

    // Error messages
    errors: {
        apiUnavailable: "Não foi possível conectar ao servidor de análise. Verifique se o serviço está disponível.",
        analysisError: "Erro ao executar análise estatística. Verifique os dados inseridos.",
        unexpectedError: "Erro inesperado. Por favor, tente novamente.",
    },

    // Loading messages
    loading: {
        analyzing: "Executando análise estatística...",
    },

    // Table headers
    tableHeaders: {
        comparacao: "Comparação",
        teste: "Teste estatístico",
        estatistica: "Estatística",
        pValorBruto: "p-valor bruto",
        pValorAjustado: "p-valor ajustado",
        efeito: "Efeito estimado",
        rejeicaoH0: "Rejeição de H₀",
    },

    // Summary card labels
    summary: {
        conclusaoFinal: "Conclusão final",
        alfaEfetivo: "Alfa efetivo",
        metodologia: "Metodologia",
        correcaoMultipla: "Correção múltipla",
        alfaAcumulado: "Alfa acumulado",
        fatorInflacao: "Fator de inflação",
        completude: "Completude do experimento",
        datasInterinas: "Datas recomendadas para análises sequenciais",
    },

    // Option values
    options: {
        tipoMetrica: {
            numerica: "Numérica (baseada em média)",
            conversao: "Conversão / Proporção",
        },
        intencaoTeste: {
            detectar_aumento: "Detectar aumento (teste unilateral)",
            detectar_reducao: "Detectar redução (teste unilateral)",
            detectar_diferenca: "Detectar diferença (teste bilateral)",
        },
        metodologia: {
            frequentista: "Frequentista",
            testes_sequenciais: "Testes sequenciais",
        },
        tipoCorrecao: {
            Bonferroni: "Bonferroni",
            "Holm-Bonferroni": "Holm–Bonferroni (recomendado)",
            Sidak: "Šidák",
        },
        funcaoGastoAlfa: {
            linear: "Linear (recomendado)",
            obrien_fleming: "O'Brien–Fleming",
            pocock: "Pocock",
            exponencial: "Exponencial",
            potencia: "Potência",
        },
        fatorInflacao: {
            Pocock: "Pocock",
            "O'Brien-Fleming": "O'Brien–Fleming",
        },
    },
} as const;
