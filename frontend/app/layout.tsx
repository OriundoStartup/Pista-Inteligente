import { Analytics } from "@vercel/analytics/react"
import type { Metadata } from "next";
import Script from "next/script";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Chatbot from "@/components/Chatbot";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pista Inteligente - Predicciones Hípicas con IA",
  description: "Predicciones hípicas con Inteligencia Artificial para Hipódromo Chile y Club Hípico de Chile. Análisis profesional de carreras, pronósticos y estadísticas en tiempo real.",
  keywords: "programa hipódromo chile, club hípico de chile, predicciones hípicas, carreras de caballos chile, pronósticos hipódromo, análisis hípico, inteligencia artificial carreras",
  openGraph: {
    type: "website",
    title: "Pista Inteligente - Predicciones Hípicas con IA",
    description: "Predicciones con IA para Hipódromo Chile y Club Hípico de Chile",
    images: ["/header_brand.png"],
    locale: "es_CL",
    siteName: "Pista Inteligente",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pista Inteligente - Predicciones Hípicas",
    description: "Predicciones con IA para carreras de caballos en Chile",
    images: ["/header_brand.png"],
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
        {/* Google Fonts: Outfit */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap"
          rel="stylesheet"
        />

        {/* Google AdSense */}
        <Script
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

        {/* Top Ad Banner */}
        <div className="container" style={{ textAlign: 'center', margin: 0, padding: '0.5rem 0' }}>
          <ins
            className="adsbygoogle"
            style={{ display: 'block' }}
            data-ad-client="ca-pub-5579178295407019"
            data-ad-slot="1234567890"
            data-ad-format="auto"
            data-full-width-responsive="true"
          />
        </div>

        {/* Main Content */}
        <main className="container">
          {children}

          {/* Bottom Ad Banner */}
          <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <ins
              className="adsbygoogle"
              style={{ display: 'block' }}
              data-ad-client="ca-pub-5579178295407019"
              data-ad-slot="1234567890"
              data-ad-format="auto"
              data-full-width-responsive="true"
            />
          </div>
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
