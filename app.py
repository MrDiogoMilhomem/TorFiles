"""
Aplicação Flask principal.
Sistema de compartilhamento de arquivos seguro.
"""
import os
import sys

# Adicionar diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, redirect, url_for, session
from config import Config
from dotenv import load_dotenv

load_dotenv()

#Variaveis do LocalDev
LOCALDEV = os.environ.get("LOCALDEV", "false").lower() in ("True", "true", "1", "yes", "on")
LOCALDEV_DEBUG = os.environ.get("LOCALDEV_DEBUG", "false").lower() in ("True", "true", "1", "yes", "on")
LOCALDEV_HOST = os.environ.get("LOCALDEV_HOST")
LOCALDEV_PORT = os.environ.get("LOCALDEV_PORT")

# Criar aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configurações adicionais
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Importar e registrar blueprints
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.download import download_bp
from routes.dashboard import dashboard_bp
from routes.docs import docs_bp

app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(download_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(docs_bp)


@app.route('/')
def index():
    """Página inicial."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


@app.errorhandler(404)
def not_found(e):
    """Página de erro 404."""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Página de erro 500."""
    return render_template('errors/500.html'), 500


@app.errorhandler(413)
def request_entity_too_large(e):
    """Arquivo muito grande."""
    return render_template('errors/413.html'), 413


@app.context_processor
def inject_globals():
    """Injeta variáveis globais em todos os templates."""
    return {
        'current_user': session.get('username'),
        'is_authenticated': 'user_id' in session
    }


def init_databases():
    """Inicializa as tabelas nos bancos de dados."""
    try:
        from services.database import mariadb, postgres
        mariadb.init_tables()
        postgres.init_tables()
        print("Databases initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


def start_cleanup_worker():
    """Inicia o worker de limpeza."""
    try:
        from services.cleanup import cleanup_worker
        cleanup_worker.start()
        print("Cleanup worker started")
    except Exception as e:
        print(f"Cleanup worker error: {e}")


# Inicialização
with app.app_context():
    init_databases()
    start_cleanup_worker()


if __name__ == '__main__' and LOCALDEV:
    # Para desenvolvimento local
    print("-> Ambiente de desenvouvimento local ativo.")
    app.run(
        debug=LOCALDEV_DEBUG, 
        host=LOCALDEV_HOST, 
        port=LOCALDEV_PORT
    )
else: 
    print("-> Ambiente de desenvouvimento local desativo.")
