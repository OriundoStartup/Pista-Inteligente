import { Analytics } from "@vercel/analytics/react"
import type { Metadata } from "next";
import Script from "next/script";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Chatbot from "@/components/Chatbot";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pista Inteligente - Predicciones Hípicas con IA | Teletrak Chile",
  description: "Predicciones hípicas con Inteligencia Artificial para Hipódromo Chile, Club Hípico de Santiago y Valparaíso Sporting. Pronósticos de carreras de caballos, programa del día, resultados y análisis profesional. Alternativa inteligente a Teletrak con IA.",
  keywords: [
    // Hipódromos principales
    "hipódromo chile", "club hípico de santiago", "valparaíso sporting", "hipódromo chile carreras hoy",
    // Teletrak y apuestas
    "teletrak", "teletrak chile", "teletrak carreras", "teletrak en vivo", "teletrak resultados",
    // Carreras de caballos
    "carreras de caballos chile", "carreras de caballos hoy", "programa carreras de caballos",
    "resultados carreras de caballos", "caballos chile",
    // Predicciones y pronósticos
    "predicciones hípicas", "pronósticos hipódromo", "predicciones carreras de caballos",
    "pronosticos turf chile", "picks carreras chile",
    // Apuestas hípicas
    "apuestas hípicas chile", "apuestas caballos chile", "quinela hipódromo", "exacta hipódromo",
    // Análisis
    "análisis hípico", "estadísticas jinetes chile", "inteligencia artificial carreras",
    // Programa del día
    "programa hipódromo chile hoy", "programa club hípico hoy", "partantes del día"
  ].join(", "),
  authors: [{ name: "Pista Inteligente" }],
  creator: "Pista Inteligente",
  publisher: "Pista Inteligente",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "https://pista-inteligente.vercel.app",
  },
  category: "Sports",
  openGraph: {
    type: "website",
    title: "Pista Inteligente - Predicciones Hípicas con IA | Teletrak Chile",
    description: "Predicciones con IA para Hipódromo Chile, Club Hípico de Santiago y Valparaíso Sporting. Pronósticos, programa del día, resultados y análisis de carreras de caballos.",
    url: "https://pista-inteligente.vercel.app",
    images: [{
      url: "/header_brand.png",
      width: 1200,
      height: 630,
      alt: "Pista Inteligente - Predicciones Hípicas con Inteligencia Artificial"
    }],
    locale: "es_CL",
    siteName: "Pista Inteligente",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pista Inteligente - Predicciones Hípicas con IA",
    description: "Predicciones y pronósticos para carreras de caballos en Chile. Hipódromo Chile, Club Hípico y Valparaíso Sporting.",
    images: ["/header_brand.png"],
    creator: "@PistaInteligente",
  },
  verification: {
    google: "tu-codigo-de-verificacion-google", // Actualizar con tu código real de Google Search Console
  },
  other: {
    "geo.region": "CL",
    "geo.placename": "Santiago, Chile",
    "content-language": "es-CL",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <head>
        {/* Mobile Viewport - Essential for responsive design */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover" />
        <meta name="theme-color" content="#0f172a" />

        {/* Google AdSense Verification Meta Tag */}
        <meta name="google-adsense-account" content="ca-pub-5579178295407019" />

        {/* Google Fonts: Outfit */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap"
          rel="stylesheet"
        />

        {/* JSON-LD Structured Data for SEO */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@graph": [
                {
                  "@type": "WebSite",
                  "@id": "https://pista-inteligente.vercel.app/#website",
                  "url": "https://pista-inteligente.vercel.app",
                  "name": "Pista Inteligente",
                  "description": "Predicciones hípicas con Inteligencia Artificial para carreras de caballos en Chile",
                  "publisher": { "@id": "https://pista-inteligente.vercel.app/#organization" },
                  "inLanguage": "es-CL",
                  "potentialAction": {
                    "@type": "SearchAction",
                    "target": "https://pista-inteligente.vercel.app/programa?q={search_term_string}",
                    "query-input": "required name=search_term_string"
                  }
                },
                {
                  "@type": "Organization",
                  "@id": "https://pista-inteligente.vercel.app/#organization",
                  "name": "Pista Inteligente",
                  "url": "https://pista-inteligente.vercel.app",
                  "logo": {
                    "@type": "ImageObject",
                    "url": "https://pista-inteligente.vercel.app/header_brand.png"
                  },
                  "description": "Plataforma de predicciones hípicas con IA para Hipódromo Chile, Club Hípico de Santiago y Valparaíso Sporting",
                  "areaServed": {
                    "@type": "Country",
                    "name": "Chile"
                  },
                  "knowsAbout": [
                    "Carreras de caballos",
                    "Hipódromo Chile",
                    "Club Hípico de Santiago",
                    "Valparaíso Sporting",
                    "Teletrak",
                    "Predicciones hípicas",
                    "Inteligencia Artificial"
                  ]
                },
                {
                  "@type": "SportsOrganization",
                  "name": "Pista Inteligente - Análisis Hípico",
                  "sport": "Horse Racing",
                  "url": "https://pista-inteligente.vercel.app",
                  "description": "Análisis y predicciones para carreras de caballos en los principales hipódromos de Chile"
                }
              ]
            })
          }}
        />

        {/* 
          Google AdSense Script - Carga el SDK de AdSense
          Este script habilita Auto Ads, que Google optimiza automáticamente
          para colocar anuncios en las mejores posiciones de tu sitio.
        */}
        <Script
          id="adsense-script"
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5579178295407019"
          crossOrigin="anonymous"
          strategy="afterInteractive"
        />
      </head>
      <body>
        {/* Header */}
        <Header />

        {/* Hero Banner */}
        <div className="hero-banner">
          <img
            src="/header_brand.png"
            alt="Pista Inteligente - Programa Hipódromo Chile y Club Hípico de Chile con Predicciones IA"
            className="hero-banner-img"
          />
        </div>

        {/* Main Content */}
        <main className="container">
          {children}
        </main>

        {/* Chatbot Widget */}
        <Chatbot />

        {/* Footer */}
        <Footer />
        <Analytics />
      </body>
    </html>
  );
}
