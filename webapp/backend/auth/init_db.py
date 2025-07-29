"""
Script para inicializar la base de datos con el esquema de autenticación
Crea las restricciones y índices necesarios para el sistema de usuarios
"""
from neo4j import GraphDatabase
import os
import sys

def create_auth_schema(driver):
    """Crea el esquema de autenticación en Neo4j"""
    
    with driver.session() as session:
        # Crear restricciones de unicidad para Admin
        constraints = [
            "CREATE CONSTRAINT admin_username_unique IF NOT EXISTS FOR (a:Admin) REQUIRE a.username IS UNIQUE",
            "CREATE CONSTRAINT admin_email_unique IF NOT EXISTS FOR (a:Admin) REQUIRE a.email IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
                print(f"✅ Restricción creada: {constraint}")
            except Exception as e:
                print(f"⚠️  Restricción ya existe o error: {constraint} - {e}")
        

def create_admin_user(driver):
    """Crea un usuario administrador por defecto"""
    
    from security import PasswordHasher
    import config
    
    admin_password = config.ADMIN_PASSWORD
    admin_email = config.ADMIN_EMAIL
    
    password_hash = PasswordHasher.hash_password(admin_password)
    
    with driver.session() as session:
        # Verificar si ya existe un admin
        existing_admin = session.run(
            "MATCH (a:Admin) RETURN count(a) as count"
        ).single()
        
        if existing_admin["count"] > 0:
            print("⚠️  Ya existe un usuario administrador")
            return
        
        # Crear usuario admin
        result = session.run(
            """
            CREATE (a:Admin {
                username: 'admin',
                email: $email,
                password_hash: $password_hash,
                first_name: 'Administrador',
                last_name: 'del Sistema',
                role: 'admin'
            })
            RETURN a.username as username, a.email as email
            """,
            email=admin_email,
            password_hash=password_hash
        ).single()
        
        print(f"✅ Usuario administrador creado:")
        print(f"   Username: {result['username']}")
        print(f"   Email: {result['email']}")
        print(f"   Password: {admin_password}")
        print(f"   ⚠️  CAMBIA LA CONTRASEÑA DESPUÉS DEL PRIMER LOGIN")

def create_sample_users(driver):
    """Crea administradores de ejemplo para desarrollo"""
    
    from security import PasswordHasher
    
    sample_admins = [
        {
            "username": "admin1",
            "email": "admin1@logistics.com", 
            "password": "Admin123!",
            "first_name": "Admin",
            "last_name": "Uno"
        },
        {
            "username": "admin2",
            "email": "admin2@logistics.com",
            "password": "Admin123!",
            "first_name": "Admin", 
            "last_name": "Dos"
        }
    ]
    
    with driver.session() as session:
        for admin_data in sample_admins:
            # Verificar si el administrador ya existe
            existing = session.run(
                "MATCH (a:Admin {username: $username}) RETURN count(a) as count",
                username=admin_data["username"]
            ).single()
            
            if existing["count"] > 0:
                print(f"⚠️  Administrador {admin_data['username']} ya existe")
                continue
            
            password_hash = PasswordHasher.hash_password(admin_data["password"])
            
            session.run(
                """
                CREATE (a:Admin {
                    username: $username,
                    email: $email,
                    password_hash: $password_hash,
                    first_name: $first_name,
                    last_name: $last_name,
                    role: 'admin'
                })
                """,
                username=admin_data["username"],
                email=admin_data["email"],
                password_hash=password_hash,
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"]
            )
            
            print(f"✅ Administrador creado: {admin_data['username']}")

def main():
    """Función principal para inicializar la base de datos"""
    
    import config
    
    # Configuración de conexión desde config.py
    uri = config.URI
    user = config.USER
    password = config.PASSWORD
    
    print("🚀 Inicializando sistema de autenticación...")
    print(f"   Conectando a: {uri}")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verificar conexión
        with driver.session() as session:
            session.run("RETURN 1")
            print("✅ Conexión a Neo4j exitosa")
        
        # Crear esquema
        print("\n📋 Creando esquema de autenticación...")
        create_auth_schema(driver)
        
        # Crear usuario admin
        print("\n👤 Creando usuario administrador...")
        create_admin_user(driver)
        
        # Crear usuarios de ejemplo (solo en desarrollo)
        if config.ENVIRONMENT == "development":
            print("\n🧪 Creando administradores de ejemplo...")
            create_sample_users(driver)
        
        print("\n✅ Inicialización completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Cambia la contraseña del administrador")
        print("   2. Configura las variables de entorno de producción")
        print("   3. Habilita HTTPS en producción")
        print("   4. Solo administradores tienen acceso al sistema")
        
        driver.close()
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
