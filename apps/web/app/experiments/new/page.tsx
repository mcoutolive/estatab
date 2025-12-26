'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { UX } from '@/utils/ux'
import { ExperimentConfig } from '@/utils/types'
import { storage } from '@/utils/storage'

export default function NewExperiment() {
    const router = useRouter()
    const [config, setConfig] = useState<ExperimentConfig>({
        nome_metrica: '',
        tipo_metrica: 'numerica',
        tamanho_amostral_calculado: 1000,
        intencao_teste: 'detectar_aumento',
        alfa: 0.05,
        metodologia: 'frequentista',
        tipo_correcao: 'Holm-Bonferroni',
        fator_inflacao: "Pocock",
        funcao_gasto_alfa: 'linear',
        valor_lambda: 1,
    })

    const [errors, setErrors] = useState<Record<string, string>>({})

    useEffect(() => {
        // Load existing config if available
        const saved = storage.loadConfig()
        if (saved) {
            setConfig(saved)
        }
    }, [])

    const validate = (): boolean => {
        const newErrors: Record<string, string> = {}

        if (!config.nome_metrica.trim()) {
            newErrors.nome_metrica = UX.validation.required
        }

        if (config.tamanho_amostral_calculado <= 0) {
            newErrors.tamanho_amostral_calculado = UX.validation.mustBePositive
        }

        if (config.alfa <= 0 || config.alfa >= 1) {
            newErrors.alfa = UX.validation.required
        }

        if (config.metodologia === 'testes_sequenciais') {
            if (!config.data_inicio_experimento) {
                newErrors.data_inicio_experimento = UX.validation.required
            }
            if (!config.data_fim_experimento) {
                newErrors.data_fim_experimento = UX.validation.required
            }
            if (config.data_inicio_experimento && config.data_fim_experimento) {
                const start = new Date(config.data_inicio_experimento)
                const end = new Date(config.data_fim_experimento)
                const diffDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
                if (diffDays < 14) {
                    newErrors.data_fim_experimento = UX.validation.sequentialMinDays
                }

                // O'Brien-Fleming constraint: k <= 4
                if (config.fator_inflacao === "O'Brien-Fleming") {
                    const k = Math.floor(diffDays / 7) - 1 // 2 weeks min -> 1 interim, 3 -> 2, 4 -> 3, 5 -> 4
                    if (k > 4) {
                        newErrors.fator_inflacao = "O fator O'Brien-Fleming suporta no máximo 4 análises interinas (aprox. 5 semanas)."
                    }
                }
            }
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (validate()) {
            storage.saveConfig(config)
            router.push('/experiments/run')
        }
    }

    const isSequential = config.metodologia === 'testes_sequenciais'

    return (
        <div className="container py-4">
            <h1 className="mb-4">{UX.titles.newExperiment}</h1>

            <form onSubmit={handleSubmit}>
                <div className="card mb-4">
                    <div className="card-body">
                        <h5 className="card-title mb-3">Configuração Básica</h5>

                        <div className="mb-3">
                            <label className="form-label">{UX.labels.nomeMetrica}</label>
                            <input
                                type="text"
                                className="form-control"
                                value={config.nome_metrica}
                                onChange={(e) => setConfig({ ...config, nome_metrica: e.target.value })}
                            />
                            {errors.nome_metrica && (
                                <div className="text-danger small mt-1">{errors.nome_metrica}</div>
                            )}
                        </div>

                        <div className="mb-3">
                            <label className="form-label">{UX.labels.tipoMetrica}</label>
                            <select
                                className="form-select"
                                value={config.tipo_metrica}
                                onChange={(e) => setConfig({ ...config, tipo_metrica: e.target.value })}
                            >
                                <option value="numerica">{UX.options.tipoMetrica.numerica}</option>
                                <option value="conversao">{UX.options.tipoMetrica.conversao}</option>
                            </select>
                            <div className="form-text">{UX.tooltips.tipoMetrica}</div>
                        </div>

                        <div className="mb-3">
                            <label className="form-label">{UX.labels.intencaoTeste}</label>
                            <select
                                className="form-select"
                                value={config.intencao_teste}
                                onChange={(e) => setConfig({ ...config, intencao_teste: e.target.value })}
                            >
                                <option value="detectar_aumento">{UX.options.intencaoTeste.detectar_aumento}</option>
                                <option value="detectar_reducao">{UX.options.intencaoTeste.detectar_reducao}</option>
                                <option value="detectar_diferenca">{UX.options.intencaoTeste.detectar_diferenca}</option>
                            </select>
                            <div className="form-text">{UX.tooltips.intencaoTeste}</div>
                        </div>

                        <div className="mb-3">
                            <label className="form-label">{UX.labels.metodologia}</label>
                            <select
                                className="form-select"
                                value={config.metodologia}
                                onChange={(e) => setConfig({ ...config, metodologia: e.target.value })}
                            >
                                <option value="frequentista">{UX.options.metodologia.frequentista}</option>
                                <option value="testes_sequenciais">{UX.options.metodologia.testes_sequenciais}</option>
                            </select>
                            {config.metodologia === 'testes_sequenciais' && (
                                <div className="form-text">{UX.tooltips.metodologiaSequencial}</div>
                            )}
                        </div>

                        <div className="row">
                            <div className="col-md-6 mb-3">
                                <label className="form-label">{UX.labels.alfa}</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    className="form-control"
                                    value={config.alfa}
                                    onChange={(e) => setConfig({ ...config, alfa: parseFloat(e.target.value) })}
                                />
                                {errors.alfa && (
                                    <div className="text-danger small mt-1">{errors.alfa}</div>
                                )}
                            </div>

                            <div className="col-md-6 mb-3">
                                <label className="form-label">{UX.labels.tamanhoAmostral}</label>
                                <input
                                    type="number"
                                    className="form-control"
                                    value={config.tamanho_amostral_calculado}
                                    onChange={(e) => setConfig({ ...config, tamanho_amostral_calculado: parseInt(e.target.value) })}
                                />
                                {errors.tamanho_amostral_calculado && (
                                    <div className="text-danger small mt-1">{errors.tamanho_amostral_calculado}</div>
                                )}
                            </div>
                        </div>

                        <div className="mb-3 d-none">
                            {/* Hidden since it moves to the next step */}
                            <label className="form-label">{UX.labels.tipoCorrecao}</label>
                            <select
                                className="form-select"
                                value={config.tipo_correcao}
                                onChange={(e) => setConfig({ ...config, tipo_correcao: e.target.value })}
                            >
                                <option value="Bonferroni">{UX.options.tipoCorrecao.Bonferroni}</option>
                                <option value="Holm-Bonferroni">{UX.options.tipoCorrecao['Holm-Bonferroni']}</option>
                                <option value="Sidak">{UX.options.tipoCorrecao.Sidak}</option>
                            </select>
                        </div>
                    </div>
                </div>

                {isSequential && (
                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title mb-3">Configuração de Testes Sequenciais</h5>

                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">{UX.labels.dataInicio}</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        value={config.data_inicio_experimento || ''}
                                        onChange={(e) => setConfig({ ...config, data_inicio_experimento: e.target.value })}
                                    />
                                    {errors.data_inicio_experimento && (
                                        <div className="text-danger small mt-1">{errors.data_inicio_experimento}</div>
                                    )}
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">{UX.labels.dataFim}</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        value={config.data_fim_experimento || ''}
                                        onChange={(e) => setConfig({ ...config, data_fim_experimento: e.target.value })}
                                    />
                                    {errors.data_fim_experimento && (
                                        <div className="text-danger small mt-1">{errors.data_fim_experimento}</div>
                                    )}
                                </div>
                            </div>

                            <div className="mb-3">
                                <label className="form-label">{UX.labels.funcaoGastoAlfa}</label>
                                <select
                                    className="form-select"
                                    value={config.funcao_gasto_alfa}
                                    onChange={(e) => setConfig({ ...config, funcao_gasto_alfa: e.target.value })}
                                >
                                    <option value="linear">{UX.options.funcaoGastoAlfa.linear}</option>
                                    <option value="obrien_fleming">{UX.options.funcaoGastoAlfa.obrien_fleming}</option>
                                    <option value="pocock">{UX.options.funcaoGastoAlfa.pocock}</option>
                                    <option value="exponencial">{UX.options.funcaoGastoAlfa.exponencial}</option>
                                    <option value="potencia">{UX.options.funcaoGastoAlfa.potencia}</option>
                                </select>
                                {config.funcao_gasto_alfa === 'obrien_fleming' && (
                                    <div className="form-text">{UX.tooltips.funcaoOBrienFleming}</div>
                                )}
                            </div>

                            <div className="mb-3">
                                <label className="form-label">{UX.labels.fatorInflacao}</label>
                                <select
                                    className="form-select"
                                    value={config.fator_inflacao}
                                    onChange={(e) => setConfig({ ...config, fator_inflacao: e.target.value })}
                                >
                                    <option value="Pocock">{UX.options.fatorInflacao.Pocock}</option>
                                    <option value="O'Brien-Fleming">{UX.options.fatorInflacao["O'Brien-Fleming"]}</option>
                                </select>
                                {errors.fator_inflacao && (
                                    <div className="text-danger small mt-1">{errors.fator_inflacao}</div>
                                )}
                            </div>

                            <div className="mb-3">
                                <label className="form-label">{UX.labels.valorLambda}</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    className="form-control"
                                    value={config.valor_lambda}
                                    onChange={(e) => setConfig({ ...config, valor_lambda: parseFloat(e.target.value) })}
                                />
                            </div>
                        </div>
                    </div>
                )}

                <div className="d-flex justify-content-end">
                    <button type="submit" className="btn btn-primary">
                        {UX.buttons.next}
                    </button>
                </div>
            </form>
        </div>
    )
}
