"""
Setup AI ERP System with default roles and Super Admin user
This command initializes the AI ERP system for Oil & Gas engineering
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
import logging

from authentication.models import RejlersUser
from ai_erp.models import ERPRole, UserERPProfile, AISystemLog
from ai_erp.rbac import create_default_roles
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Setup AI ERP System with default roles and create Super Admin user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            help='Email for Super Admin user',
            default='admin@rejlers.com'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            help='Password for Super Admin user',
            default='SuperAdmin@2024'
        )
        parser.add_argument(
            '--admin-name',
            type=str,
            help='Full name for Super Admin user',
            default='Super Administrator'
        )
        parser.add_argument(
            '--skip-user-creation',
            action='store_true',
            help='Skip Super Admin user creation, only create roles'
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write(
                    self.style.SUCCESS('🚀 Setting up AI-Powered ERP System for Oil & Gas Engineering...')
                )
                
                # Step 1: Create default roles
                self.stdout.write('📋 Creating default ERP roles...')
                roles_created = create_default_roles()
                
                if roles_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created {len(roles_created)} ERP roles')
                    )
                    for role in roles_created:
                        self.stdout.write(f'   - {role.name} ({role.code})')
                else:
                    self.stdout.write('ℹ️  ERP roles already exist')
                
                # Step 2: Create Super Admin user (if requested)
                if not options['skip_user_creation']:
                    admin_email = options['admin_email']
                    admin_password = options['admin_password']
                    admin_name = options['admin_name']
                    
                    self.stdout.write(f'👑 Creating Super Admin user: {admin_email}...')
                    
                    # Check if user already exists
                    if RejlersUser.objects.filter(email=admin_email).exists():
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  User with email {admin_email} already exists')
                        )
                        user = RejlersUser.objects.get(email=admin_email)
                    else:
                        # Create new user
                        name_parts = admin_name.split(' ', 1)
                        first_name = name_parts[0] if name_parts else 'Super'
                        last_name = name_parts[1] if len(name_parts) > 1 else 'Administrator'
                        
                        user = RejlersUser.objects.create_user(
                            email=admin_email,
                            username=admin_email.split('@')[0],
                            password=admin_password,
                            first_name=first_name,
                            last_name=last_name,
                            is_active=True,
                            is_staff=True,
                            is_superuser=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Created Super Admin user: {admin_email}')
                        )
                    
                    # Step 3: Create ERP profile for Super Admin
                    super_admin_role = ERPRole.objects.get(code='SUPER_ADMIN')
                    
                    erp_profile, created = UserERPProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'role': super_admin_role,
                            'experience_level': 'expert',
                            'primary_domain': 'upstream',
                            'specializations': ['system_administration', 'ai_management', 'project_oversight']
                        }
                    )
                    
                    if created:
                        self.stdout.write('✅ Created Super Admin ERP profile')
                    else:
                        # Update existing profile to Super Admin role
                        erp_profile.role = super_admin_role
                        erp_profile.save()
                        self.stdout.write('✅ Updated user to Super Admin role')
                    
                # Log the setup
                try:
                    AISystemLog.objects.create(
                        user=user,
                        log_type='system_setup',
                        ai_model_used='system',
                        processing_time=0,
                        input_data={
                            'action': 'initial_setup',
                            'roles_created': len(roles_created) if roles_created else 0,
                            'super_admin_created': created
                        },
                        ip_address='127.0.0.1',  # Default setup IP
                        session_id='system_setup',
                        success=True
                    )
                except Exception as log_error:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Could not create setup log: {log_error}')
                    )                # Step 4: Display setup summary
                self.display_setup_summary(options)
                
        except Exception as e:
            logger.error(f"ERP setup failed: {str(e)}")
            raise CommandError(f'Setup failed: {str(e)}')

    def display_setup_summary(self, options):
        """Display setup summary and next steps"""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('🎉 AI-Powered ERP System Setup Complete!')
        )
        self.stdout.write('='*60)
        
        # Display roles
        self.stdout.write('\n📊 Available Roles:')
        roles = ERPRole.objects.all()
        for role in roles:
            user_count = UserERPProfile.objects.filter(role=role).count()
            self.stdout.write(f'   {role.name} ({role.code}) - {user_count} users')
        
        # Display Super Admin info
        if not options['skip_user_creation']:
            self.stdout.write('\n👑 Super Admin Access:')
            self.stdout.write(f'   Email: {options["admin_email"]}')
            self.stdout.write(f'   Password: {options["admin_password"]}')
            self.stdout.write('   Dashboard: /ai-erp/admin-dashboard/')
        
        # Display system features
        self.stdout.write('\n🔧 System Features:')
        self.stdout.write('   • Role-Based Access Control (RBAC)')
        self.stdout.write('   • AI-Powered Drawing Analysis')
        self.stdout.write('   • Engineering Simulation Management')
        self.stdout.write('   • OpenAI GPT-4o-mini Integration')
        self.stdout.write('   • Computer Vision for Technical Drawings')
        self.stdout.write('   • Domain-Specific AI Assistance')
        
        # Display next steps
        self.stdout.write('\n🚀 Next Steps:')
        self.stdout.write('   1. Run migrations: python manage.py migrate')
        self.stdout.write('   2. Start development server: python manage.py runserver')
        self.stdout.write('   3. Login as Super Admin and access dashboard')
        self.stdout.write('   4. Create additional users and assign roles')
        self.stdout.write('   5. Upload technical drawings for AI analysis')
        
        # Display API endpoints
        self.stdout.write('\n🌐 Key Endpoints:')
        self.stdout.write('   • Main Dashboard: /ai-erp/')
        self.stdout.write('   • Admin Dashboard: /ai-erp/admin-dashboard/')
        self.stdout.write('   • Drawing Analysis: /drawing-analysis/')
        self.stdout.write('   • Simulation Management: /simulation-management/')
        self.stdout.write('   • API Root: /api/v1/')
        
        self.stdout.write('\n✨ System is ready for Oil & Gas engineering tasks!')
        self.stdout.write('='*60)