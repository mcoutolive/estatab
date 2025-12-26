'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { UX } from '@/utils/ux'
import { AnalyzeResponse } from '@/utils/types'
import { storage } from '@/utils/storage'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

export default function Results() {
    const router = useRouter()
    const [results, setResults] = useState<AnalyzeResponse | null>(null)

    useEffect(() => {
        const savedResults = storage.loadResults()
        if (!savedResults) {
            router.push('/experiments/new')
            return
        }
        setResults(savedResults)
    }, [router])

    if (!results) {
        return (
            <div className="container py-4">
                <div className="spinner"></div>
            </div>
        )
    }

    const chartData = results.comparacoes.map((comp) => ({
        name: comp.comparacao.split(' vs ')[0],
        efeito: comp.efeito,
    }))

    return (
        <div className="container py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>{UX.titles.results}</h1>
                <button
                    className="btn btn-primary"
                    onClick={() => {
                        storage.clearAll()
                        router.push('/')
                    }}
                >
                    {UX.buttons.newExperiment}
                </button>
            </div>

            {/* Summary Cards */}
            <div className="row mb-4">
                <div className="col-md-3 mb-3">
                    <div className="card h-100">
                        <div className="card-body">
                            <h6 className="card-subtitle mb-2 text-muted">{UX.summary.conclusaoFinal}</h6>
                            <p className="card-text fw-bold">{results.conclusao_final}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3 mb-3">
                    <div className="card h-100">
                        <div className="card-body">
                            <h6 className="card-subtitle mb-2 text-muted">{UX.summary.alfaEfetivo}</h6>
                            <p className="card-text fw-bold">{results.alfaEfetivo.toFixed(4)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3 mb-3">
                    <div className="card h-100">
                        <div className="card-body">
                            <h6 className="card-subtitle mb-2 text-muted">{UX.summary.metodologia}</h6>
                            <p className="card-text fw-bold">
                                {results.metodologia === 'frequentista'
                                    ? UX.options.metodologia.frequentista
                                    : UX.options.metodologia.testes_sequenciais}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="col-md-3 mb-3">
                    <div className="card h-100">
                        <div className="card-body">
                            <h6 className="card-subtitle mb-2 text-muted">{UX.summary.correcaoMultipla}</h6>
                            <p className="card-text fw-bold">{results.correcao.metodo}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Comparisons Table */}
            <div className="card mb-4">
                <div className="card-body">
                    <h5 className="card-title mb-3">Comparações Estatísticas</h5>
                    <div className="table-responsive">
                        <table className="table table-striped">
                            <thead>
                                <tr>
                                    <th>{UX.tableHeaders.comparacao}</th>
                                    <th>{UX.tableHeaders.teste}</th>
                                    <th>{UX.tableHeaders.estatistica}</th>
                                    <th>{UX.tableHeaders.pValorAjustado}</th>
                                    <th>{UX.tableHeaders.efeito}</th>
                                    <th>{UX.tableHeaders.rejeicaoH0}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.comparacoes.map((comp, index) => (
                                    <tr key={index}>
                                        <td>{comp.comparacao}</td>
                                        <td>{comp.teste}</td>
                                        <td>{comp.estatistica.toFixed(4)}</td>
                                        <td>{comp.pvalorAjustado.toFixed(4)}</td>
                                        <td>{(comp.efeito * 100).toFixed(2)}%</td>
                                        <td>
                                            {comp.rejeitaH0Corrigido ? (
                                                <span className="badge badge-success">Sim</span>
                                            ) : (
                                                <span className="badge badge-danger">Não</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Sequential Testing Panel */}
            {results.sequenciais && (
                <div className="card mb-4">
                    <div className="card-body">
                        <h5 className="card-title mb-3">Informações de Testes Sequenciais</h5>
                        <div className="row">
                            <div className="col-md-3 mb-3">
                                <strong>{UX.summary.alfaAcumulado}:</strong>
                                <p>{results.sequenciais.alfaAcumulado.toFixed(6)}</p>
                            </div>
                            <div className="col-md-3 mb-3">
                                <strong>{UX.summary.fatorInflacao}:</strong>
                                <p>{results.sequenciais.valorFatorInflacao.toFixed(4)}</p>
                            </div>
                            <div className="col-md-3 mb-3">
                                <strong>{UX.summary.completude}:</strong>
                                <p>{(results.sequenciais.completudeExperimento * 100).toFixed(1)}%</p>
                            </div>
                            {results.sequenciais.numeroTestesSequenciaisRealizados && (
                                <div className="col-md-3 mb-3">
                                    <strong>Número de análises interinas:</strong>
                                    <p>{results.sequenciais.numeroTestesSequenciaisRealizados}</p>
                                </div>
                            )}
                        </div>
                        {results.sequenciais.datasTestesSequenciais && results.sequenciais.datasTestesSequenciais.length > 0 && (
                            <div>
                                <strong>{UX.summary.datasInterinas}:</strong>
                                <p>{results.sequenciais.datasTestesSequenciais.join(', ')}</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Visualization */}
            <div className="card">
                <div className="card-body">
                    <h5 className="card-title mb-3">Efeito Estimado por Comparação</h5>
                    <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="name" />
                            <YAxis label={{ value: 'Efeito %', angle: -90, position: 'insideLeft' }} />
                            <Tooltip
                                formatter={(value: number) => [`${(value * 100).toFixed(2)}%`, 'Efeito']}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                            />
                            <Legend />
                            <Bar
                                dataKey="efeito"
                                name="Efeito Estimado"
                                radius={[4, 4, 0, 0]}
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.efeito > 0 ? '#198754' : '#dc3545'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    )
}
