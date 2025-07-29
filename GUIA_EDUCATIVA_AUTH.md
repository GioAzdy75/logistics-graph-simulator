# 🎓 Guía Educativa: Sistema de Autenticación Web

## 📚 **Índice de Conceptos**

1. [¿Por qué necesitamos autenticación?](#problema)
2. [Conceptos básicos de seguridad](#conceptos-basicos)
3. [JWT - JSON Web Tokens](#jwt)
4. [Rate Limiting](#rate-limiting)
5. [Hashing de contraseñas](#hashing)
6. [Gestión de sesiones](#sesiones)
7. [CORS - Cross-Origin Resource Sharing](#cors)
8. [Arquitectura del sistema](#arquitectura)
9. [Flujo completo paso a paso](#flujo)
10. [Ejercicios prácticos](#ejercicios)

---

## 🔍 **1. ¿Por qué necesitamos autenticación?** {#problema}

### **El problema sin autenticación:**
```javascript
// ❌ Sistema inseguro (como tenías antes)
app.get("/datos-importantes", () => {
  return database.getAllSecrets(); // ¡Cualquiera puede acceder!
});
```

**Problemas:**
- Cualquier persona puede acceder a datos sensibles
- No sabes quién hizo qué acción
- No puedes controlar permisos
- Ataques masivos sin límites

### **La solución con autenticación:**
```javascript
// ✅ Sistema seguro (como implementamos)
app.get("/datos-importantes", requireAuth, (req, res) => {
  const user = req.user; // Sabemos quién es
  return database.getUserData(user.id); // Solo sus datos
});
```

**Beneficios:**
- Solo usuarios válidos acceden
- Auditoría de acciones (logs)
- Permisos granulares
- Protección contra ataques

---

## 🔐 **2. Conceptos Básicos de Seguridad** {#conceptos-basicos}

### **Autenticación vs Autorización**

#### **🆔 Autenticación** - "¿Quién eres?"
```python
# Usuario dice: "Soy Juan con contraseña 123456"
# Sistema verifica: "¿Es realmente Juan?"
username = "juan"
password = "123456"
user = authenticate(username, password)  # ¿Es válido?
```

#### **🔒 Autorización** - "¿Qué puedes hacer?"
```python
# Usuario autenticado como Juan
# Sistema verifica: "¿Juan puede eliminar archivos?"
if user.role == "admin":
    delete_file()  # ✅ Permitido
else:
    raise PermissionError("❌ No autorizado")
```

### **Los 3 Pilares de la Seguridad Web:**

1. **🔐 Confidencialidad** - Solo quien debe ver, ve
2. **🛡️ Integridad** - Los datos no se modifican sin autorización  
3. **⚡ Disponibilidad** - El sistema está accesible cuando se necesita

---

## 🎫 **3. JWT - JSON Web Tokens** {#jwt}

### **¿Qué es un JWT?**
Un JWT es como un **"pase de acceso digital"** que contiene información verificable.

### **Anatomía de un JWT:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Se divide en 3 partes separadas por puntos (`.`):

#### **🏷️ Header (Cabecera):**
```json
{
  "alg": "HS256",    // Algoritmo de encriptación
  "typ": "JWT"       // Tipo de token
}
```

#### **📦 Payload (Contenido):**
```json
{
  "sub": "1234567890",           // Subject (ID del usuario)
  "name": "John Doe",            // Nombre del usuario
  "iat": 1516239022,             // Issued At (cuándo se creó)
  "exp": 1516239922              // Expiration (cuándo expira)
}
```

#### **🔏 Signature (Firma):**
```javascript
// El servidor firma con su clave secreta
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

### **¿Por qué JWT es seguro?**

#### **🔒 Verificación sin base de datos:**
```python
# El servidor puede verificar el token sin consultar la BD
def verify_jwt(token):
    try:
        # Decodifica y verifica la firma
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload  # ✅ Token válido
    except jwt.ExpiredSignatureError:
        return None  # ❌ Token expirado
    except jwt.InvalidTokenError:
        return None  # ❌ Token inválido
```

#### **⏰ Expiración automática:**
```python
# Token que expira en 30 minutos
token = jwt.encode({
    'user_id': 123,
    'exp': datetime.utcnow() + timedelta(minutes=30)
}, SECRET_KEY)
```

### **JWT vs Sesiones Tradicionales:**

| Característica | JWT | Sesiones |
|---------------|-----|----------|
| **Storage** | Cliente (localStorage) | Servidor (memoria/BD) |
| **Escalabilidad** | ✅ Excelente | ❌ Limitada |
| **Seguridad** | ✅ Buena (con HTTPS) | ✅ Excelente |
| **Revocación** | ❌ Difícil | ✅ Fácil |
| **Tamaño** | Mayor | Menor |

---

## ⏱️ **4. Rate Limiting** {#rate-limiting}

### **¿Qué es Rate Limiting?**
Es como un **"guardia de seguridad"** que controla cuántas veces puedes hacer algo en un período determinado.

### **Problema sin Rate Limiting:**
```python
# ❌ Ataque de fuerza bruta
for password in ["123456", "password", "qwerty", ...]:
    response = login("admin", password)  # Sin límites!
    if response.success:
        print("¡Contraseña encontrada!")
        break
```

### **Solución con Rate Limiting:**
```python
# ✅ Sistema protegido
attempts = redis.get(f"login_attempts:{ip_address}")
if attempts >= 5:
    raise TooManyAttempts("Espera 15 minutos")

try:
    user = authenticate(username, password)
    redis.delete(f"login_attempts:{ip_address}")  # Limpiar intentos
    return success_response
except AuthenticationError:
    redis.incr(f"login_attempts:{ip_address}")  # Contar intento fallido
    redis.expire(f"login_attempts:{ip_address}", 900)  # 15 min
    raise
```

### **Tipos de Rate Limiting:**

#### **🔢 Por IP Address:**
```python
# 5 intentos por IP cada 15 minutos
@rate_limit(key="ip", limit=5, window=900)
def login(request):
    pass
```

#### **👤 Por Usuario:**
```python
# 3 intentos por usuario cada hora
@rate_limit(key=lambda r: r.form['username'], limit=3, window=3600)
def login(request):
    pass
```

#### **📊 Por Endpoint:**
```python
# 100 requests por minuto a la API
@rate_limit(key="global", limit=100, window=60)
def api_endpoint(request):
    pass
```

### **Algoritmos de Rate Limiting:**

#### **🪣 Token Bucket:**
```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity      # Capacidad máxima
        self.tokens = capacity        # Tokens actuales
        self.refill_rate = refill_rate # Tokens por segundo
        self.last_refill = time.time()
    
    def allow_request(self):
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True  # ✅ Permitir
        return False     # ❌ Denegar
    
    def _refill(self):
        now = time.time()
        tokens_to_add = (now - self.last_refill) * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
```

#### **🪟 Sliding Window:**
```python
def sliding_window_rate_limit(user_id, limit, window):
    now = time.time()
    window_start = now - window
    
    # Contar requests en la ventana deslizante
    requests = redis.zcount(f"requests:{user_id}", window_start, now)
    
    if requests >= limit:
        return False  # ❌ Límite excedido
    
    # Agregar request actual
    redis.zadd(f"requests:{user_id}", {str(uuid.uuid4()): now})
    redis.expire(f"requests:{user_id}", window)
    return True  # ✅ Permitir
```

---

## 🔐 **5. Hashing de Contraseñas** {#hashing}

### **¿Por qué no guardar contraseñas en texto plano?**

#### **❌ Almacenamiento inseguro:**
```sql
-- Si hackearan tu BD, verían esto:
SELECT * FROM users;
| id | username | password  |
|----|----------|-----------|
| 1  | juan     | mi_secreto|
| 2  | maria    | 123456    |
```

#### **✅ Almacenamiento seguro:**
```sql
-- Con hashing, verían esto (inútil para el atacante):
SELECT * FROM users;
| id | username | password_hash                                                    |
|----|----------|------------------------------------------------------------------|
| 1  | juan     | $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/.lkYpZkpY8jU6kLFK |
| 2  | maria    | $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoYrU7jh2OL3cEPKzN2K |
```

### **¿Cómo funciona el hashing?**

#### **🔄 Proceso de registro:**
```python
# 1. Usuario envía contraseña
password = "mi_secreto_123"

# 2. Sistema genera salt aleatorio
salt = bcrypt.gensalt()  # Ej: $2b$12$LQv3c1yqBWVHxkd0LHAkCO

# 3. Sistema hashea contraseña + salt
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
# Resultado: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/.lkYpZkpY8jU6kLFK

# 4. Guarda SOLO el hash, nunca la contraseña original
user.password_hash = password_hash
```

#### **🔍 Proceso de login:**
```python
# 1. Usuario envía contraseña
password_attempt = "mi_secreto_123"

# 2. Sistema obtiene el hash guardado
stored_hash = user.password_hash

# 3. Sistema compara
if bcrypt.checkpw(password_attempt.encode('utf-8'), stored_hash):
    return "✅ Login exitoso"
else:
    return "❌ Contraseña incorrecta"
```

### **¿Por qué bcrypt es mejor que MD5 o SHA1?**

#### **⚡ MD5/SHA1 - Demasiado rápidos:**
```python
# ❌ Un atacante puede probar millones por segundo
import hashlib
password_hash = hashlib.md5("123456".encode()).hexdigest()
# Resultado en 0.000001 segundos
```

#### **🐌 bcrypt - Intencionalmente lento:**
```python
# ✅ bcrypt toma tiempo deliberadamente
import bcrypt
password_hash = bcrypt.hashpw("123456".encode(), bcrypt.gensalt(rounds=12))
# Resultado en ~0.3 segundos (configurable)
```

**Rounds en bcrypt:**
- `rounds=10` → ~0.1 segundos por hash
- `rounds=12` → ~0.3 segundos por hash  
- `rounds=15` → ~2.5 segundos por hash

**Atacante con bcrypt:**
- Sin bcrypt: 1,000,000 intentos/segundo
- Con bcrypt: 3 intentos/segundo (¡300,000x más lento!)

### **Salt - ¿Por qué es importante?**

#### **❌ Sin salt (vulnerable a rainbow tables):**
```python
# Dos usuarios con la misma contraseña tendrán el mismo hash
user1_hash = md5("123456")  # 5d41402abc4b2a76b9719d911017c592
user2_hash = md5("123456")  # 5d41402abc4b2a76b9719d911017c592
# ¡Un atacante sabe que ambos usan "123456"!
```

#### **✅ Con salt (cada hash es único):**
```python
# Misma contraseña, diferentes hashes
user1_salt = generate_random_salt()  # xK8mN9pQ
user1_hash = bcrypt("123456" + user1_salt)  # abc123...

user2_salt = generate_random_salt()  # vL2eR7wM  
user2_hash = bcrypt("123456" + user2_salt)  # def456...
# ¡Hashes totalmente diferentes!
```

---

## 🗄️ **6. Gestión de Sesiones** {#sesiones}

### **¿Qué es una sesión?**
Una sesión es como **"recordar que ya te autenticaste"** mientras navegas.

### **Problema sin sesiones:**
```javascript
// ❌ Usuario tiene que hacer login en cada página
fetch("/dashboard")   // 401 - No autenticado
fetch("/profile")     // 401 - No autenticado  
fetch("/settings")    // 401 - No autenticado
```

### **Solución con sesiones:**
```javascript
// ✅ Login una vez, navega libremente
login("user", "pass")  // Recibe token
localStorage.setItem("token", token)

// Ahora todas las requests incluyen el token automáticamente
fetch("/dashboard", {
  headers: { "Authorization": `Bearer ${token}` }
})  // ✅ 200 OK
```

### **Tipos de almacenamiento de sesiones:**

#### **🍪 Cookies (tradicional):**
```javascript
// El servidor envía cookie
response.set_cookie("session_id", "abc123", {
  httpOnly: true,      // No accesible desde JavaScript
  secure: true,        // Solo HTTPS
  sameSite: "strict"   // Protección CSRF
})

// El browser envía automáticamente en cada request
```

#### **📱 localStorage (SPA/JWT):**
```javascript
// Login exitoso
const response = await fetch("/login", {
  method: "POST",
  body: JSON.stringify({username, password})
})
const {access_token} = await response.json()

// Guardar token
localStorage.setItem("token", access_token)

// Usar en requests
fetch("/api/data", {
  headers: {
    "Authorization": `Bearer ${localStorage.getItem("token")}`
  }
})
```

#### **🧠 sessionStorage (temporal):**
```javascript
// Se borra al cerrar la pestaña
sessionStorage.setItem("token", access_token)
```

### **Estrategias de expiración:**

#### **⏰ Expiración fija:**
```python
# Token expira en exactamente 30 minutos
token = create_jwt({
    'user_id': 123,
    'exp': datetime.utcnow() + timedelta(minutes=30)
})
```

#### **🔄 Refresh tokens:**
```python
# Access token corto + Refresh token largo
tokens = {
    'access_token': create_jwt({...}, expires_in=15),      # 15 min
    'refresh_token': create_jwt({...}, expires_in=7*24*60) # 7 días
}

# Cliente renueva automáticamente
if access_token_expired():
    new_access_token = refresh(refresh_token)
```

#### **🏃 Sliding expiration:**
```python
# Cada actividad extiende la sesión
def extend_session(user_id):
    session_data = redis.get(f"session:{user_id}")
    if session_data:
        redis.expire(f"session:{user_id}", 1800)  # +30 min más
```

---

## 🌐 **7. CORS - Cross-Origin Resource Sharing** {#cors}

### **¿Qué es CORS?**
CORS es una **política de seguridad del browser** que controla qué dominios pueden acceder a tu API.

### **El problema del Same-Origin Policy:**
```javascript
// ❌ Esta request será BLOQUEADA por el browser
// Frontend en: http://localhost:3000
// Backend en:  http://localhost:8000

fetch("http://localhost:8000/api/data")
// Error: CORS policy blocked this request
```

### **¿Por qué existe esta restricción?**

#### **🚨 Ataque sin CORS:**
```html
<!-- Sitio malicioso: evil-site.com -->
<script>
// ❌ Sin CORS, esto funcionaría
fetch("https://tu-banco.com/api/transfer", {
  method: "POST",
  body: JSON.stringify({
    to: "atacante@evil.com",
    amount: 1000000
  }),
  credentials: "include" // Incluye cookies de autenticación
})
</script>
```

#### **✅ Protección con CORS:**
```javascript
// El browser verifica ANTES de enviar la request:
// "¿El servidor tu-banco.com permite requests desde evil-site.com?"
// Respuesta: NO → Request bloqueada
```

### **Cómo funciona CORS:**

#### **🤝 Preflight request:**
```http
# Browser envía OPTIONS antes de la request real
OPTIONS /api/data HTTP/1.1
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization, Content-Type

# Servidor responde con permisos
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```

#### **✅ Request real:**
```http
# Si el preflight fue exitoso, browser envía la request real
POST /api/data HTTP/1.1
Origin: http://localhost:3000
Authorization: Bearer eyJ...
```

### **Configuración CORS en tu aplicación:**

#### **❌ Configuración insegura (la que tenías antes):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ¡Cualquier dominio!
    allow_methods=["*"],           # ¡Todos los métodos!
    allow_headers=["*"],           # ¡Todas las cabeceras!
    allow_credentials=True         # ¡Con cookies!
)
# Esto permite que cualquier sitio web ataque a tus usuarios
```

#### **✅ Configuración segura (la que implementamos):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[                      # Solo dominios específicos
        "http://localhost:3000",         # Tu frontend en desarrollo
        "https://tuapp.com"              # Tu frontend en producción
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Solo métodos necesarios
    allow_headers=["Authorization", "Content-Type"], # Solo headers necesarios
    allow_credentials=True               # Permitir cookies/tokens
)
```

### **Niveles de seguridad CORS:**

#### **🔴 Muy inseguro:**
```python
allow_origins=["*"]
allow_credentials=True
# ¡Nunca hagas esto! Cualquier sitio puede hacer requests autenticados
```

#### **🟡 Inseguro para desarrollo:**
```python
allow_origins=["*"]
allow_credentials=False
# Aceptable solo para APIs públicas sin autenticación
```

#### **🟢 Seguro:**
```python
allow_origins=["https://tudominio.com"]
allow_credentials=True
# Perfecto para producción
```

---

## 🏗️ **8. Arquitectura del Sistema** {#arquitectura}

### **Patrón de separación de responsabilidades:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Base de       │
│   (React)       │    │   (FastAPI)     │    │   Datos         │
│                 │    │                 │    │   (Neo4j)       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Login UI      │◄──►│ • Auth routes   │◄──►│ • Admin nodes   │
│ • Token storage │    │ • JWT creation  │    │ • Constraints   │
│ • Auto-redirect│    │ • Rate limiting │    │ • Indexes       │
│ • Logout button │    │ • Password hash │    │ • Security logs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Flujo de datos en tu aplicación:**

#### **📂 Estructura de archivos:**
```
webapp/backend/auth/
├── models.py          # 📝 Estructuras de datos (Pydantic)
├── security.py        # 🔐 Utilidades de seguridad
├── service.py         # 💼 Lógica de negocio
├── routes.py          # 🛣️ Endpoints HTTP
└── init_db.py         # 🗄️ Inicialización BD
```

#### **🔄 Responsabilidades por archivo:**

**`models.py` - Definiciones de datos:**
```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
```

**`security.py` - Herramientas de seguridad:**
```python
class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
class TokenManager:
    def create_access_token(self, data: dict) -> str:
        return jwt.encode(data, SECRET_KEY, algorithm="HS256")
    
class RateLimiter:
    def check_rate_limit(self, key: str) -> dict:
        # Lógica de rate limiting con Redis
```

**`service.py` - Lógica de negocio:**
```python
class AuthService:
    def authenticate_user(self, username: str, password: str) -> UserResponse:
        # 1. Buscar usuario en Neo4j
        # 2. Verificar contraseña con bcrypt
        # 3. Registrar evento de seguridad
        # 4. Retornar datos del usuario
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        # 1. Validar datos
        # 2. Hash de contraseña
        # 3. Crear nodo en Neo4j
        # 4. Retornar usuario creado
```

**`routes.py` - Endpoints HTTP:**
```python
@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm):
    # 1. Rate limiting
    # 2. Autenticar usuario
    # 3. Crear tokens JWT
    # 4. Retornar respuesta
    
@auth_router.get("/me")
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    # 1. Token ya validado por el Depends
    # 2. Retornar info del usuario
```

### **Patrón Dependency Injection:**

```python
# En lugar de crear dependencias dentro de funciones...
def login():
    neo4j_conn = Neo4jConnection(...)  # ❌ Acoplamiento fuerte
    redis_client = redis.Redis(...)
    auth_service = AuthService(neo4j_conn, redis_client)
    
# Usamos inyección de dependencias
def get_auth_service():
    return AuthService(neo4j_conn, redis_client)

@app.post("/login")
def login(auth_service: AuthService = Depends(get_auth_service)):  # ✅ Flexible
    return auth_service.authenticate(...)
```

**Beneficios:**
- ✅ **Testeable** - Puedes inyectar mocks
- ✅ **Reutilizable** - Una instancia para múltiples endpoints  
- ✅ **Mantenible** - Cambios centralizados
- ✅ **Escalable** - Fácil agregar nuevas dependencias

---

## 🔄 **9. Flujo Completo Paso a Paso** {#flujo}

### **Flujo de registro (una sola vez):**

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant N as Neo4j
    participant R as Redis

    U->>F: Llena formulario registro
    F->>B: POST /auth/register {username, email, password, first_name, last_name, role}
    
    B->>R: Verificar rate limiting
    R-->>B: ✅ Permitido
    
    B->>B: Validar formato de datos
    B->>B: Hash contraseña con bcrypt
    
    B->>N: Verificar username único
    N-->>B: ✅ Disponible
    
    B->>N: CREATE (admin:Admin {...})
    N-->>B: ✅ Admin creado
    
    B->>N: LOG evento de seguridad
    B-->>F: ✅ Usuario creado
    F-->>U: "Registro exitoso, ahora puedes hacer login"
```

### **Flujo de login (cada sesión):**

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant N as Neo4j
    participant R as Redis

    U->>F: Ingresa username/password
    F->>B: POST /auth/login (username=admin&password=Admin123!Dev)
    
    B->>R: Verificar rate limiting para IP
    R-->>B: ✅ 2/5 intentos permitidos
    
    B->>N: MATCH (a:Admin {username: 'admin'})
    N-->>B: ✅ Admin encontrado + password_hash
    
    B->>B: bcrypt.checkpw(password, stored_hash)
    B->>B: ✅ Contraseña correcta
    
    B->>R: Limpiar contadores de intentos fallidos
    B->>B: Crear JWT access_token (exp: 30min)
    B->>B: Crear JWT refresh_token (exp: 7 días)
    B->>R: Crear sesión en Redis
    B->>N: LOG evento "login_success"
    
    B-->>F: {access_token, refresh_token, user: {...}}
    F->>F: localStorage.setItem("token", access_token)
    F-->>U: Redirigir a dashboard
```

### **Flujo de request protegido:**

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant N as Neo4j

    U->>F: Click "Crear Mapa"
    F->>F: token = localStorage.getItem("token")
    F->>B: POST /Mapa (Authorization: Bearer token)
    
    B->>B: Extraer token del header
    B->>B: jwt.decode(token, SECRET_KEY)
    B->>B: ✅ Token válido, no expirado
    
    B->>N: MATCH (a:Admin) WHERE id(a) = token.user_id
    N-->>B: ✅ Admin existe
    
    B->>N: Ejecutar lógica de crear mapa
    N-->>B: ✅ Mapa creado
    
    B-->>F: ✅ {status: "success", mapa_id: 123}
    F-->>U: "Mapa creado exitosamente"
```

### **Flujo de token expirado:**

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend

    U->>F: Navega después de 30+ minutos
    F->>B: GET /auth/me (Authorization: Bearer expired_token)
    
    B->>B: jwt.decode(token)
    B->>B: ❌ jwt.ExpiredSignatureError
    
    B-->>F: 401 Unauthorized
    F->>F: Detectar error 401
    F->>F: localStorage.removeItem("token")
    F->>F: window.location = "/login"
    F-->>U: Pantalla de login con mensaje "Sesión expirada"
```

### **Flujo de rate limiting:**

```mermaid
sequenceDiagram
    participant A as Atacante
    participant F as Frontend
    participant B as Backend
    participant R as Redis

    A->>F: Intento 1: username=admin&password=wrong1
    F->>B: POST /auth/login
    B->>R: INCR login_attempts:192.168.1.100
    R-->>B: 1 intento
    B-->>F: ❌ 401 Credenciales incorrectas

    A->>F: Intento 2: username=admin&password=wrong2
    F->>B: POST /auth/login  
    B->>R: INCR login_attempts:192.168.1.100
    R-->>B: 2 intentos
    B-->>F: ❌ 401 Credenciales incorrectas

    Note over A,R: ... intentos 3, 4, 5 ...

    A->>F: Intento 6: username=admin&password=wrong6
    F->>B: POST /auth/login
    B->>R: GET login_attempts:192.168.1.100
    R-->>B: 5 intentos (límite alcanzado)
    B-->>F: ❌ 429 Too Many Requests "Bloqueado por 15 minutos"
    
    Note over A,R: 15 minutos después...
    
    A->>F: Intento después del bloqueo
    F->>B: POST /auth/login
    B->>R: GET login_attempts:192.168.1.100
    R-->>B: 0 intentos (TTL expiró)
    B-->>F: ✅ Procesando login normalmente
```

---

## 🧪 **10. Ejercicios Prácticos** {#ejercicios}

### **Ejercicio 1: Decodificar un JWT**

**Token de ejemplo:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Pasos:**
1. Separa el token por puntos (`.`)
2. Decodifica la primera parte (header) desde Base64
3. Decodifica la segunda parte (payload) desde Base64
4. ¿Qué información contiene?

**Herramienta online:** https://jwt.io/

### **Ejercicio 2: Calcular seguridad de contraseñas**

**Contraseñas a evaluar:**
- `123456`
- `password123`
- `Mi_Super_Contraseña_Segura_2025!`

**Calcula para cada una:**
1. ¿Cuántos caracteres únicos posibles?
2. ¿Cuántas combinaciones totales?
3. ¿Cuánto tiempo tomaría crackear con MD5 vs bcrypt?

**Fórmulas:**
```
Combinaciones = caracteres_posibles ^ longitud
Tiempo_MD5 = combinaciones / 1_000_000_000  # 1B hashes/segundo
Tiempo_bcrypt = combinaciones / 3           # 3 hashes/segundo
```

### **Ejercicio 3: Simular rate limiting**

**Implementa tu propio rate limiter simple:**
```python
import time

class SimpleRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {user_id: [timestamp1, timestamp2, ...]}
    
    def allow_request(self, user_id):
        now = time.time()
        
        # TODO: Implementa la lógica
        # 1. Obtener requests del usuario
        # 2. Filtrar solo los que están dentro de la ventana
        # 3. Verificar si está bajo el límite
        # 4. Agregar el request actual si se permite
        # 5. Retornar True/False
        
        pass

# Prueba
limiter = SimpleRateLimiter(max_requests=3, window_seconds=60)

print(limiter.allow_request("user1"))  # True
print(limiter.allow_request("user1"))  # True  
print(limiter.allow_request("user1"))  # True
print(limiter.allow_request("user1"))  # False (límite excedido)
```

### **Ejercicio 4: Analizar configuración CORS**

**Para cada configuración, determina si es segura y por qué:**

```python
# Configuración A
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
)

# Configuración B  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://miapp.com"],
    allow_credentials=False,
    allow_methods=["GET", "POST"]
)

# Configuración C
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://miapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

### **Ejercicio 5: Debugging de autenticación**

**Tienes estos logs de error. ¿Qué está pasando?**

```
2025-07-29 10:30:15 - ERROR - jwt.ExpiredSignatureError: Signature has expired
2025-07-29 10:30:16 - INFO - User redirected to login page
2025-07-29 10:30:45 - ERROR - 429 Too Many Requests for IP 192.168.1.100
2025-07-29 10:35:10 - INFO - Successful login for user 'admin'
2025-07-29 10:35:15 - ERROR - CORS error: Origin 'https://evil-site.com' not allowed
```

**Preguntas:**
1. ¿Qué pasó a las 10:30:15?
2. ¿Por qué el error 429 a las 10:30:45?
3. ¿El login a las 10:35:10 es sospechoso?
4. ¿Qué significa el error CORS de las 10:35:15?

---

## 📚 **Recursos para Seguir Aprendiendo**

### **📖 Documentación oficial:**
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - Decodificador y explicación
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Vulnerabilidades más comunes

### **🎥 Videos recomendados:**
- "How JWT Works" - Hussein Nasser
- "Password Hashing Explained" - Computerphile  
- "CORS in 100 Seconds" - Fireship

### **🛠️ Herramientas útiles:**
- [Have I Been Pwned](https://haveibeenpwned.com/) - Verificar si contraseñas fueron hackeadas
- [Postman](https://www.postman.com/) - Testing de APIs
- [Burp Suite](https://portswigger.net/burp) - Testing de seguridad

### **📚 Libros:**
- "Web Application Security" - Andrew Hoffman
- "OAuth 2 in Action" - Justin Richer
- "The Tangled Web" - Michal Zalewski

---

## 🎯 **Resumen de Conceptos Clave**

| Concepto | ¿Qué es? | ¿Por qué es importante? |
|----------|----------|------------------------|
| **JWT** | Token autofirmado con datos del usuario | Autenticación sin estado, escalable |
| **Rate Limiting** | Límites en número de requests | Previene ataques de fuerza bruta |
| **Bcrypt** | Hash lento para contraseñas | Hace impracticable el cracking |
| **CORS** | Política del browser para cross-origin | Previene ataques desde sitios maliciosos |
| **Sessions** | Recordar autenticación entre requests | UX fluida sin re-login constante |
| **Middleware** | Código que se ejecuta en cada request | Validación y seguridad automática |

¡Ahora tienes una base sólida para entender sistemas de autenticación modernos! 🎓✨
