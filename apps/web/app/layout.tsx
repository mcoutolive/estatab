import type { Metadata } from 'next'
import 'bootstrap/dist/css/bootstrap.min.css'
import './globals.css'

export const metadata: Metadata = {
    title: 'EstatAB - Plataforma de Experimentação Estatística',
    description: 'Plataforma corporativa de experimentação estatística com testes sequenciais e controle rigoroso de significância',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="pt-BR">
            <body>
                <nav className="navbar navbar-dark bg-primary">
                    <div className="container-fluid">
                        <a className="navbar-brand brand-font" href="/">
                            EstatAB
                        </a>
                    </div>
                </nav>
                <main>
                    {children}
                </main>
                <footer className="bg-light text-center py-3 mt-5">
                    <div className="container">
                        <p className="text-muted mb-0">
                            © 2025 EstatAB - Plataforma corporativa de experimentação estatística
                        </p>
                    </div>
                </footer>
            </body>
        </html>
    )
}
