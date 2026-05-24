"""
Rotas de autenticação.
Registro, login e logout.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from utils.validators import validate_username, validate_password, sanitize_input
from utils.rate_limiter import rate_limiter, get_rate_limit_key

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página e processamento de registro."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Rate limiting
        key = get_rate_limit_key(request, 'register')
        if rate_limiter.is_rate_limited(key):
            remaining = rate_limiter.get_remaining_time(key)
            flash(f'Muitas tentativas. Aguarde {remaining} segundos.', 'error')
            return render_template('auth/register.html')
        
        rate_limiter.record_attempt(key)
        
        # Obter dados do formulário
        username = sanitize_input(request.form.get('username', '').strip())
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validar username
        valid, error = validate_username(username)
        if not valid:
            flash(error, 'error')
            return render_template('auth/register.html', username=username)
        
        # Validar senha
        valid, error = validate_password(password)
        if not valid:
            flash(error, 'error')
            return render_template('auth/register.html', username=username)
        
        # Confirmar senha
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/register.html', username=username)
        
        # Criar usuário
        try:
            user = User.create(username, password)
            
            # Fazer login automaticamente com regeneração de sessão para prevenir fixação
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            # Limpar rate limit após sucesso
            rate_limiter.reset(key)
            
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('dashboard.index'))
        
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('auth/register.html', username=username)
        except Exception as e:
            flash('Erro ao criar conta. Tente novamente.', 'error')
            return render_template('auth/register.html', username=username)
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página e processamento de login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        # Rate limiting
        key = get_rate_limit_key(request, 'login')
        if rate_limiter.is_rate_limited(key):
            remaining = rate_limiter.get_remaining_time(key)
            flash(f'Muitas tentativas. Aguarde {remaining} segundos.', 'error')
            return render_template('auth/login.html')
        
        rate_limiter.record_attempt(key)
        
        # Obter dados do formulário
        username = sanitize_input(request.form.get('username', '').strip())
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username e senha são obrigatórios.', 'error')
            return render_template('auth/login.html', username=username)
        
        # Buscar usuário
        user = User.find_by_username(username)
        
        if not user or not user.verify_password(password):
            flash('Username ou senha incorretos.', 'error')
            return render_template('auth/login.html', username=username)
        
        # Criar sessão com regeneração de sessão para prevenir fixação
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True
        
        # Limpar rate limit após sucesso
        rate_limiter.reset(key)
        
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Logout do usuário."""
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))
