"""
Endpoints de autenticación FastAPI
Implementa las rutas de autenticación seguras
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, List
from auth.models import (
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    RefreshTokenRequest, PasswordChangeRequest, LoginAttempt
)
from auth.service import AuthService
from auth.security import TokenManager, RateLimiter, SecurityConfig, get_client_ip
from services.neo4j_connection import Neo4jConnection
import redis
import os

# Router de autenticación
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Dependencias globales
def get_auth_service():
    """Obtiene una instancia del servicio de autenticación"""
    import config
    from services.neo4j_connection import Neo4jConnection
    
    neo4j_conn = Neo4jConnection(
        uri=config.URI,
        user=config.USER,
        password=config.PASSWORD
    )
    
    try:
        redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        # Test connection
        redis_client.ping()
    except:
        redis_client = None
        print("⚠️  Redis no disponible - usando fallback sin cache")
    
    return AuthService(neo4j_conn.driver, redis_client)

def get_rate_limiter():
    """Obtiene una instancia del rate limiter"""
    import config
    
    try:
        redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=1,  # Base diferente para rate limiting
            decode_responses=True
        )
        redis_client.ping()
        return RateLimiter(redis_client)
    except:
        return RateLimiter(None)

def get_current_user(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    """Obtiene el usuario actual del token"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.split(" ")[1]
    
    # Verificar si el token está en blacklist
    if auth_service.token_manager.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verificar token
    payload = auth_service.token_manager.verify_access_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Obtener usuario
    user = auth_service.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

def require_admin(current_user: UserResponse = Depends(get_current_user)):
    """Requiere que el usuario sea administrador - Simplificado: todos son admin"""
    return current_user

# Endpoints

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    """Registra un nuevo usuario"""
    
    client_ip = get_client_ip(request)
    
    # Rate limiting para registro
    rate_check = rate_limiter.check_rate_limit(f"register:{client_ip}")
    if not rate_check["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos de registro. Intenta en {rate_check['lockout_remaining']} segundos"
        )
    
    try:
        user = auth_service.create_user(user_data)
        rate_limiter.clear_attempts(f"register:{client_ip}")
        return user
        
    except ValueError as e:
        rate_limiter.record_failed_attempt(f"register:{client_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        rate_limiter.record_failed_attempt(f"register:{client_ip}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    """Inicia sesión y devuelve tokens"""
    
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    
    # Rate limiting
    rate_check = rate_limiter.check_rate_limit(f"login:{client_ip}")
    if not rate_check["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos de login. Cuenta bloqueada por {rate_check['lockout_remaining']} segundos"
        )
    
    # Autenticar usuario
    user = auth_service.authenticate_user(
        form_data.username, 
        form_data.password, 
        client_ip, 
        user_agent
    )
    
    if not user:
        rate_limiter.record_failed_attempt(f"login:{client_ip}")
        rate_limiter.record_failed_attempt(f"login:{form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Limpiar intentos fallidos
    rate_limiter.clear_attempts(f"login:{client_ip}")
    rate_limiter.clear_attempts(f"login:{form_data.username}")
    
    # Crear tokens
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = auth_service.token_manager.create_access_token(token_data)
    refresh_token = auth_service.token_manager.create_refresh_token(token_data)
    
    # Crear sesión
    session_id = auth_service.create_session(user.id, client_ip, user_agent)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@auth_router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Renueva el access token usando el refresh token"""
    
    try:
        # Verificar refresh token
        payload = auth_service.token_manager.verify_refresh_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )
        
        # Obtener usuario
        user = auth_service.get_user_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no válido"
            )
        
        # Crear nuevo access token
        token_data = {"sub": str(user.id), "username": user.username}
        new_access_token = auth_service.token_manager.create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )

@auth_router.post("/logout")
async def logout(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Cierra sesión y revoca el token"""
    
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        auth_service.token_manager.revoke_token(token)
    
    return {"message": "Sesión cerrada exitosamente"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user

@auth_router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Cambia la contraseña del usuario actual"""
    
    try:
        success = auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        return {"message": "Contraseña cambiada exitosamente"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@auth_router.get("/check-rate-limit")
async def check_rate_limit(
    request: Request,
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> LoginAttempt:
    """Verifica el estado del rate limiting para el cliente"""
    
    client_ip = get_client_ip(request)
    rate_check = rate_limiter.check_rate_limit(f"login:{client_ip}")
    
    message = None
    if not rate_check["allowed"]:
        message = f"Cuenta bloqueada por {rate_check['lockout_remaining']} segundos"
    elif rate_check["attempts"] > 0:
        remaining = SecurityConfig.MAX_LOGIN_ATTEMPTS - rate_check["attempts"]
        message = f"Quedan {remaining} intentos antes del bloqueo"
    
    return LoginAttempt(
        allowed=rate_check["allowed"],
        attempts=rate_check["attempts"],
        lockout_remaining=rate_check["lockout_remaining"],
        message=message
    )

# Endpoints de administración

@auth_router.post("/admin/create-user", response_model=UserResponse)
async def admin_create_user(
    user_data: UserCreate,
    current_admin: UserResponse = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Crea un usuario (solo administradores)"""
    try:
        return auth_service.create_user(user_data, created_by_admin=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@auth_router.get("/admin/users", response_model=List[UserResponse])
async def admin_list_users(
    current_admin: UserResponse = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Lista todos los usuarios (solo administradores)"""
    # Implementar lista de usuarios
    # Por ahora retornamos lista vacía
    return []

@auth_router.get("/health")
async def health_check():
    """Verifica el estado del servicio de autenticación"""
    return {
        "status": "healthy",
        "service": "authentication",
        "version": "1.0.0"
    }
