'use client'

import { useEffect, useRef } from 'react'

declare global {
    interface Window {
        adsbygoogle: any[]
    }
}

interface AdBannerProps {
    dataAdSlot: string
    dataAdFormat?: string
    dataFullWidthResponsive?: boolean
    className?: string
    showAd?: boolean
}

export function AdBanner({
    dataAdSlot,
    dataAdFormat = 'auto',
    dataFullWidthResponsive = true,
    className = '',
    showAd = true,
}: AdBannerProps) {
    const adRef = useRef<boolean>(false)

    useEffect(() => {
        if (!showAd) return
        // Guard: only push once per mount (avoids double-push in React StrictMode)
        if (adRef.current) return
        adRef.current = true

        try {
            if (typeof window !== 'undefined') {
                (window.adsbygoogle = window.adsbygoogle || []).push({})
            }
        } catch (err) {
            console.error('AdSense error:', err)
        }
    }, [])

    if (!showAd) return null

    return (
        <div className={`ad-container ${className}`}>
            <span className="ad-label">Publicidad</span>
            <ins
                className="adsbygoogle"
                style={{ display: 'block' }}
                data-ad-client="ca-pub-5579178295407019"
                data-ad-slot={dataAdSlot}
                data-ad-format={dataAdFormat}
                data-full-width-responsive={dataFullWidthResponsive.toString()}
            />
        </div>
    )
}

// ─── Variantes preconfiguradas ───────────────────────────────────

/** Banner horizontal responsive — ideal entre secciones */
export function AdBannerHorizontal({ className, showAd }: { className?: string; showAd?: boolean }) {
    return (
        <AdBanner
            dataAdSlot="auto"
            dataAdFormat="auto"
            dataFullWidthResponsive={true}
            className={className}
            showAd={showAd}
        />
    )
}

/** Anuncio In-Article — se inserta dentro del flujo de contenido */
export function AdBannerInArticle({ className, showAd }: { className?: string; showAd?: boolean }) {
    return (
        <AdBanner
            dataAdSlot="auto"
            dataAdFormat="fluid"
            dataFullWidthResponsive={true}
            className={`ad-in-article ${className || ''}`}
            showAd={showAd}
        />
    )
}

/** Anuncio Multiplex — grid de anuncios nativos al final del contenido */
export function AdBannerMultiplex({ className, showAd }: { className?: string; showAd?: boolean }) {
    return (
        <AdBanner
            dataAdSlot="auto"
            dataAdFormat="autorelaxed"
            dataFullWidthResponsive={true}
            className={`ad-multiplex ${className || ''}`}
            showAd={showAd}
        />
    )
}
