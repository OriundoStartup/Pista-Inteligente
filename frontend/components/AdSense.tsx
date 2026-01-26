'use client'

import { useEffect } from 'react'

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
}

export function AdBanner({
    dataAdSlot,
    dataAdFormat = 'auto',
    dataFullWidthResponsive = true,
    className = '',
}: AdBannerProps) {
    useEffect(() => {
        try {
            if (typeof window !== 'undefined') {
                (window.adsbygoogle = window.adsbygoogle || []).push({})
            }
        } catch (err) {
            console.error('AdSense error:', err)
        }
    }, [])

    return (
        <div className={`ad-container ${className}`} style={{ minHeight: '100px', textAlign: 'center' }}>
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

// Anuncio automático que Google optimiza
export function AdAutoAds() {
    useEffect(() => {
        try {
            if (typeof window !== 'undefined') {
                (window.adsbygoogle = window.adsbygoogle || []).push({})
            }
        } catch (err) {
            console.error('AdSense Auto Ads error:', err)
        }
    }, [])

    return null
}

// Componente para inicializar AdSense (usar en layout)
export function AdSenseInit() {
    useEffect(() => {
        // Inicializar array de adsbygoogle si no existe
        if (typeof window !== 'undefined') {
            window.adsbygoogle = window.adsbygoogle || []
        }
    }, [])

    return null
}
