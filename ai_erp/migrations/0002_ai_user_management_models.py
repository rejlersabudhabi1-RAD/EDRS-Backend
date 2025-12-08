# Generated migration for AI-powered Super Admin user management features

from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings


class Migration(migrations.Migration):
    
    dependencies = [
        ('authentication', '0001_initial'),
        ('ai_erp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('activity_type', models.CharField(choices=[
                    ('login', 'User Login'),
                    ('logout', 'User Logout'),
                    ('page_view', 'Page View'),
                    ('document_upload', 'Document Upload'),
                    ('document_process', 'Document Processing'),
                    ('ai_query', 'AI Query'),
                    ('system_config', 'System Configuration'),
                    ('user_management', 'User Management Action'),
                    ('security_event', 'Security Event'),
                    ('performance_issue', 'Performance Issue'),
                ], max_length=20)),
                ('description', models.TextField()),
                ('page_url', models.CharField(blank=True, max_length=500)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('session_id', models.CharField(blank=True, max_length=100)),
                ('duration_seconds', models.PositiveIntegerField(blank=True, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to='authentication.rejlersuser')),
            ],
            options={
                'db_table': 'user_activity_log',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIInsightModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('insight_type', models.CharField(choices=[
                    ('user_behavior', 'User Behavior Analysis'),
                    ('system_performance', 'System Performance Analysis'),
                    ('security_analysis', 'Security Analysis'),
                    ('resource_optimization', 'Resource Optimization'),
                    ('predictive_maintenance', 'Predictive Maintenance'),
                    ('anomaly_detection', 'Anomaly Detection'),
                ], max_length=25)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[
                    ('low', 'Low Priority'),
                    ('medium', 'Medium Priority'),
                    ('high', 'High Priority'),
                    ('critical', 'Critical Priority'),
                ], default='medium', max_length=10)),
                ('confidence_score', models.FloatField(help_text='AI confidence level (0.0-1.0)')),
                ('generated_by', models.CharField(help_text='AI model that generated this insight', max_length=100)),
                ('action_items', models.JSONField(default=list, help_text='Recommended actions')),
                ('metadata', models.JSONField(default=dict)),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_insights', to='authentication.rejlersuser')),
                ('target_users', models.ManyToManyField(blank=True, related_name='ai_insights', to='authentication.rejlersuser')),
            ],
            options={
                'db_table': 'ai_insight_model',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserSessionTracking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('device_type', models.CharField(blank=True, max_length=50)),
                ('browser', models.CharField(blank=True, max_length=100)),
                ('os', models.CharField(blank=True, max_length=100)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('current_page', models.CharField(blank=True, max_length=500)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('login_time', models.DateTimeField(auto_now_add=True)),
                ('logout_time', models.DateTimeField(blank=True, null=True)),
                ('total_duration', models.PositiveIntegerField(blank=True, help_text='Session duration in seconds', null=True)),
                ('pages_visited', models.JSONField(default=list)),
                ('actions_performed', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_tracking', to='authentication.rejlersuser')),
            ],
            options={
                'db_table': 'user_session_tracking',
                'ordering': ['-last_activity'],
            },
        ),
        migrations.CreateModel(
            name='SystemMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('metric_type', models.CharField(max_length=50)),
                ('metric_name', models.CharField(max_length=100)),
                ('metric_value', models.FloatField()),
                ('unit', models.CharField(blank=True, max_length=20)),
                ('threshold_min', models.FloatField(blank=True, null=True)),
                ('threshold_max', models.FloatField(blank=True, null=True)),
                ('is_critical', models.BooleanField(default=False)),
                ('metadata', models.JSONField(default=dict)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'system_metrics',
                'ordering': ['-recorded_at'],
            },
        ),
        
        # Add indexes for performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS user_activity_log_user_created_idx ON user_activity_log (user_id, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS user_activity_log_user_created_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS user_activity_log_type_created_idx ON user_activity_log (activity_type, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS user_activity_log_type_created_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS user_activity_log_ip_idx ON user_activity_log (ip_address);",
            reverse_sql="DROP INDEX IF EXISTS user_activity_log_ip_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_insight_type_created_idx ON ai_insight_model (insight_type, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS ai_insight_type_created_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_insight_priority_created_idx ON ai_insight_model (priority, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS ai_insight_priority_created_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS ai_insight_resolved_idx ON ai_insight_model (is_resolved);",
            reverse_sql="DROP INDEX IF EXISTS ai_insight_resolved_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS user_session_user_active_idx ON user_session_tracking (user_id, is_active);",
            reverse_sql="DROP INDEX IF EXISTS user_session_user_active_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS user_session_last_activity_idx ON user_session_tracking (last_activity DESC);",
            reverse_sql="DROP INDEX IF EXISTS user_session_last_activity_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_metrics_type_recorded_idx ON system_metrics (metric_type, recorded_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS system_metrics_type_recorded_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS system_metrics_critical_idx ON system_metrics (is_critical);",
            reverse_sql="DROP INDEX IF EXISTS system_metrics_critical_idx;"
        ),
    ]