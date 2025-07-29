"""
Servicio de autenticación para Neo4j
Gestiona usuarios y autenticación en la base de datos de grafos
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from neo4j import Driver
from auth.models import UserCreate, UserResponse, UserSession, SecurityEvent
from auth.security import PasswordHasher, TokenManager, SecurityConfig
import uuid
import json

class AuthService:
    """Servicio principal de autenticación"""
    
    def __init__(self, neo4j_driver: Driver, redis_client=None):
        self.driver = neo4j_driver
        self.redis_client = redis_client
        self.token_manager = TokenManager(redis_client)
        
    def create_user(self, user_data: UserCreate, created_by_admin: bool = False) -> UserResponse:
        """Crea un nuevo administrador en Neo4j"""
        
        # Validar contraseña
        from auth.security import PasswordValidator
        password_validation = PasswordValidator.validate_password(user_data.password)
        if not password_validation["valid"]:
            raise ValueError(f"Contraseña inválida: {', '.join(password_validation['errors'])}")
        
        # Hash de la contraseña
        password_hash = PasswordHasher.hash_password(user_data.password)
        
        with self.driver.session() as session:
            # Verificar si el administrador ya existe
            existing_user = session.run(
                """
                MATCH (a:Admin {username: $username})
                RETURN a
                """,
                username=user_data.username
            ).single()
            
            if existing_user:
                raise ValueError("El nombre de usuario ya existe")
            
            # Verificar si el email ya existe
            existing_email = session.run(
                """
                MATCH (a:Admin {email: $email})
                RETURN a
                """,
                email=user_data.email
            ).single()
            
            if existing_email:
                raise ValueError("El email ya está registrado")
            
            # Crear el administrador
            result = session.run(
                """
                CREATE (a:Admin {
                    username: $username,
                    email: $email,
                    password_hash: $password_hash,
                    first_name: $first_name,
                    last_name: $last_name,
                    role: $role
                })
                RETURN 
                    id(a) as id,
                    a.username as username,
                    a.email as email,
                    a.first_name as first_name,
                    a.last_name as last_name,
                    a.role as role
                """,
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role
            ).single()
            
            # Log del evento de seguridad
            self.log_security_event(SecurityEvent(
                event_type="admin_created",
                user_id=result["id"], # type: ignore
                username=result["username"], # type: ignore
                ip_address="system",
                user_agent="system",
                details={"created_by_admin": created_by_admin}
            ))
            
            return UserResponse(
                id=result["id"], # pyright: ignore[reportIndexIssue] # type: ignore
                username=result["username"], # type: ignore
                email=result["email"], # type: ignore
                first_name=result["first_name"], # type: ignore
                last_name=result["last_name"], # type: ignore
                role=result["role"] # type: ignore
            )
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[UserResponse]:
        """Autentica un administrador con username/password"""
        
        with self.driver.session() as session:
            # Buscar administrador
            result = session.run(
                """
                MATCH (a:Admin {username: $username})
                RETURN 
                    id(a) as id,
                    a.username as username,
                    a.email as email,
                    a.password_hash as password_hash,
                    a.first_name as first_name,
                    a.last_name as last_name,
                    a.role as role,
                    a.failed_login_attempts as failed_attempts
                """,
                username=username
            ).single()
            
            if not result:
                # Log intento fallido
                self.log_security_event(SecurityEvent(
                    event_type="login_failed",
                    user_id=None,
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "admin_not_found"}
                ))
                return None
            
            # Verificar contraseña
            if not PasswordHasher.verify_password(password, result["password_hash"]):
                # Incrementar contador de intentos fallidos
                session.run(
                    """
                    MATCH (a:Admin {username: $username})
                    SET a.failed_login_attempts = a.failed_login_attempts + 1
                    """,
                    username=username
                )
                
                self.log_security_event(SecurityEvent(
                    event_type="login_failed",
                    user_id=result["id"],
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "invalid_password", "attempts": result["failed_attempts"] + 1}
                ))
                return None
            
            # Login exitoso - actualizar datos
            session.run(
                """
                MATCH (a:Admin {username: $username})
                SET a.failed_login_attempts = 0
                """,
                username=username
            )
            
            # Log login exitoso
            self.log_security_event(SecurityEvent(
                event_type="login_success",
                user_id=result["id"],
                username=username,
                ip_address=ip_address,
                user_agent=user_agent
            ))
            
            return UserResponse(
                id=result["id"], # pyright: ignore[reportIndexIssue] # type: ignore
                username=result["username"], # type: ignore
                email=result["email"], # type: ignore
                first_name=result["first_name"], # type: ignore
                last_name=result["last_name"] # type: ignore
            )
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Obtiene un administrador por ID"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a:Admin)
                WHERE id(a) = $user_id
                RETURN 
                    id(a) as id,
                    a.username as username,
                    a.email as email,
                    a.first_name as first_name,
                    a.last_name as last_name
                """,
                user_id=user_id
            ).single()
            
            if result:
                return UserResponse(
                id=result["id"], # pyright: ignore[reportIndexIssue] # type: ignore
                username=result["username"], # type: ignore
                email=result["email"], # type: ignore
                first_name=result["first_name"], # type: ignore
                last_name=result["last_name"] # type: ignore
                )
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Obtiene un administrador por username"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a:Admin {username: $username})
                RETURN 
                    id(a) as id,
                    a.username as username,
                    a.email as email,
                    a.first_name as first_name,
                    a.last_name as last_name
                """,
                username=username
            ).single()
            
            if result:
                return UserResponse(
                id=result["id"], # pyright: ignore[reportIndexIssue] # type: ignore
                username=result["username"], # type: ignore
                email=result["email"], # type: ignore
                first_name=result["first_name"], # type: ignore
                last_name=result["last_name"] # type: ignore
                )
            return None
    
    def create_session(self, user_id: int, ip_address: str, user_agent: str) -> str:
        """Crea una nueva sesión de usuario"""
        session_id = str(uuid.uuid4())
        
        if self.redis_client:
            session_data = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            # Guardar sesión en Redis con TTL
            ttl = SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 2  # El doble que el access token
            self.redis_client.setex(
                f"session:{session_id}",
                ttl,
                json.dumps(session_data)
            )
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Valida una sesión existente"""
        if self.redis_client:
            session_data = self.redis_client.get(f"session:{session_id}")
            if session_data:
                return json.loads(session_data)
        return None
    
    def revoke_session(self, session_id: str):
        """Revoca una sesión"""
        if self.redis_client:
            self.redis_client.delete(f"session:{session_id}")
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña de un administrador"""
        
        # Validar nueva contraseña
        from auth.security import PasswordValidator
        password_validation = PasswordValidator.validate_password(new_password)
        if not password_validation["valid"]:
            raise ValueError(f"Nueva contraseña inválida: {', '.join(password_validation['errors'])}")
        
        with self.driver.session() as session:
            # Obtener administrador actual
            result = session.run(
                """
                MATCH (a:Admin)
                WHERE id(a) = $user_id
                RETURN a.password_hash as password_hash, a.username as username
                """,
                user_id=user_id
            ).single()
            
            if not result:
                return False
            
            # Verificar contraseña actual
            if not PasswordHasher.verify_password(current_password, result["password_hash"]):
                return False
            
            # Actualizar contraseña
            new_password_hash = PasswordHasher.hash_password(new_password)
            session.run(
                """
                MATCH (a:Admin)
                WHERE id(a) = $user_id
                SET 
                    a.password_hash = $password_hash,
                    a.last_password_change = datetime()
                """,
                user_id=user_id,
                password_hash=new_password_hash
            )
            
            # Log del evento
            self.log_security_event(SecurityEvent(
                event_type="password_changed",
                user_id=user_id,
                username=result["username"],
                ip_address="system",
                user_agent="system"
            ))
            
            return True
    
    def log_security_event(self, event: SecurityEvent):
        """Registra un evento de seguridad"""
        with self.driver.session() as session:
            session.run(
                """
                CREATE (e:SecurityEvent {
                    event_type: $event_type,
                    user_id: $user_id,
                    username: $username,
                    ip_address: $ip_address,
                    user_agent: $user_agent,
                    details: $details,
                    timestamp: datetime($timestamp)
                })
                """,
                event_type=event.event_type,
                user_id=event.user_id,
                username=event.username,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                details=json.dumps(event.details) if event.details else None,
                timestamp=event.timestamp.isoformat()
            )
    
    def get_active_sessions(self, user_id: int) -> List[UserSession]:
        """Obtiene las sesiones activas de un usuario"""
        sessions = []
        if self.redis_client:
            # Buscar todas las sesiones activas
            for key in self.redis_client.scan_iter(match="session:*"):
                session_data = self.redis_client.get(key)
                if session_data:
                    data = json.loads(session_data)
                    if data.get("user_id") == user_id:
                        session_id = key.decode().split(":")[1]
                        sessions.append(UserSession(
                            user_id=data["user_id"],
                            username=data.get("username", ""),
                            session_id=session_id,
                            created_at=datetime.fromisoformat(data["created_at"]),
                            last_activity=datetime.fromisoformat(data["last_activity"]),
                            ip_address=data["ip_address"],
                            user_agent=data["user_agent"]
                        ))
        return sessions
