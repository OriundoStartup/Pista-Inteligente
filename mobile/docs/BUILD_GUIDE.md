# 🏗️ Build Guide — Pista Inteligente Mobile

## 1. Antes del Build (Checklist)

- [ ] Crear cuenta en [expo.dev](https://expo.dev/signup)
- [ ] Ejecutar `npx eas login` (iniciar sesión en Expo)
- [ ] Ejecutar `cd mobile && npx eas init` (genera projectId)
- [ ] Reemplazar placeholders en `app.json`:

| Placeholder | Aparece | Acción |
|---|---|---|
| `REPLACE_WITH_EAS_PROJECT_ID` | 2 veces (`extra.eas.projectId` + `updates.url`) | Se llena con `eas init` |
| `REPLACE_WITH_EXPO_ACCOUNT` | 1 vez (`owner`) | Tu username de Expo |

- [ ] Verificar `.env` tiene las 4 variables:
```env
EXPO_PUBLIC_SUPABASE_URL=https://...supabase.co    # ✅ Requerido
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJ...               # ✅ Requerido
EXPO_PUBLIC_API_BASE_URL=https://pista-intel...     # ⚠️ Recomendado
EXPO_PUBLIC_DONATION_URL=https://link.merc...       # 🟢 Opcional
```

- [ ] **Android:** Descargar `google-services.json` de [Firebase Console](https://console.firebase.google.com) → Project Settings → General → Android
- [ ] **iOS:** Tener [Apple Developer Account](https://developer.apple.com) ($99 USD/año)

---

## 2. Primer Build Android (sin Apple account)

### Build preview (APK para testing)

```bash
cd mobile
npx eas build --profile preview --platform android
```

EAS compila en la nube (~5-10 min). Al terminar, te da un link para descargar el `.apk`.

### Instalar en device físico

```bash
# Opción 1: Descargar el .apk directo desde el link de EAS

# Opción 2: Con adb (si tienes el device conectado por USB)
adb install -r path/to/pista-inteligente.apk
```

### Probar OAuth deep link en el build real

```bash
# Abrir la app y navegar a Perfil → Login → Google
# Después del login, verificar que el deep link funciona:
adb shell am start -a android.intent.action.VIEW \
  -d "pistainteligente://auth/callback#access_token=test" \
  com.pistainteligente.app
```

### Build producción (AAB para Play Store)

```bash
npx eas build --profile production --platform android
```

Genera `.aab` (Android App Bundle) optimizado para Play Store.

---

## 3. Primer Build iOS

### Build preview (para TestFlight)

```bash
npx eas build --profile preview --platform ios
```

### Credenciales que EAS pide automáticamente

En el primer build, EAS te preguntará:

1. **Distribution Certificate** → Selecciona "Let EAS handle it" (recomendado)
2. **Provisioning Profile** → Selecciona "Let EAS handle it"
3. **Apple ID** → Tu correo de Apple Developer
4. **Apple Team** → Si tienes múltiples teams, elige el correcto

> 💡 EAS guarda las credenciales en su servidor de forma segura. No necesitas Xcode.

### Probar deep link en iOS Simulator

```bash
xcrun simctl openurl booted "pistainteligente://auth/callback#access_token=test"
```

### Distribuir via TestFlight

```bash
# Primero, build de producción:
npx eas build --profile production --platform ios

# Luego submit a App Store Connect:
npx eas submit --platform ios
```

La app aparece en TestFlight automáticamente después del review (~24-48h).

---

## 4. Submit a Stores

### Google Play Store

```bash
# Requiere google-services.json configurado en eas.json
npx eas submit --platform android --profile production
```

**Antes de submit:**
- Crear la app en [Google Play Console](https://play.google.com/console)
- Configurar el Service Account key ([guía](https://docs.expo.dev/submit/android/))
- Tener screenshots, descripción, y política de privacidad

### Apple App Store

```bash
# Requiere Apple Developer account
npx eas submit --platform ios --profile production
```

**Antes de submit:**
- Crear la app en [App Store Connect](https://appstoreconnect.apple.com)
- Configurar credenciales en `eas.json` → `submit.production.ios`
- Tener screenshots, descripción, y info de clasificación

### Metadata necesaria para ambas stores

| Campo | Valor |
|---|---|
| Nombre | Pista Inteligente |
| Descripción corta | Predicciones hípicas con IA para Chile |
| Categoría | Deportes / Entretenimiento |
| Clasificación | 17+ (referencias a apuestas) |
| Privacidad | `https://pista-inteligente.vercel.app/politica-de-privacidad` |
| Screenshots | 5-8 por dispositivo |
| Idioma | Español (Chile) |

### Links útiles

- [EAS Build docs](https://docs.expo.dev/build/introduction/)
- [EAS Submit docs](https://docs.expo.dev/submit/introduction/)
- [Google Play Console](https://play.google.com/console)
- [App Store Connect](https://appstoreconnect.apple.com)
- [Expo Credentials](https://docs.expo.dev/app-signing/managed-credentials/)

---

## 5. CORS (si chatbot o análisis fallan)

Si las llamadas a `/api/chat` o `/api/analisis/patrones` fallan desde la app, agregar headers CORS en las API routes de Next.js:

```typescript
// frontend/app/api/chat/route.ts (y analisis/patrones/route.ts)
export async function OPTIONS() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
```
