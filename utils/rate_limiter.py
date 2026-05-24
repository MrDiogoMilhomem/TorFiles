"""
Rate limiter para proteção contra brute force.
Implementação em memória simples para ambiente serverless.
"""
import time
from collections import defaultdict
from config import Config


class RateLimiter:
    """
    Rate limiter baseado em janela deslizante.
    
    Limita tentativas por IP em uma janela de tempo.
    """
    
    def __init__(self):
        self.attempts = defaultdict(list)
        self.max_attempts = Config.RATE_LIMIT_ATTEMPTS
        self.window = Config.RATE_LIMIT_WINDOW
    
    def _clean_old_attempts(self, key):
        """Remove tentativas antigas fora da janela."""
        now = time.time()
        self.attempts[key] = [
            timestamp for timestamp in self.attempts[key]
            if now - timestamp < self.window
        ]
    
    def is_rate_limited(self, key):
        """
        Verifica se um identificador está limitado.
        
        Args:
            key: Identificador (geralmente IP ou IP + action)
        
        Returns:
            bool: True se limitado, False caso contrário
        """
        self._clean_old_attempts(key)
        return len(self.attempts[key]) >= self.max_attempts
    
    def record_attempt(self, key):
        """
        Registra uma tentativa.
        
        Args:
            key: Identificador
        """
        self._clean_old_attempts(key)
        self.attempts[key].append(time.time())
    
    def get_remaining_time(self, key):
        """
        Retorna tempo restante até o limite ser resetado.
        
        Args:
            key: Identificador
        
        Returns:
            int: Segundos restantes, 0 se não limitado
        """
        if not self.is_rate_limited(key):
            return 0
        
        if not self.attempts[key]:
            return 0
        
        oldest = min(self.attempts[key])
        remaining = self.window - (time.time() - oldest)
        return max(0, int(remaining))
    
    def reset(self, key):
        """
        Reseta o contador para um identificador.
        
        Args:
            key: Identificador
        """
        if key in self.attempts:
            del self.attempts[key]


# Instância global
rate_limiter = RateLimiter()


def get_rate_limit_key(request, action=None):
    """
    Gera uma chave de rate limit a partir do request.
    
    Args:
        request: Flask request object
        action: Ação opcional para distinguir diferentes endpoints
    
    Returns:
        str: Chave única para rate limiting
    """
    # Tenta obter IP real (considerando proxies/Tor)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    
    if action:
        return f"{ip}:{action}"
    print(f"IP: {ip}")
    return ip
