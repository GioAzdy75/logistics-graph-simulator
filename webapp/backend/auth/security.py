"""
Sistema de autenticación seguro para producción
Implementa las mejores prácticas de seguridad para aplicaciones web
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import redis
import json
import config

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class SecurityConfig:
    """Configuración centralizada de seguridad"""
    
    # Claves secretas (desde config.py o variables de entorno)
    SECRET_KEY: str = config.JWT_SECRET_KEY
    REFRESH_SECRET_KEY: str = config.JWT_REFRESH_SECRET_KEY
    
    # Algoritmos JWT
    ALGORITHM: str = "HS256"
    
    # Tiempos de expiración
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Política de contraseñas
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_NUMBERS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True

class PasswordValidator:
    """Validador de políticas de contraseña"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Valida una contraseña según las políticas de seguridad"""
        errors = []
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"La contraseña debe tener al menos {SecurityConfig.MIN_PASSWORD_LENGTH} caracteres")
        
        if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")
        
        if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("La contraseña debe contener al menos una letra minúscula")
        
        if SecurityConfig.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número")
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("La contraseña debe contener al menos un carácter especial")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": len(password) + (len(set(password)) * 2)  # Score simple de fortaleza
        }

class TokenManager:
    """Gestor de tokens JWT con refresh tokens"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    def create_access_token(self, data: dict) -> str:
        """Crea un token de acceso JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
    
    def create_refresh_token(self, data: dict) -> str:
        """Crea un refresh token JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SecurityConfig.REFRESH_SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
    
    def verify_access_token(self, token: str) -> dict:
        """Verifica y decodifica un token de acceso"""
        try:
            payload = jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tipo de token inválido"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def verify_refresh_token(self, token: str) -> dict:
        """Verifica y decodifica un refresh token"""
        try:
            payload = jwt.decode(token, SecurityConfig.REFRESH_SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tipo de token inválido"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido o expirado"
            )
    
    def revoke_token(self, token: str):
        """Revoca un token (lo añade a la blacklist)"""
        if self.redis_client:
            try:
                payload = jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM])
                exp = payload.get("exp")
                if exp:
                    # Calcular TTL hasta la expiración natural del token
                    ttl = exp - int(datetime.utcnow().timestamp())
                    if ttl > 0:
                        self.redis_client.setex(f"blacklist:{token}", ttl, "revoked")
            except JWTError:
                pass
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Verifica si un token está en la blacklist"""
        if self.redis_client:
            return bool(self.redis_client.exists(f"blacklist:{token}"))
        return False

class RateLimiter:
    """Sistema de rate limiting para prevenir ataques de fuerza bruta"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    def check_rate_limit(self, identifier: str) -> Dict[str, Any]:
        """Verifica si un identificador (IP, usuario) está dentro de los límites"""
        if not self.redis_client:
            return {"allowed": True, "attempts": 0, "lockout_remaining": 0}
        
        attempts_key = f"login_attempts:{identifier}"
        lockout_key = f"lockout:{identifier}"
        
        # Verificar si está en lockout
        if self.redis_client.exists(lockout_key):
            lockout_remaining = self.redis_client.ttl(lockout_key)
            return {
                "allowed": False,
                "attempts": SecurityConfig.MAX_LOGIN_ATTEMPTS,
                "lockout_remaining": lockout_remaining
            }
        
        # Obtener intentos actuales
        attempts = int(self.redis_client.get(attempts_key) or 0)
        
        return {
            "allowed": attempts < SecurityConfig.MAX_LOGIN_ATTEMPTS,
            "attempts": attempts,
            "lockout_remaining": 0
        }
    
    def record_failed_attempt(self, identifier: str):
        """Registra un intento fallido de login"""
        if not self.redis_client:
            return
        
        attempts_key = f"login_attempts:{identifier}"
        attempts = int(self.redis_client.get(attempts_key) or 0) + 1
        
        # Incrementar contador con expiración de 1 hora
        self.redis_client.setex(attempts_key, 3600, attempts)
        
        # Si se alcanza el máximo, activar lockout
        if attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            lockout_key = f"lockout:{identifier}"
            lockout_duration = SecurityConfig.LOCKOUT_DURATION_MINUTES * 60
            self.redis_client.setex(lockout_key, lockout_duration, "locked")
    
    def clear_attempts(self, identifier: str):
        """Limpia los intentos fallidos (después de login exitoso)"""
        if not self.redis_client:
            return
        
        attempts_key = f"login_attempts:{identifier}"
        self.redis_client.delete(attempts_key)

class PasswordHasher:
    """Gestor de hash de contraseñas usando bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        """Verifica si un hash necesita ser actualizado"""
        return pwd_context.needs_update(hashed_password)

def get_client_ip(request) -> str:
    """Obtiene la IP real del cliente considerando proxies"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"
