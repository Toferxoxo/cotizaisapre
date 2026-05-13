from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mail import Mail, Message
from datetime import datetime
from functools import wraps
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()  # Lee el archivo .env automáticamente

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'cambia_esto_por_algo_seguro')

# ─── Configuración de correo ────────────────────────────────────────────────
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD']       = os.getenv('MAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USER')

CORREO_ASESOR  = os.getenv('CORREO_ASESOR')
WA_NUMERO      = os.getenv('WA_NUMERO', '56912345678')   # sin +
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

mail = Mail(app)

# ─── Base de datos ──────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'cotizaciones.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre    TEXT    NOT NULL,
                correo    TEXT    NOT NULL,
                telefono  TEXT    NOT NULL,
                edad      INTEGER,
                isapre    TEXT,
                sueldo    TEXT,
                cargas    TEXT,
                region    TEXT,
                mensaje   TEXT,
                estado    TEXT    NOT NULL DEFAULT "Nuevo",
                fecha     TEXT    NOT NULL
            )
        ''')
        conn.commit()

def guardar_cotizacion(d: dict) -> int:
    with get_db() as conn:
        cur = conn.execute('''
            INSERT INTO cotizaciones
                (nombre, correo, telefono, edad, isapre, sueldo, cargas, region, mensaje, fecha)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (
            d['nombre'], d['correo'], d['telefono'],
            d.get('edad'), d.get('isapre'), d.get('sueldo'),
            d.get('cargas'), d.get('region'),
            d.get('msg', ''),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        return cur.lastrowid

# ─── Decorador login admin ──────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ─── Email HTML ─────────────────────────────────────────────────────────────
def build_email_html(d: dict, cid: int) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8">
    <style>
      body{{font-family:Arial,sans-serif;background:#f5f7ff;margin:0;padding:20px;}}
      .box{{background:white;border-radius:12px;max-width:560px;margin:0 auto;overflow:hidden;
            box-shadow:0 4px 20px rgba(0,0,0,.08);}}
      .header{{background:linear-gradient(135deg,#2563eb,#7c3aed);padding:24px 28px;}}
      .header h1{{color:white;margin:0;font-size:20px;}}
      .header p{{color:rgba(255,255,255,.75);margin:4px 0 0;font-size:14px;}}
      .body{{padding:24px 28px;}}
      .row{{display:flex;gap:12px;margin-bottom:12px;}}
      .field{{flex:1;background:#f5f7ff;border-radius:8px;padding:12px 14px;}}
      .field .lbl{{font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;
                   letter-spacing:.8px;margin-bottom:4px;}}
      .field .val{{font-size:15px;font-weight:600;color:#0f172a;}}
      .msg-box{{background:#f5f7ff;border-radius:8px;padding:14px;margin-top:4px;}}
      .msg-box .lbl{{font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;
                     letter-spacing:.8px;margin-bottom:6px;}}
      .msg-box p{{font-size:14px;color:#334155;margin:0;}}
      .footer{{background:#f8fafc;border-top:1px solid #e2e8f0;padding:14px 28px;
               font-size:12px;color:#94a3b8;text-align:center;}}
      .badge{{display:inline-block;background:#dcfce7;color:#059669;font-size:12px;
              font-weight:700;padding:3px 10px;border-radius:100px;}}
    </style>
    </head>
    <body>
    <div class="box">
      <div class="header">
        <h1>🏥 Nueva cotización #{cid}</h1>
        <p>{datetime.now().strftime('%d/%m/%Y a las %H:%M')} hrs &nbsp;·&nbsp; <span class="badge">Nuevo lead</span></p>
      </div>
      <div class="body">
        <div class="row">
          <div class="field"><div class="lbl">👤 Nombre</div><div class="val">{d['nombre']}</div></div>
          <div class="field"><div class="lbl">🎂 Edad</div><div class="val">{d.get('edad','—')}</div></div>
        </div>
        <div class="row">
          <div class="field"><div class="lbl">📧 Correo</div><div class="val">{d['correo']}</div></div>
          <div class="field"><div class="lbl">📱 Teléfono</div><div class="val">+569 {d['telefono']}</div></div>
        </div>
        <div class="row">
          <div class="field"><div class="lbl">💼 Isapre actual</div><div class="val">{d.get('isapre','—')}</div></div>
          <div class="field"><div class="lbl">💰 Sueldo</div><div class="val">{d.get('sueldo','—')}</div></div>
        </div>
        <div class="row">
          <div class="field"><div class="lbl">👨‍👩‍👧 Cargas</div><div class="val">{d.get('cargas','—')}</div></div>
          <div class="field"><div class="lbl">🌎 Región</div><div class="val">{d.get('region','—')}</div></div>
        </div>
        <div class="msg-box">
          <div class="lbl">💬 Mensaje</div>
          <p>{d.get('msg','Sin mensaje') or 'Sin mensaje'}</p>
        </div>
      </div>
      <div class="footer">CotizaIsapre · Sistema de cotizaciones automático</div>
    </div>
    </body></html>
    """

# ─── Rutas públicas ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', wa_numero=WA_NUMERO)

@app.route('/cotizar', methods=['POST'])
def cotizar():
    datos = request.get_json(silent=True) or {}

    # Validación
    for campo in ['nombre', 'correo', 'telefono']:
        if not str(datos.get(campo, '')).strip():
            return jsonify({'ok': False, 'error': f'El campo {campo} es requerido'}), 400

    # Guardar en BD
    cid = guardar_cotizacion(datos)

    # Enviar correo (no bloquea si falla)
    try:
        msg = Message(
            subject=f'🏥 Nueva cotización #{cid} — {datos["nombre"]}',
            recipients=[CORREO_ASESOR],
            html=build_email_html(datos, cid)
        )
        mail.send(msg)
    except Exception as e:
        print(f'[MAIL ERROR] {e}')

    return jsonify({'ok': True, 'id': cid})

# ─── Panel admin ─────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_leads'))
        error = 'Contraseña incorrecta'
    return render_template('login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/leads')
@login_required
def admin_leads():
    filtro  = request.args.get('estado', 'todos')
    buscar  = request.args.get('q', '').strip()
    with get_db() as conn:
        query  = 'SELECT * FROM cotizaciones'
        params = []
        conds  = []
        if filtro != 'todos':
            conds.append('estado = ?'); params.append(filtro)
        if buscar:
            conds.append('(nombre LIKE ? OR correo LIKE ? OR telefono LIKE ?)')
            params += [f'%{buscar}%'] * 3
        if conds:
            query += ' WHERE ' + ' AND '.join(conds)
        query += ' ORDER BY fecha DESC'
        rows = conn.execute(query, params).fetchall()
        total = conn.execute('SELECT COUNT(*) FROM cotizaciones').fetchone()[0]
        nuevos = conn.execute("SELECT COUNT(*) FROM cotizaciones WHERE estado='Nuevo'").fetchone()[0]
    return render_template('admin.html', leads=rows, filtro=filtro,
                           buscar=buscar, total=total, nuevos=nuevos)

@app.route('/admin/estado/<int:lid>', methods=['POST'])
@login_required
def cambiar_estado(lid):
    nuevo = request.form.get('estado')
    if nuevo in ('Nuevo', 'Contactado', 'Cerrado'):
        with get_db() as conn:
            conn.execute('UPDATE cotizaciones SET estado=? WHERE id=?', (nuevo, lid))
            conn.commit()
    return redirect(request.referrer or url_for('admin_leads'))

@app.route('/admin/eliminar/<int:lid>', methods=['POST'])
@login_required
def eliminar_lead(lid):
    with get_db() as conn:
        conn.execute('DELETE FROM cotizaciones WHERE id=?', (lid,))
        conn.commit()
    return redirect(url_for('admin_leads'))

# ─── Arranque ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
