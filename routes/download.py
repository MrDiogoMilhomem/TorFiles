"""
Rotas de download de arquivos.
Acesso via código de 5 dígitos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, Response
from models.file import File
from utils.validators import validate_code, sanitize_input
from utils.rate_limiter import rate_limiter, get_rate_limit_key
from utils.helpers import format_timedelta
import io
import traceback

download_bp = Blueprint('download', __name__)


@download_bp.route('/d', methods=['GET', 'POST'])
@download_bp.route('/d/<code>', methods=['GET', 'POST'])
def access(code=None):
    """
    Página de acesso a arquivo via código.
    
    GET com código: Mostra informações do arquivo
    POST com código: Processa download
    GET sem código: Mostra formulário para inserir código
    """
    # Se não tem código, mostrar formulário
    if not code:
        if request.method == 'POST':
            code = sanitize_input(request.form.get('code', '').strip().upper())
            if code:
                return redirect(url_for('download.access', code=code))
            flash('Insira um código válido.', 'error')
        return render_template('download/access.html', show_code_form=True)
    
    # Validar código
    valid, error = validate_code(code)
    if not valid:
        flash(error, 'error')
        return render_template('download/access.html', show_code_form=True)
    
    # Rate limiting para busca de código
    key = get_rate_limit_key(request, f'code:{code}')
    if rate_limiter.is_rate_limited(key):
        remaining = rate_limiter.get_remaining_time(key)
        flash(f'Muitas tentativas. Aguarde {remaining} segundos.', 'error')
        return render_template('download/access.html', show_code_form=True)
    
    # Buscar arquivo
    file = File.find_by_code(code.upper())
    
    if not file:
        rate_limiter.record_attempt(key)
        flash('Código não encontrado.', 'error')
        return render_template('download/access.html', show_code_form=True)
    
    # Verificar se pode ser baixado
    if not file.is_downloadable():
        if file.status == 'paused':
            flash('Este arquivo está pausado pelo proprietário.', 'warning')
        elif file.is_expired():
            flash('Este arquivo expirou.', 'warning')
        else:
            flash('Este arquivo não está disponível para download.', 'warning')
        return render_template('download/access.html', show_code_form=True)
    
    # Processar download
    if request.method == 'POST' and 'download' in request.form:
        password = request.form.get('password', '').strip() or None
        
        # Verificar senha se necessário
        if file.has_password:
            if not password:
                flash('Este arquivo requer senha.', 'error')
                return render_template('download/access.html', 
                                       file=file,
                                       time_remaining=format_timedelta(file.time_remaining()))
            
            if not file.verify_download_password(password):
                rate_limiter.record_attempt(get_rate_limit_key(request, f'pwd:{code}'))
                flash('Senha incorreta.', 'error')
                return render_template('download/access.html',
                                       file=file,
                                       time_remaining=format_timedelta(file.time_remaining()))
        
        try:
            # Descriptografar arquivo
            decrypted_data = file.decrypt(password)
            
            if not decrypted_data:
                flash('Erro ao recuperar arquivo.', 'error')
                return render_template('download/access.html',
                                       file=file,
                                       time_remaining=format_timedelta(file.time_remaining()))
            
            # Decrementar contador
            file.decrement_downloads()
            
            # Enviar arquivo
            return Response(
                decrypted_data,
                mimetype='application/octet-stream',
                headers={
                    'Content-Disposition': f'attachment; filename="{file.filename}"',
                    'Content-Length': len(decrypted_data)
                }
            )
        
        except Exception as e:
            flash('Erro ao processar download.', 'error')
            print("ERRO REAL:")
            traceback.print_exc()
            return render_template('download/access.html',
                                   file=file,
                                   time_remaining=format_timedelta(file.time_remaining()))
    
    # Mostrar informações do arquivo
    return render_template('download/access.html',
                           file=file,
                           time_remaining=format_timedelta(file.time_remaining()))
