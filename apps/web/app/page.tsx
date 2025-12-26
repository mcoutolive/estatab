'use client'

import { UX } from '@/utils/ux'
import { useRouter } from 'next/navigation'

export default function Home() {
    const router = useRouter()

    return (
        <div>
            <div className="hero-section">
                <div className="container">
                    <h1>{UX.titles.home}</h1>
                    <p className="lead">{UX.titles.homeSubtitle}</p>
                    <button
                        className="btn btn-light btn-lg"
                        onClick={() => router.push('/experiments/new')}
                    >
                        {UX.buttons.createExperiment}
                    </button>
                </div>
            </div>

            <div className="container py-5">
                <div className="row">
                    <div className="col-md-4 mb-4">
                        <div className="card h-100">
                            <div className="card-body">
                                <h5 className="card-title">Testes Sequenciais</h5>
                                <p className="card-text">
                                    Realize análises interinas com controle rigoroso do erro tipo I
                                    através de funções de gasto de alfa.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4 mb-4">
                        <div className="card h-100">
                            <div className="card-body">
                                <h5 className="card-title">Correções Múltiplas</h5>
                                <p className="card-text">
                                    Suporte para Bonferroni, Holm-Bonferroni e Šidák para controle
                                    de comparações múltiplas.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4 mb-4">
                        <div className="card h-100">
                            <div className="card-body">
                                <h5 className="card-title">Resultados Auditáveis</h5>
                                <p className="card-text">
                                    Relatórios completos com estatísticas de teste, p-valores
                                    ajustados e conclusões fundamentadas.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
