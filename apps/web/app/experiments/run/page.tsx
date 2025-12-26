'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { UX } from '@/utils/ux'
import { Variante, AnalyzeRequest } from '@/utils/types'
import { storage } from '@/utils/storage'

export default function RunExperiment() {
    const router = useRouter()
    const [config, setConfig] = useState<any>(null)
    const [variantes, setVariantes] = useState<Variante[]>([
        {
            nome_variante: '',
            numero_amostras: 0,
            valor_media: 0,
            desvio_padrao: 0,
            variante_controle: false,
        },
    ])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const savedConfig = storage.loadConfig()
        if (!savedConfig) {
            router.push('/experiments/new')
            return
        }
        setConfig(savedConfig)

        const savedVariantes = storage.loadVariantes()
        if (savedVariantes && savedVariantes.length > 0) {
            setVariantes(savedVariantes)
        }
    }, [router])

    const addVariante = () => {
        setVariantes([
            ...variantes,
            {
                nome_variante: '',
                numero_amostras: 0,
                valor_media: 0,
                desvio_padrao: 0,
                variante_controle: false,
            },
        ])
    }

    const removeVariante = (index: number) => {
        setVariantes(variantes.filter((_, i) => i !== index))
    }

    const updateVariante = (index: number, field: keyof Variante, value: any) => {
        const updated = [...variantes]
        updated[index] = { ...updated[index], [field]: value }
        setVariantes(updated)
    }

    const validate = (): boolean => {
        const controlCount = variantes.filter((v) => v.variante_controle).length
        if (controlCount !== 1) {
            setError(UX.validation.exactlyOneControl)
            return false
        }

        if (variantes.length < 2) {
            setError(UX.validation.atLeastTwoVariants)
            return false
        }

        for (const v of variantes) {
            if (!v.nome_variante.trim()) {
                setError(UX.validation.required)
                return false
            }
            if (v.numero_amostras <= 0) {
                setError(UX.validation.mustBePositive)
                return false
            }
            if (config.tipo_metrica === 'numerica' && !v.desvio_padrao) {
                setError(UX.validation.desvioPadraoRequired)
                return false
            }
        }

        return true
    }

    const handleExecute = async () => {
        setError(null)
        if (!validate()) {
            return
        }

        storage.saveVariantes(variantes)

        const request: AnalyzeRequest = {
            config,
            variantes,
        }

        setLoading(true)

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            const response = await fetch(`${apiUrl}/v1/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || UX.errors.analysisError)
            }

            const result = await response.json()
            storage.saveResults(result)
            router.push('/experiments/results')
        } catch (err: any) {
            setError(err.message || UX.errors.apiUnavailable)
        } finally {
            setLoading(false)
        }
    }

    if (!config) {
        return <div className="container py-4"><div className="spinner"></div></div>
    }

    const isNumeric = config.tipo_metrica === 'numerica'

    return (
        <div className="container py-4">
            <h1 className="mb-4">{UX.titles.runExperiment}</h1>

            <div className="card mb-4">
                <div className="card-body">
                    <h5 className="card-title">Configuração do Experimento</h5>
                    <p className="mb-1"><strong>Métrica:</strong> {config.nome_metrica}</p>
                    <p className="mb-1"><strong>Tipo:</strong> {config.tipo_metrica}</p>
                    <p className="mb-1"><strong>Metodologia:</strong> {config.metodologia}</p>
                    <p className="mb-0"><strong>Alfa:</strong> {config.alfa}</p>
                </div>
            </div>

            {variantes.length > 2 && (
                <div className="card mb-4 border-primary">
                    <div className="card-body">
                        <h5 className="card-title mb-3">Correção para Múltiplas Comparações</h5>
                        <div className="mb-3">
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
                            <div className="form-text">{UX.tooltips.correcaoHolm}</div>
                        </div>
                    </div>
                </div>
            )}

            {error && (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            )}

            <div className="card mb-4">
                <div className="card-body">
                    <h5 className="card-title mb-3">Variantes</h5>
                    <div className="form-text mb-3">{UX.tooltips.varianteControle}</div>

                    {variantes.map((variante, index) => (
                        <div key={index} className="border rounded p-3 mb-3">
                            <div className="d-flex justify-content-between align-items-center mb-3">
                                <h6 className="mb-0">Variante {index + 1}</h6>
                                {variantes.length > 1 && (
                                    <button
                                        type="button"
                                        className="btn btn-danger btn-sm"
                                        onClick={() => removeVariante(index)}
                                    >
                                        {UX.buttons.removeVariant}
                                    </button>
                                )}
                            </div>

                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">{UX.labels.nomeVariante}</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        value={variante.nome_variante}
                                        onChange={(e) => updateVariante(index, 'nome_variante', e.target.value)}
                                    />
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">{UX.labels.numeroAmostras}</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={variante.numero_amostras}
                                        onChange={(e) => updateVariante(index, 'numero_amostras', parseInt(e.target.value) || 0)}
                                    />
                                </div>
                            </div>

                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        {isNumeric ? UX.labels.valorMedia : UX.labels.taxa}
                                    </label>
                                    <input
                                        type="number"
                                        step="0.001"
                                        className="form-control"
                                        value={variante.valor_media}
                                        onChange={(e) => updateVariante(index, 'valor_media', parseFloat(e.target.value) || 0)}
                                    />
                                </div>

                                {isNumeric && (
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label">{UX.labels.desvioPadrao}</label>
                                        <input
                                            type="number"
                                            step="0.001"
                                            className="form-control"
                                            value={variante.desvio_padrao || ''}
                                            onChange={(e) => updateVariante(index, 'desvio_padrao', parseFloat(e.target.value) || undefined)}
                                        />
                                    </div>
                                )}
                            </div>

                            <div className="form-check">
                                <input
                                    className="form-check-input"
                                    type="checkbox"
                                    id={`control-${index}`}
                                    checked={variante.variante_controle}
                                    onChange={(e) => updateVariante(index, 'variante_controle', e.target.checked)}
                                />
                                <label className="form-check-label" htmlFor={`control-${index}`}>
                                    {UX.labels.varianteControle}
                                </label>
                            </div>
                        </div>
                    ))}

                    <button type="button" className="btn btn-secondary" onClick={addVariante}>
                        {UX.buttons.addVariant}
                    </button>
                </div>
            </div>

            <div className="d-flex justify-content-end gap-2">
                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => router.push('/experiments/new')}
                    disabled={loading}
                >
                    Voltar
                </button>
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleExecute}
                    disabled={loading}
                >
                    {loading ? UX.loading.analyzing : UX.buttons.executeAnalysis}
                </button>
            </div>

            {loading && (
                <div className="text-center mt-4">
                    <div className="spinner"></div>
                    <p className="text-muted mt-2">{UX.loading.analyzing}</p>
                </div>
            )}
        </div>
    )
}
