#!/usr/bin/env python3
"""
Rejlers EDRS - Database Migration Helper Script
Assists with migrating from old Railway cluster to new Railway cluster
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrationHelper:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path("database_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def check_railway_cli(self):
        """Check if Railway CLI is installed"""
        try:
            result = subprocess.run(['railway', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Railway CLI found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Railway CLI not found. Install it from: https://railway.app/cli")
            return False
    
    def check_database_connection(self, database_url=None):
        """Test database connection"""
        logger.info("Testing database connection...")
        
        if database_url:
            os.environ['DATABASE_URL'] = database_url
        
        try:
            # Test with Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.settings')
            import django
            django.setup()
            
            from django.db import connections
            from django.core.management.color import no_style
            
            db = connections['default']
            with db.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            logger.info("✅ Database connection successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def backup_database(self, source_url, backup_name=None):
        """Create database backup using pg_dump"""
        if not backup_name:
            backup_name = f"rejlers_edrs_backup_{self.timestamp}.sql"
        
        backup_path = self.backup_dir / backup_name
        
        logger.info(f"Creating database backup: {backup_path}")
        
        try:
            # Use pg_dump to create backup
            cmd = [
                'pg_dump', 
                source_url,
                '-f', str(backup_path),
                '--verbose',
                '--no-acl',
                '--no-owner'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✅ Backup created successfully: {backup_path}")
            return backup_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Backup failed: {e.stderr}")
            return None
    
    def restore_database(self, target_url, backup_path):
        """Restore database from backup using psql"""
        logger.info(f"Restoring database from: {backup_path}")
        
        try:
            # Use psql to restore backup
            cmd = [
                'psql',
                target_url,
                '-f', str(backup_path),
                '--quiet'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("✅ Database restored successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Restore failed: {e.stderr}")
            return False
    
    def get_database_info(self):
        """Get current database configuration info"""
        logger.info("Gathering database configuration info...")
        
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.settings')
            import django
            django.setup()
            
            from django.conf import settings
            
            db_config = settings.DATABASES['default']
            
            # Mask sensitive info
            masked_config = db_config.copy()
            if 'PASSWORD' in masked_config:
                masked_config['PASSWORD'] = '*' * 8
            
            logger.info(f"Current database config: {masked_config}")
            return db_config
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return None
    
    def run_migrations(self):
        """Run Django migrations"""
        logger.info("Running Django migrations...")
        
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.settings')
            
            # Run migrations
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
            
            logger.info("✅ Migrations completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migrations failed: {e}")
            return False
    
    def validate_data_integrity(self):
        """Basic data integrity checks"""
        logger.info("Validating data integrity...")
        
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.settings')
            import django
            django.setup()
            
            # Check core models
            from django.contrib.auth import get_user_model
            from projects.models import Project
            from services.models import Service
            from team.models import TeamMember
            
            User = get_user_model()
            
            checks = {
                'Users': User.objects.count(),
                'Projects': Project.objects.count(),
                'Services': Service.objects.count(),
                'Team Members': TeamMember.objects.count(),
            }
            
            logger.info("Data integrity check results:")
            for model, count in checks.items():
                logger.info(f"  {model}: {count} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Data integrity check failed: {e}")
            return False
    
    def create_migration_report(self, results):
        """Create migration report"""
        report_path = self.backup_dir / f"migration_report_{self.timestamp}.json"
        
        report = {
            'timestamp': self.timestamp,
            'migration_results': results,
            'django_version': self.get_django_version(),
            'database_config': self.get_database_info()
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Migration report saved: {report_path}")
        return report_path
    
    def get_django_version(self):
        """Get Django version"""
        try:
            import django
            return django.get_version()
        except:
            return "Unknown"

def main():
    """Main migration workflow"""
    print("🚀 Rejlers EDRS - Database Migration Helper")
    print("=" * 50)
    
    helper = DatabaseMigrationHelper()
    results = {}
    
    # Check prerequisites
    if not helper.check_railway_cli():
        return 1
    
    # Get current database info
    current_db = helper.get_database_info()
    results['current_db_check'] = current_db is not None
    
    # Test current connection
    results['current_connection'] = helper.check_database_connection()
    
    print("\n📋 Migration Options:")
    print("1. Create database backup")
    print("2. Test new database connection")
    print("3. Run migrations on new database")
    print("4. Validate data integrity")
    print("5. Full migration workflow")
    print("0. Exit")
    
    try:
        choice = input("\nSelect option (0-5): ").strip()
        
        if choice == "1":
            source_url = input("Enter source DATABASE_URL: ").strip()
            backup_path = helper.backup_database(source_url)
            results['backup'] = backup_path is not None
            
        elif choice == "2":
            target_url = input("Enter new DATABASE_URL: ").strip()
            results['new_connection'] = helper.check_database_connection(target_url)
            
        elif choice == "3":
            target_url = input("Enter new DATABASE_URL: ").strip()
            os.environ['DATABASE_URL'] = target_url
            results['migrations'] = helper.run_migrations()
            
        elif choice == "4":
            results['data_integrity'] = helper.validate_data_integrity()
            
        elif choice == "5":
            print("\n🔄 Starting full migration workflow...")
            
            # Step 1: Backup current database
            source_url = input("Enter OLD Railway DATABASE_URL: ").strip()
            backup_path = helper.backup_database(source_url)
            results['backup'] = backup_path is not None
            
            if backup_path:
                # Step 2: Test new database
                target_url = input("Enter NEW Railway DATABASE_URL: ").strip()
                results['new_connection'] = helper.check_database_connection(target_url)
                
                if results['new_connection']:
                    # Step 3: Restore to new database
                    os.environ['DATABASE_URL'] = target_url
                    results['restore'] = helper.restore_database(target_url, backup_path)
                    
                    if results['restore']:
                        # Step 4: Run migrations
                        results['migrations'] = helper.run_migrations()
                        
                        # Step 5: Validate data
                        results['data_integrity'] = helper.validate_data_integrity()
        
        elif choice == "0":
            print("👋 Migration helper exited.")
            return 0
        
        # Create report
        report_path = helper.create_migration_report(results)
        
        print(f"\n✅ Migration process completed!")
        print(f"📊 Report saved: {report_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Migration interrupted by user.")
        return 1
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())