import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
    title: 'Guía Completa de Hípica en Chile | Cómo Analizar Carreras de Caballos',
    description: 'Guía educativa sobre las carreras de caballos en Chile. Aprende sobre hipódromos, tipos de apuestas, cómo leer un programa hípico, terminología y consejos para analizar carreras.',
}

export default function GuiaPage() {
    return (
        <div className="container" style={{ padding: '2rem 0' }}>
            <article style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                    <h1 style={{ fontSize: 'clamp(1.75rem, 5vw, 2.5rem)', color: 'var(--text-main)', marginBottom: '0.75rem', fontWeight: 800 }}>
                        📖 Guía Completa de Hípica en Chile
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '700px', margin: '0 auto', lineHeight: 1.7 }}>
                        Todo lo que necesitas saber sobre las carreras de caballos en Chile: desde los conceptos básicos
                        hasta cómo interpretar un programa hípico. Una guía pensada tanto para principiantes como para
                        aficionados que quieran profundizar su conocimiento.
                    </p>
                </div>

                {/* Section 1: Introduction */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--primary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🏇 ¿Qué son las Carreras de Caballos?
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Las carreras de caballos, también conocidas como <strong>turf</strong> o <strong>hípica</strong>, son
                        competencias deportivas donde caballos purasangre corren sobre distancias predeterminadas en recintos
                        especializados llamados hipódromos. En Chile, la hípica tiene una tradición que se remonta a mediados
                        del siglo XIX, siendo uno de los deportes más antiguos del país.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Cada carrera tiene entre 6 y 16 caballos participantes (llamados <strong>partantes</strong>), cada uno
                        montado por un <strong>jinete</strong> profesional y preparado por un <strong>entrenador</strong> (o preparador).
                        Las distancias van desde los 800 metros (carreras &quot;sprint&quot;) hasta los 2.400 metros o más (carreras
                        &quot;de fondo&quot;).
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>
                        Los hipódromos chilenos ofrecen jornadas regulares durante todo el año, con un calendario que incluye
                        carreras comunes y <strong>clásicos</strong> (carreras especiales de mayor prestigio y premio). Las jornadas
                        típicamente constan de 8 a 14 carreras por día.
                    </p>
                </div>

                {/* Section 2: Hipódromos */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--secondary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🏟️ Los Hipódromos de Chile
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        Chile cuenta con cuatro hipódromos principales que operan regularmente. Cada uno tiene características
                        únicas en cuanto a la superficie de pista, longitud del recorrido y tipo de carreras que alberga.
                    </p>

                    <div style={{ display: 'grid', gap: '1rem' }}>
                        <div style={{ padding: '1.25rem', background: 'rgba(99, 102, 241, 0.06)', borderRadius: '12px', borderLeft: '3px solid var(--primary)' }}>
                            <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>Hipódromo Chile</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                <strong>Ubicación:</strong> Independencia, Santiago. <strong>Pista:</strong> Arena, 1.500 metros de circunferencia.
                                <strong> Actividad:</strong> Lunes a viernes durante todo el año. Es el hipódromo con mayor actividad del país,
                                ofreciendo jornadas casi diarias con carreras desde 800 hasta 2.400 metros. La pista de arena es más uniforme
                                que la de pasto y menos afectada por las condiciones climáticas.
                            </p>
                        </div>
                        <div style={{ padding: '1.25rem', background: 'rgba(52, 211, 153, 0.06)', borderRadius: '12px', borderLeft: '3px solid var(--secondary)' }}>
                            <h3 style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>Club Hípico de Santiago</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                <strong>Ubicación:</strong> Blanco Encalada, Santiago. <strong>Pista:</strong> Pasto, 2.000 metros de circunferencia.
                                <strong> Fundado:</strong> 1869. Es el recinto hípico más antiguo de Chile y alberga los clásicos más prestigiosos
                                del calendario nacional, como el St. Leger y el Gran Premio Nacional. Las carreras en pasto tienen dinámicas
                                diferentes: la superficie es más exigente y las condiciones climáticas (lluvia, humedad) la afectan significativamente.
                            </p>
                        </div>
                        <div style={{ padding: '1.25rem', background: 'rgba(16, 185, 129, 0.06)', borderRadius: '12px', borderLeft: '3px solid #10b981' }}>
                            <h3 style={{ color: '#10b981', marginBottom: '0.5rem', fontSize: '1.1rem' }}>Valparaíso Sporting Club</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                <strong>Ubicación:</strong> Viña del Mar. <strong>Pista:</strong> Pasto.
                                Conocido como la &quot;cuna de la hípica chilena&quot;, es sede del legendario <strong>Derby</strong>,
                                una de las carreras clásicas más importantes de Sudamérica. El clima costero de Viña del Mar agrega
                                un factor adicional: la brisa marina y la humedad pueden influir en el rendimiento de los caballos.
                            </p>
                        </div>
                        <div style={{ padding: '1.25rem', background: 'rgba(245, 158, 11, 0.06)', borderRadius: '12px', borderLeft: '3px solid #f59e0b' }}>
                            <h3 style={{ color: '#f59e0b', marginBottom: '0.5rem', fontSize: '1.1rem' }}>Club Hípico de Concepción</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                <strong>Ubicación:</strong> Hualpén, Biobío. Principal recinto del sur de Chile.
                                Ofrece jornadas regulares con carreras que complementan el circuito nacional, permitiendo
                                a caballos y jinetes del sur competir sin necesidad de trasladarse a Santiago.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Section 3: Reading a Program */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--accent)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        📋 Cómo Leer un Programa Hípico
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        El programa hípico (o programa del día) es el documento que detalla todas las carreras de una jornada.
                        Contiene información esencial sobre cada carrera y sus participantes. Entender cómo leerlo es fundamental
                        para analizar las carreras de forma informada.
                    </p>

                    <h3 style={{ color: 'var(--text-main)', fontSize: '1.1rem', marginBottom: '0.75rem' }}>Información de la Carrera</h3>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        <li><strong>Número de carrera:</strong> Orden correlativo dentro de la jornada (Carrera 1, Carrera 2, etc.).</li>
                        <li><strong>Distancia:</strong> Metros a recorrer (800m, 1000m, 1200m, 1400m, 1600m, 1800m, 2000m, etc.).</li>
                        <li><strong>Categoría:</strong> Nivel de competencia. Las categorías van desde las más bajas (nuevos ejemplares) hasta las más altas (caballos de élite).</li>
                        <li><strong>Superficie:</strong> Arena o pasto, según el hipódromo.</li>
                        <li><strong>Premio:</strong> Monto en dinero que se reparte entre los primeros lugares.</li>
                    </ul>

                    <h3 style={{ color: 'var(--text-main)', fontSize: '1.1rem', marginBottom: '0.75rem' }}>Información de Cada Partante</h3>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li><strong>Número (Mandil):</strong> El número que lleva el caballo en la carrera. En Pista Inteligente, las predicciones se muestran con este número.</li>
                        <li><strong>Caballo:</strong> Nombre del ejemplar.</li>
                        <li><strong>Jinete:</strong> Profesional que monta al caballo durante la carrera.</li>
                        <li><strong>Preparador:</strong> Entrenador responsable de la preparación física del caballo.</li>
                        <li><strong>Peso:</strong> Kilogramos que carga el caballo (incluye jinete y montura). A mayor peso, mayor esfuerzo.</li>
                        <li><strong>Posición de partida:</strong> Ubicación en las casillas de partida, del riel interior al exterior.</li>
                    </ul>
                </div>

                {/* Section 4: Types of Bets */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--primary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🎯 Tipos de Apuestas Hípicas
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        Existen diversas modalidades de apuestas hípicas, cada una con diferentes niveles de dificultad y
                        potencial de retorno. Las principales son:
                    </p>

                    <div style={{ display: 'grid', gap: '1rem' }}>
                        <div style={{ padding: '1rem', background: 'rgba(255, 215, 0, 0.06)', borderRadius: '8px', borderLeft: '3px solid #FFD700' }}>
                            <h3 style={{ color: '#FFD700', fontSize: '1rem', marginBottom: '0.25rem' }}>🥇 Ganador</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                Acertar qué caballo llegará primero. Es la apuesta más sencilla y directa.
                            </p>
                        </div>
                        <div style={{ padding: '1rem', background: 'rgba(192, 192, 192, 0.06)', borderRadius: '8px', borderLeft: '3px solid #C0C0C0' }}>
                            <h3 style={{ color: '#C0C0C0', fontSize: '1rem', marginBottom: '0.25rem' }}>🎯 Quiniela (Exacta)</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                Acertar los dos primeros lugares en el orden exacto de llegada. Mayor dificultad pero mejores dividendos.
                            </p>
                        </div>
                        <div style={{ padding: '1rem', background: 'rgba(205, 127, 50, 0.06)', borderRadius: '8px', borderLeft: '3px solid #CD7F32' }}>
                            <h3 style={{ color: '#CD7F32', fontSize: '1rem', marginBottom: '0.25rem' }}>🏆 Trifecta</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                Acertar los tres primeros lugares en orden exacto. Considerablemente más difícil, con dividendos proporcionalmente más altos.
                            </p>
                        </div>
                        <div style={{ padding: '1rem', background: 'rgba(99, 102, 241, 0.06)', borderRadius: '8px', borderLeft: '3px solid var(--primary)' }}>
                            <h3 style={{ color: 'var(--primary)', fontSize: '1rem', marginBottom: '0.25rem' }}>⭐ Superfecta</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7 }}>
                                Acertar los cuatro primeros lugares en orden exacto. La apuesta más difícil pero con los dividendos más altos.
                                Pista Inteligente predice los 4 primeros lugares de cada carrera, cubriendo esta modalidad.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Section 5: Glossary */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--secondary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        📚 Glosario de Términos Hípicos
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        La hípica tiene su propio vocabulario. Aquí explicamos los términos más comunes que encontrarás
                        en programas, resultados y en nuestra plataforma:
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '0.75rem' }}>
                        {[
                            { term: 'Partante', def: 'Caballo inscrito y confirmado para correr en una carrera específica.' },
                            { term: 'Mandil', def: 'Número que lleva el caballo durante la carrera, visible en su costado.' },
                            { term: 'Haras', def: 'Establecimiento donde nacen y se crían los caballos purasangre.' },
                            { term: 'Dividendo', def: 'Monto que se paga por cada peso apostado en un resultado ganador.' },
                            { term: 'Stud', def: 'Propietario o grupo de propietarios de un caballo de carrera.' },
                            { term: 'Cuerpo', def: 'Unidad de medida de distancia entre caballos al final de una carrera (~2.4 metros).' },
                            { term: 'Clásico', def: 'Carrera especial de mayor prestigio y premio dentro del calendario hípico.' },
                            { term: 'Pista pesada', def: 'Condición de la pista cuando está mojada por lluvia, más lenta y exigente.' },
                            { term: 'Riel', def: 'Baranda interior de la pista. Correr "por el riel" significa ir por el camino más corto.' },
                            { term: 'Score de Confianza', def: 'Métrica de Pista Inteligente que indica la probabilidad calibrada de cada caballo.' },
                        ].map((item, i) => (
                            <div key={i} style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                                <strong style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>{item.term}:</strong>{' '}
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{item.def}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Section 6: Responsible Gambling */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem', borderLeft: '4px solid var(--accent)' }}>
                    <h2 style={{ color: 'var(--accent)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        ⚠️ Juego Responsable
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Las apuestas hípicas son una forma de entretenimiento que implica riesgo financiero. En Pista Inteligente
                        promovemos el juego responsable y recomendamos:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li>Establece un presupuesto de entretenimiento y no lo excedas.</li>
                        <li>Nunca apuestes dinero que necesites para gastos esenciales.</li>
                        <li>Las predicciones de IA son herramientas de análisis, no garantías de ganancia.</li>
                        <li>Si sientes que las apuestas están afectando tu bienestar, busca ayuda profesional.</li>
                    </ul>
                </div>

                {/* CTA */}
                <div style={{ textAlign: 'center', padding: '2rem 1rem', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(52, 211, 153, 0.1))', borderRadius: '16px' }}>
                    <h2 style={{ color: 'var(--text-main)', marginBottom: '1rem', fontSize: 'clamp(1.25rem, 4vw, 1.75rem)' }}>
                        ¿Listo para ver las predicciones de hoy?
                    </h2>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', maxWidth: '500px', margin: '0 auto 1.5rem', lineHeight: 1.6 }}>
                        Ahora que conoces los conceptos básicos, consulta nuestras predicciones generadas por Inteligencia Artificial.
                    </p>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                        <Link href="/programa" className="cta-button" style={{ display: 'inline-block' }}>
                            Ver Predicciones
                        </Link>
                        <Link href="/metodologia" style={{ display: 'inline-block', padding: '1rem 2rem', border: '1px solid var(--primary)', borderRadius: '50px', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
                            Nuestra Metodología
                        </Link>
                    </div>
                </div>
            </article>
        </div>
    )
}
