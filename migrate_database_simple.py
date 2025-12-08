#!/usr/bin/env python3
"""
Rejlers EDRS - Database Migration Script
Simple migration without requiring local PostgreSQL installation
"""

import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.settings')
    
    try:
        django.setup()
        print("✅ Django environment loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def check_database_connection():
    """Test current database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from django.db import connections
        from django.core.management.color import no_style
        
        db = connections['default']
        with db.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print("✅ Database connection successful!")
        
        # Get database info
        db_settings = db.settings_dict
        print(f"   Engine: {db_settings.get('ENGINE', 'Unknown')}")
        print(f"   Database: {db_settings.get('NAME', 'Unknown')}")
        print(f"   Host: {db_settings.get('HOST', 'localhost')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure your DATABASE_URL environment variable is set correctly")
        return False

def run_migrations():
    """Run Django migrations"""
    print("\n🚀 Running Django migrations...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Show current migration status
        print("\n📋 Current migration status:")
        execute_from_command_line(['manage.py', 'showmigrations'])
        
        print("\n⚡ Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        
        print("\n✅ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_superuser():
    """Create Django superuser"""
    print("\n👤 Creating Django superuser...")
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser already exists")
            existing_superusers = User.objects.filter(is_superuser=True)
            for user in existing_superusers:
                print(f"   - {user.email}")
            return True
        
        # Create new superuser interactively
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'createsuperuser'])
        
        print("✅ Superuser created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Superuser creation failed: {e}")
        return False

def check_data_integrity():
    """Basic data integrity check"""
    print("\n🔍 Checking data integrity...")
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Count records in main tables
        user_count = User.objects.count()
        
        print("📊 Database Statistics:")
        print(f"   Users: {user_count}")
        
        # Try to import and count other models
        try:
            from projects.models import Project
            project_count = Project.objects.count()
            print(f"   Projects: {project_count}")
        except:
            print("   Projects: Not available (app may not be migrated)")
        
        try:
            from services.models import Service  
            service_count = Service.objects.count()
            print(f"   Services: {service_count}")
        except:
            print("   Services: Not available (app may not be migrated)")
            
        try:
            from team.models import TeamMember
            team_count = TeamMember.objects.count()
            print(f"   Team Members: {team_count}")
        except:
            print("   Team Members: Not available (app may not be migrated)")
        
        print("✅ Data integrity check completed")
        return True
        
    except Exception as e:
        print(f"❌ Data integrity check failed: {e}")
        return False

def show_database_tables():
    """Show all database tables"""
    print("\n📋 Database Tables:")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            
            if tables:
                print("   Django System Tables:")
                for table in tables:
                    table_name = table[0]
                    if table_name.startswith('django_'):
                        print(f"   - {table_name}")
                
                print("\n   EDRS Application Tables:")
                for table in tables:
                    table_name = table[0]
                    if not table_name.startswith('django_') and not table_name.startswith('auth_'):
                        print(f"   - {table_name}")
            else:
                print("   No tables found")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not list tables: {e}")
        return False

def main():
    """Main migration workflow"""
    print("🚀 Rejlers EDRS - Database Migration Tool")
    print("=" * 50)
    
    # Setup Django
    if not setup_django():
        return 1
    
    # Test database connection
    if not check_database_connection():
        print("\n💡 To fix connection issues:")
        print("   1. Make sure DATABASE_URL is set in your environment")
        print("   2. For Railway: Get DATABASE_URL from Railway dashboard")
        print("   3. For local: Install PostgreSQL and create database")
        return 1
    
    print("\n📋 Migration Options:")
    print("1. Run database migrations")
    print("2. Create superuser") 
    print("3. Check data integrity")
    print("4. Show database tables")
    print("5. Full migration (migrations + superuser + integrity check)")
    print("0. Exit")
    
    try:
        choice = input("\nSelect option (0-5): ").strip()
        
        if choice == "1":
            success = run_migrations()
            
        elif choice == "2":
            success = create_superuser()
            
        elif choice == "3":
            success = check_data_integrity()
            
        elif choice == "4":
            success = show_database_tables()
            
        elif choice == "5":
            print("\n🔄 Starting full migration process...")
            
            # Run migrations
            if run_migrations():
                # Create superuser
                print("\n" + "="*50)
                create_user = input("Create superuser? (y/n): ").lower().strip()
                if create_user == 'y':
                    create_superuser()
                
                # Check data integrity
                print("\n" + "="*50)  
                check_data_integrity()
                
                # Show tables
                print("\n" + "="*50)
                show_database_tables()
                
                print("\n🎉 Full migration completed successfully!")
                print("\n🚀 Next steps:")
                print("   - Test Django admin: python manage.py runserver")
                print("   - Visit: http://127.0.0.1:8000/admin/")
                print("   - Connect pgAdmin4 to view database")
            else:
                print("❌ Migration failed, stopping process")
        
        elif choice == "0":
            print("👋 Migration tool exited.")
            return 0
        
        else:
            print("❌ Invalid option selected")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Migration interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())