export default function Loading() {
    return (
        <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '1rem' }}>
            <div style={{ textAlign: 'center', marginBottom: '2rem', animation: 'pulse 1.5s infinite alternate' }}>
                <div style={{ height: '2rem', width: '60%', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', margin: '0 auto 1rem' }}></div>
                <div style={{ height: '1rem', width: '80%', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', margin: '0 auto' }}></div>
            </div>

            <div className="glass-card" style={{ marginBottom: '1.5rem', animation: 'pulse 1.5s infinite alternate' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem', textAlign: 'center' }}>
                    {[1, 2, 3].map(i => (
                        <div key={i} style={{ padding: '1rem' }}>
                            <div style={{ height: '2.5rem', width: '50px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', margin: '0 auto 0.5rem' }}></div>
                            <div style={{ height: '1rem', width: '80%', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', margin: '0 auto' }}></div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="glass-card" style={{ animation: 'pulse 1.5s infinite alternate', opacity: 0.8 }}>
                <div style={{ height: '1.5rem', width: '200px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', marginBottom: '2rem' }}></div>

                {[1, 2].map(hipodromo => (
                    <div key={hipodromo} style={{ marginBottom: '1.5rem', borderLeft: '4px solid rgba(255,255,255,0.1)', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', padding: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                            <div style={{ height: '1.5rem', width: '250px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}></div>
                            <div style={{ height: '2rem', width: '100px', background: 'rgba(255,255,255,0.1)', borderRadius: '50px' }}></div>
                        </div>

                        {[1, 2, 3].map(carrera => (
                            <div key={carrera} style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', marginBottom: '1rem' }}>
                                <div style={{ height: '1.2rem', width: '150px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', marginBottom: '1rem' }}></div>
                                <div style={{ height: '150px', width: '100%', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}></div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
            <style>{`
                @keyframes pulse {
                    0% { opacity: 0.6; }
                    100% { opacity: 1; }
                }
            `}</style>
        </div>
    )
}
