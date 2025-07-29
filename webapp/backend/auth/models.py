"""
Modelos Pydantic para autenticación
Define las estructuras de datos para el sistema de auth
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

class UserCreate(BaseModel):
    """Modelo para crear un nuevo administrador"""
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos')
        if len(v) < 3:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('El nombre de usuario no puede tener más de 50 caracteres')
        return v.lower()

class UserLogin(BaseModel):
    """Modelo para login de administrador"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Modelo de respuesta de administrador (sin contraseña)"""
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Respuesta de autenticación con tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Solicitud de refresh token"""
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    """Solicitud de cambio de contraseña"""
    current_password: str
    new_password: str
    
class PasswordResetRequest(BaseModel):
    """Solicitud de reset de contraseña"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Confirmación de reset de contraseña"""
    token: str
    new_password: str

class LoginAttempt(BaseModel):
    """Información de intento de login"""
    allowed: bool
    attempts: int
    lockout_remaining: int
    message: Optional[str] = None

class UserUpdate(BaseModel):
    """Modelo para actualizar datos de administrador"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserSession(BaseModel):
    """Información de sesión de administrador"""
    user_id: int
    username: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str

class SecurityEvent(BaseModel):
    """Evento de seguridad para logging"""
    event_type: str  # login_success, login_failed, password_changed, etc.
    user_id: Optional[int]
    username: Optional[str]
    ip_address: str
    user_agent: str
    details: Optional[dict] = None
    timestamp: datetime = datetime.utcnow()
