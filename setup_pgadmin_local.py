#!/usr/bin/env python3
"""
Rejlers EDRS - pgAdmin4 Local Setup Helper
Automates local PostgreSQL database setup for development
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

class PgAdminSetupHelper:
    def __init__(self):
        self.db_name = "rejlers_edrs_local"
        self.db_user = "rejlers_dev"
        self.db_host = "localhost"
        self.db_port = "5432"
    
    def check_postgresql_installed(self):
        """Check if PostgreSQL is installed and accessible"""
        try:
            result = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ PostgreSQL not found. Please install PostgreSQL first.")
            print("   Download from: https://www.postgresql.org/download/windows/")
            print("   Or install via chocolatey: choco install postgresql")
            return False
    
    def check_pgadmin_installed(self):
        """Check if pgAdmin4 is installed"""
        pgadmin_paths = [
            r"C:\Program Files\pgAdmin 4\v*\runtime\pgAdmin4.exe",
            r"C:\Program Files (x86)\pgAdmin 4\v*\runtime\pgAdmin4.exe",
            os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\pgAdmin 4")
        ]
        
        for path_pattern in pgadmin_paths:
            import glob
            matches = glob.glob(path_pattern)
            if matches:
                print(f"✅ pgAdmin4 found at: {matches[0]}")
                return True
        
        print("⚠️  pgAdmin4 not found in standard locations.")
        print("   Download from: https://www.pgadmin.org/download/pgadmin-4-windows/")
        print("   Or install via chocolatey: choco install pgadmin4")
        return False
    
    def create_local_database(self):
        """Create local development database"""
        print(f"\n🏗️  Creating local database: {self.db_name}")
        
        # Get PostgreSQL superuser password
        postgres_password = getpass.getpass("Enter PostgreSQL 'postgres' user password: ")
        
        # Create database and user
        sql_commands = f"""
-- Create database
CREATE DATABASE {self.db_name};

-- Create user
CREATE USER {self.db_user} WITH PASSWORD 'dev_password_2025';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user};
ALTER USER {self.db_user} CREATEDB;

-- Connect to the new database
\\c {self.db_name}

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO {self.db_user};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {self.db_user};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {self.db_user};

\\q
"""
        
        # Write SQL to temporary file
        temp_sql_file = Path("temp_setup.sql")
        with open(temp_sql_file, 'w') as f:
            f.write(sql_commands)
        
        try:
            # Execute SQL commands
            env = os.environ.copy()
            env['PGPASSWORD'] = postgres_password
            
            result = subprocess.run([
                'psql', 
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', 'postgres',
                '-f', str(temp_sql_file)
            ], env=env, capture_output=True, text=True, check=True)
            
            print("✅ Local database created successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Database creation failed: {e.stderr}")
            return False
        finally:
            # Clean up temp file
            if temp_sql_file.exists():
                temp_sql_file.unlink()
    
    def test_database_connection(self):
        """Test connection to local database"""
        print(f"\n🔍 Testing database connection...")
        
        dev_password = "dev_password_2025"
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = dev_password
            
            result = subprocess.run([
                'psql', 
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', self.db_name,
                '-c', 'SELECT version();'
            ], env=env, capture_output=True, text=True, check=True)
            
            print("✅ Database connection successful!")
            print(f"   Connected to: {self.db_name} as {self.db_user}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Database connection failed: {e.stderr}")
            return False
    
    def create_env_file(self):
        """Create .env.local file with database configuration"""
        print(f"\n📝 Creating .env.local configuration...")
        
        env_content = f"""# Rejlers EDRS - Local Development Database Configuration
# Generated by pgAdmin4 setup helper

# Local PostgreSQL Database
DATABASE_URL=postgresql://{self.db_user}:dev_password_2025@{self.db_host}:{self.db_port}/{self.db_name}

# Individual Database Settings (alternative to DATABASE_URL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME={self.db_name}
DB_USER={self.db_user}
DB_PASSWORD=dev_password_2025
DB_HOST={self.db_host}
DB_PORT={self.db_port}
DB_SSL_MODE=disable
DB_CONN_MAX_AGE=600
DB_ATOMIC_REQUESTS=True
DB_AUTOCOMMIT=True

# Django Development Settings
DEBUG=True
SECRET_KEY=django-insecure-local-development-key-change-me
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# JWT Settings
JWT_SECRET_KEY=local-jwt-secret-key-2025
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# Email (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# API Configuration
API_VERSION=v1
API_TITLE=Rejlers EDRS API (Local)
API_DESCRIPTION=Local development instance of Rejlers EDRS API

# File Upload
MAX_UPLOAD_SIZE=10485760

# Logging
LOG_LEVEL=DEBUG

# OpenAI (optional for local development)
# OPENAI_API_KEY=your-openai-api-key-here
"""
        
        env_local_path = Path(".env.local")
        with open(env_local_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Configuration saved to: {env_local_path.absolute()}")
        return env_local_path
    
    def generate_pgadmin_connection_info(self):
        """Generate pgAdmin4 connection information"""
        print(f"\n📊 pgAdmin4 Connection Information:")
        print("=" * 50)
        print("🏢 Server Name: Rejlers EDRS - Local Development")
        print("📁 Server Group: Local Development")
        print("")
        print("🔌 Connection Details:")
        print(f"   Host: {self.db_host}")
        print(f"   Port: {self.db_port}")
        print(f"   Database: {self.db_name}")
        print(f"   Username: {self.db_user}")
        print(f"   Password: dev_password_2025")
        print("")
        print("🔒 SSL Settings:")
        print("   SSL Mode: Disable (local development)")
        print("")
        print("📋 Steps to add in pgAdmin4:")
        print("1. Open pgAdmin4")
        print("2. Right-click 'Servers' → 'Register' → 'Server...'")
        print("3. General tab: Enter server name and group")
        print("4. Connection tab: Enter the details above")
        print("5. SSL tab: Set SSL mode to 'Disable'")
        print("6. Click 'Save'")
        print("=" * 50)
    
    def run_django_setup(self):
        """Run Django migrations and setup"""
        print(f"\n🚀 Setting up Django with local database...")
        
        try:
            # Copy .env.local to .env for Django to use
            env_local = Path(".env.local")
            env_file = Path(".env")
            
            if env_local.exists():
                import shutil
                shutil.copy(env_local, env_file)
                print("✅ Copied .env.local to .env")
            
            # Run Django migrations
            print("Running Django migrations...")
            result = subprocess.run([
                'python', 'manage.py', 'migrate'
            ], check=True, capture_output=True, text=True)
            
            print("✅ Django migrations completed successfully!")
            
            # Offer to create superuser
            create_superuser = input("\n🔐 Create Django superuser? (y/n): ").lower().strip()
            if create_superuser == 'y':
                subprocess.run(['python', 'manage.py', 'createsuperuser'])
                print("✅ Superuser created!")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Django setup failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False

def main():
    """Main setup workflow"""
    print("🐘 Rejlers EDRS - pgAdmin4 Local Setup Helper")
    print("=" * 55)
    print("")
    
    helper = PgAdminSetupHelper()
    
    # Check prerequisites
    if not helper.check_postgresql_installed():
        return 1
    
    helper.check_pgadmin_installed()
    
    print("\n📋 Setup Options:")
    print("1. Create local development database")
    print("2. Test existing database connection") 
    print("3. Generate pgAdmin4 connection info only")
    print("4. Create .env.local file only")
    print("5. Full setup (database + Django + pgAdmin config)")
    print("0. Exit")
    
    try:
        choice = input("\nSelect option (0-5): ").strip()
        
        if choice == "1":
            success = helper.create_local_database()
            if success:
                helper.test_database_connection()
                helper.generate_pgadmin_connection_info()
        
        elif choice == "2":
            helper.test_database_connection()
        
        elif choice == "3":
            helper.generate_pgadmin_connection_info()
        
        elif choice == "4":
            helper.create_env_file()
        
        elif choice == "5":
            print("\n🚀 Starting full setup process...")
            
            # Create database
            if helper.create_local_database():
                # Test connection
                if helper.test_database_connection():
                    # Create env file
                    helper.create_env_file()
                    
                    # Setup Django
                    helper.run_django_setup()
                    
                    # Show pgAdmin info
                    helper.generate_pgadmin_connection_info()
                    
                    print("\n🎉 Full setup completed successfully!")
                    print("You can now:")
                    print("- Connect to the database via pgAdmin4")
                    print("- Run Django development server: python manage.py runserver")
                    print("- Access Django admin: http://127.0.0.1:8000/admin/")
        
        elif choice == "0":
            print("👋 Setup helper exited.")
            return 0
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())