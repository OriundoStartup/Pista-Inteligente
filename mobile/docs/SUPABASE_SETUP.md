# Supabase — Configuración Completa para Pista Inteligente

## 1. Tabla `push_tokens` (Push Notifications)

La app guarda tokens de Expo Push Notifications en Supabase para enviar notificaciones server-side.

### Cómo crear la tabla

1. Ir a **Supabase Dashboard → SQL Editor → New Query**
2. Copiar y pegar el contenido de [`SUPABASE_SETUP.sql`](./SUPABASE_SETUP.sql)
3. Click **Run** (o Ctrl+Enter)
4. Verificar que se creó correctamente:

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'push_tokens' 
ORDER BY ordinal_position;
```

Resultado esperado:

| column_name | data_type | is_nullable |
|---|---|---|
| id | uuid | NO |
| user_id | uuid | NO |
| token | text | NO |
| platform | text | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

### Verificar RLS

```sql
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE tablename = 'push_tokens';
```

Debe mostrar 5 policies (SELECT/INSERT/UPDATE/DELETE para users + SELECT para service_role).

---

## 2. OAuth con Google

### Redirect URIs en Supabase Dashboard

Ir a **Authentication → URL Configuration → Redirect URLs** y agregar:

```
pistainteligente://auth/callback
com.pistainteligente.app://auth/callback
https://pista-inteligente.vercel.app/auth/callback
exp://127.0.0.1:8081/--/auth/callback
```

| URI | Uso |
|---|---|
| `pistainteligente://auth/callback` | App mobile (producción/preview) |
| `com.pistainteligente.app://auth/callback` | Android bundle ID scheme |
| `https://pista-inteligente.vercel.app/auth/callback` | Frontend web |
| `exp://127.0.0.1:8081/--/auth/callback` | Expo Dev Client (desarrollo) |

### Google Cloud Console

1. **APIs & Services → Credentials → OAuth 2.0 Client IDs**
2. Agregar Authorized redirect URI:
   ```
   https://<TU-PROYECTO>.supabase.co/auth/v1/callback
   ```
3. Copiar **Client ID** y **Client Secret** y pegarlos en:
   **Supabase → Authentication → Providers → Google**

---

## 3. Testing Deep Links

### Android (Emulador o USB)

```bash
# Simular deep link de OAuth callback
adb shell am start -a android.intent.action.VIEW \
  -d "pistainteligente://auth/callback?code=test" \
  com.pistainteligente.app

# Con tokens en hash fragment (como Supabase los envía)
adb shell am start -a android.intent.action.VIEW \
  -d "pistainteligente://auth/callback#access_token=test123&refresh_token=test456" \
  com.pistainteligente.app
```

### iOS (Simulador)

```bash
# Simular deep link
xcrun simctl openurl booted "pistainteligente://auth/callback"

# Con tokens
xcrun simctl openurl booted "pistainteligente://auth/callback#access_token=test123&refresh_token=test456"

# Verificar qué schemes están registrados
xcrun simctl get_app_container booted com.pistainteligente.app
```

### Expo Dev Client

```bash
npx uri-scheme open "pistainteligente://auth/callback#access_token=test&refresh_token=test" --ios
```

---

## 4. Flujo Completo

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  perfil.tsx  │────▶│  WebBrowser  │────▶│  Google OAuth    │
│  signIn()   │     │  (in-app)    │     │  consent screen  │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  (tabs)/    │◀────│  callback.tsx │◀────│  Supabase       │
│  home       │     │  setSession()│     │  redirect URI   │
└─────────────┘     └──────────────┘     └─────────────────┘
```

---

## 5. Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| "No se encontraron tokens" | Redirect URI no está en Supabase | Agregar URI exacta en Dashboard |
| `ERR_BARE_REDIRECT` | Falta `skipBrowserRedirect` | Verificar config en `useAuth.ts` |
| App no se abre después del login | Scheme no registrado | Verificar `scheme` en `app.json` y rebuild |
| `push_tokens relation does not exist` | Tabla no creada | Ejecutar `SUPABASE_SETUP.sql` |
| Token no se guarda en Supabase | Usuario no autenticado | Solo se guarda para users con sesión activa |
| `401 Unauthorized` | Session no persistió | Verificar AsyncStorage en `supabase.ts` |
