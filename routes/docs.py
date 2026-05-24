"""
Rotas de documentação.
Renderiza arquivos Markdown como HTML.
"""
import os
from flask import Blueprint, render_template, abort, current_app
import markdown2

docs_bp = Blueprint('docs', __name__)

# Diretório de documentação
DOCS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'docs'
)

# Ordem e títulos das páginas
DOCS_PAGES = [
    ('README', 'Visão Geral'),
    ('arquitetura', 'Arquitetura'),
    ('api', 'API'),
    ('database', 'Banco de Dados'),
    ('security', 'Segurança'),
    ('deployment', 'Deployment'),
    ('usage', 'Uso'),
]


def docs_enabled():
    """
    Verifica se a documentação está ativada.
    """
    return os.environ.get("DOCS_ENABLED", "true").lower() in ("True", "true", "1", "yes", "on")


def get_doc_content(filename):
    """
    Lê e converte um arquivo Markdown para HTML.
    """
    filepath = os.path.join(DOCS_DIR, f'{filename}.md')

    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Converter Markdown para HTML
    html = markdown2.markdown(
        content,
        extras=[
            'fenced-code-blocks',
            'tables',
            'header-ids',
            'code-friendly',
            'cuddled-lists',
        ]
    )

    return html


@docs_bp.route('/docs')
@docs_bp.route('/docs/')
def index():
    """
    Página principal da documentação.
    """

    if not docs_enabled():
        return render_template(
            'docs/disabled.html'
        ), 403

    return view('README')


@docs_bp.route('/docs/<page>')
def view(page):
    """
    Visualiza uma página de documentação.
    """

    if not docs_enabled():
        return render_template(
            'docs/disabled.html'
        ), 403

    # Verificar se a página existe
    valid_pages = [p[0] for p in DOCS_PAGES]

    if page not in valid_pages:
        abort(404)

    content = get_doc_content(page)

    if content is None:
        abort(404)

    # Encontrar título da página atual
    current_title = next(
        (
            title
            for name, title in DOCS_PAGES
            if name == page
        ),
        page
    )

    return render_template(
        'docs/viewer.html',
        content=content,
        current_page=page,
        current_title=current_title,
        pages=DOCS_PAGES
    )