# 📋 Checklist de Publicación — Pista Inteligente Mobile

## 🔴 Bloqueantes (no se puede publicar sin esto)

- [ ] Ejecutar `npx eas init` → obtener projectId real
- [ ] Reemplazar `REPLACE_WITH_EAS_PROJECT_ID` en `app.json` (aparece 2 veces: `extra.eas.projectId` y `updates.url`)
- [ ] Reemplazar `REPLACE_WITH_EXPO_ACCOUNT` en `app.json` → `owner`
- [ ] Verificar `.env` tiene `EXPO_PUBLIC_SUPABASE_URL` y `EXPO_PUBLIC_SUPABASE_ANON_KEY`
- [ ] Agregar `EXPO_PUBLIC_API_BASE_URL` a `.env` (chatbot + análisis lo necesitan)
- [ ] Configurar credenciales Apple en `eas.json` → `submit.production.ios` (appleId, ascAppId, appleTeamId)
- [ ] Generar `google-services.json` desde Firebase/Play Console y colocarlo en `/mobile/`
- [ ] Crear tabla `push_tokens` en Supabase (ejecutar `docs/SUPABASE_SETUP.sql`)
- [ ] Configurar Redirect URIs en Supabase Dashboard (ver `docs/SUPABASE_SETUP.md`)
- [ ] Reemplazar assets placeholder con ícono y splash real (1024×1024 px)

## 🟡 Recomendados (publicar con estos resueltos)

- [ ] Agregar `EXPO_PUBLIC_DONATION_URL` a `.env` (botón donación no se muestra sin esta var)
- [ ] Build de prueba: `npx eas build --profile preview --platform android`
- [ ] Probar OAuth en build real (no solo dev server) — el deep linking es el punto más frágil
- [ ] Probar deep link: `adb shell am start -a android.intent.action.VIEW -d "pistainteligente://auth/callback"`
- [ ] Verificar que la app funciona sin conexión (debe mostrar datos cacheados + OfflineBanner)
- [ ] Preparar screenshots para App Store / Play Store (5-8 por dispositivo)
- [ ] Redactar descripción larga para stores (500+ caracteres)
- [ ] Configurar CORS en API routes de Next.js si chatbot/análisis fallan desde la app

## 🟢 Opcionales (mejoras post-lanzamiento)

- [ ] Agregar `expo-haptics` para feedback táctil en tab bar
- [ ] Splash screen animado con `expo-splash-screen` avanzado
- [ ] Toggle dark/light theme
- [ ] Internacionalización (i18n) — español por defecto, inglés opcional
- [ ] Rate limiting en chatbot (evitar spam de requests)
- [ ] Agregar tests unitarios (Jest + Testing Library) para hooks y componentes
- [ ] Configurar CI/CD con GitHub Actions (ver `.github/workflows/expo-checks.yml`)
- [ ] Agregar badge de "unread messages" al ChatFAB
- [ ] Implementar SSE streaming en el chatbot (si la API lo soporta)
- [ ] Analytics con `expo-analytics` o similar
