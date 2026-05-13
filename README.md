# 🏥 CotizaIsapre — Instrucciones de instalación

## Estructura del proyecto
```
isapre_app/
├── app.py
├── requirements.txt
├── .env.example        ← copia esto como .env y rellena
├── .env                ← NO subir a GitHub
├── cotizaciones.db     ← se crea automático al correr
├── static/
│   └── img/
│       └── hero.png
└── templates/
    ├── index.html
    ├── admin.html
    └── login.html
```

---

## ▶️ Paso 1 — Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Paso 2 — Configurar el .env

1. Renombra `.env.example` → `.env`
2. Abre `.env` y rellena:
   - `MAIL_USER` → tu Gmail
   - `MAIL_PASS` → contraseña de aplicación Gmail (ver abajo)
   - `CORREO_ASESOR` → el correo donde llegan los leads
   - `WA_NUMERO` → número WhatsApp sin + (ej: 56912345678)
   - `ADMIN_PASSWORD` → contraseña del panel admin

### ¿Cómo obtener la contraseña de aplicación Gmail?
1. Entra a [myaccount.google.com](https://myaccount.google.com)
2. **Seguridad** → **Verificación en dos pasos** (debe estar activa)
3. Busca **"Contraseñas de aplicaciones"**
4. Selecciona App: `Correo` / Dispositivo: `Windows`
5. Copia los 16 caracteres generados → pégalos en `MAIL_PASS`

---

## ▶️ Paso 3 — Correr el servidor

```bash
python app.py
```

Abre [http://localhost:5000](http://localhost:5000)

---

## 📊 Panel de administración

Entra a [http://localhost:5000/admin/leads](http://localhost:5000/admin/leads)

Ingresa la contraseña que pusiste en `ADMIN_PASSWORD`.

Desde el panel puedes:
- Ver todos los leads recibidos
- Cambiar el estado: **Nuevo → Contactado → Cerrado**
- Hacer clic en el número pa' abrir WhatsApp directo
- Buscar por nombre, correo o teléfono
- Eliminar leads

---

## 🌐 Subir a producción (gratis)

### Opción A — Render.com
1. Sube el proyecto a GitHub (sin el .env)
2. Entra a [render.com](https://render.com) → New Web Service
3. Conecta el repo → Runtime: Python 3
4. Start command: `python app.py`
5. En **Environment Variables** agrega las mismas del `.env`

### Opción B — PythonAnywhere
1. Crea cuenta en [pythonanywhere.com](https://pythonanywhere.com)
2. Sube los archivos por el File Manager
3. Configura el Web App apuntando a `app.py`
