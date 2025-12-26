/**
 * TypeScript types matching the API contracts
 */

export interface ExperimentConfig {
    nome_metrica: string;
    tipo_metrica: string;
    tamanho_amostral_calculado: number;
    intencao_teste: string;
    alfa: number;
    metodologia: string;
    tipo_correcao: string;
    data_inicio_experimento?: string;
    data_fim_experimento?: string;
    fator_inflacao: string;
    funcao_gasto_alfa: string;
    valor_lambda: number;
}

export interface Variante {
    nome_variante: string;
    numero_amostras: number;
    valor_media: number;
    desvio_padrao?: number;
    variante_controle: boolean;
}

export interface AnalyzeRequest {
    config: ExperimentConfig;
    variantes: Variante[];
}

export interface Comparacao {
    comparacao: string;
    teste: string;
    estatistica: number;
    pvalor: number;
    pvalorAjustado: number;
    efeito: number;
    rejeitaH0Corrigido: boolean;
    conclusaoCorrigida: string;
    alfaCorrigido?: number;
}

export interface SequenciaisInfo {
    alfaAcumulado: number;
    valorFatorInflacao: number;
    completudeExperimento: number;
    datasTestesSequenciais?: string[];
    numeroTestesSequenciaisRealizados?: number;
}

export interface AnalyzeResponse {
    nomeMetrica: string;
    intencao: string;
    metodologia: string;
    alfaEfetivo: number;
    comparacoes: Comparacao[];
    sequenciais: SequenciaisInfo | null;
    correcao: {
        metodo: string;
        k: number;
    };
    conclusao_final: string;
}
