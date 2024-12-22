# Generated by Django 5.1.4 on 2024-12-21 23:59

import core.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('color', models.CharField(default=core.models.get_random_color, help_text='Color of the category in hex format e.g. #FF0000', max_length=7)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='HackathonLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Where the hackathon is located (e.g. Buringlont, Ontario)', max_length=255, null=True)),
                ('venue', models.CharField(blank=True, help_text='what venue is the hackathon renting (e.g. University of Toronto)', max_length=255, null=True)),
                ('country', django_countries.fields.CountryField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=False, help_text='Enable or disable notifications')),
                ('weekly', models.BooleanField(default=False, help_text='Send weekly notifications')),
                ('monthly', models.BooleanField(default=False, help_text='Send monthly notifications')),
                ('added', models.BooleanField(default=False, help_text='Send notifications when a new hackathon is added')),
                ('local_only', models.BooleanField(default=False, help_text='Only send notifications for hackathons in your local area (as defined by radius) - Changes the behavior of all other notification settings')),
                ('only_eligible', models.BooleanField(default=True, help_text='Only send notifications for hackathons you are eligible for (based on age and education level)')),
                ('radius_type', models.CharField(choices=[('km', 'Kilometers'), ('mi', 'Miles')], default='km', help_text='Unit of radius', max_length=255)),
                ('radius', models.PositiveIntegerField(default=150, help_text='Radius in which a hackathon must be in to be considered local')),
            ],
            options={
                'verbose_name_plural': 'Notification Policies',
            },
        ),
        migrations.CreateModel(
            name='Hacker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('country', django_countries.fields.CountryField(blank=True, help_text='Country you live in', max_length=3, null=True)),
                ('city', models.CharField(blank=True, help_text='City you live in', max_length=255, null=True)),
                ('school', models.CharField(blank=True, help_text='Name of your school or university', max_length=512, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('personal_website', models.CharField(blank=True, max_length=255, null=True)),
                ('education', models.SmallIntegerField(blank=True, choices=[(0, 'Middle School'), (1, 'High School'), (2, 'University/College'), (3, 'Graduated University/College'), (4, 'Other')], help_text='Your current education level e.g. High School, University, etc.', null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('saved_categories', models.ManyToManyField(help_text='Categories the user is interested in and wants updates when new hackathons meeting this critera are created.', related_name='interested_users', to='core.category')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', core.models.Notifiable()),
            ],
        ),
        migrations.CreateModel(
            name='Hackathon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('duplication_id', models.CharField(blank=True, help_text='Duplication ID for the Hackathon', max_length=255, null=True, unique=True)),
                ('net_vote', models.BigIntegerField(default=0)),
                ('source', models.CharField(choices=[('SCR', 'Scraped'), ('USR', 'User Submitted'), ('PRT', 'Partner')], default='USR', max_length=3)),
                ('scrape_source', models.CharField(choices=[('mlh', 'MLH'), ('dev', 'Devpost'), ('eth', 'ETHGlobal'), ('hcl', 'Hack Club'), ('na', 'Not Applicable')], default='na', max_length=3)),
                ('metadata', models.JSONField(blank=True, help_text='Metadata about the source of the hackathon', null=True)),
                ('is_public', models.BooleanField(default=False, help_text='Is the hackathon visible to all users')),
                ('review_status', models.CharField(blank=True, choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending'), ('requesting_changes', 'Requesting Changes')], default='pending', help_text='Status of the review process', max_length=255)),
                ('short_name', models.CharField(blank=True, help_text='Short name for the hackathon e.g. HTV', max_length=255, null=True)),
                ('name', models.CharField(help_text='Full name of the hackathon e.g. Hack the Valley', max_length=255)),
                ('website', models.URLField()),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('application_start', models.DateTimeField(blank=True, null=True)),
                ('application_deadline', models.DateTimeField(blank=True, null=True)),
                ('reimbursements', models.BooleanField(default=False)),
                ('min_age', models.SmallIntegerField(blank=True, default=0, help_text="Minimum age to participate, set to 0 if there is no minimum age and don't set if unknown", null=True)),
                ('minimum_education_level', models.SmallIntegerField(blank=True, choices=[(0, 'Middle School'), (1, 'High School'), (2, 'University/College'), (3, 'Graduated University/College'), (4, 'Other'), (5, 'Any/All')], help_text="Minimum education level required to participate, set to Any/All if there is no minimum education level and don't set if unknown", null=True)),
                ('maximum_education_level', models.SmallIntegerField(blank=True, choices=[(0, 'Middle School'), (1, 'High School'), (2, 'University/College'), (3, 'Graduated University/College'), (4, 'Other'), (5, 'Any/All')], help_text="Maximum education level required to participate, set to Any/All if there is no maximum education level and don't set if unknown", null=True)),
                ('numerical_prize_pool', models.IntegerField(blank=True, default=0, null=True)),
                ('prize_pool_items', models.TextField(blank=True, help_text='List of items in the prize pool', null=True)),
                ('fg_image', models.ImageField(blank=True, null=True, upload_to='hackathon_images')),
                ('bg_image', models.ImageField(blank=True, null=True, upload_to='hackathon_images')),
                ('hybrid', models.CharField(choices=[('I', 'In-Person'), ('O', 'Online'), ('H', 'Hybrid')], default='I', help_text='Location of the hackathon, I for in-person, V for virtual, H for hybrid', max_length=1)),
                ('freeze_data', models.BooleanField(default=False, help_text='Set to True to not update any details using scraped data. Use if you get accurate details directly from the hackathon organizers.')),
                ('is_web3', models.BooleanField(default=False, help_text='Is the hackathon Web3 themed')),
                ('is_diversity', models.BooleanField(default=False, help_text='Is the hackathon only for underrepresented groups')),
                ('is_restricted', models.BooleanField(default=False, help_text='Is enrollment in this hackathon restricted to only some group of people (like those enrolled in one specific school or unoversity)')),
                ('is_nonenglish', models.BooleanField(default=False, help_text='Is the primary language of this hackathon not English')),
                ('custom_info', models.JSONField(blank=True, default=dict, null=True)),
                ('categories', models.ManyToManyField(related_name='hackathons', to='core.category')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hackathons', to=settings.AUTH_USER_MODEL)),
                ('curators', models.ManyToManyField(related_name='curated_hackathons', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='hackathons', to='core.hackathonlocation')),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='CuratorRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=255)),
                ('team_description', models.TextField()),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('review_status', models.CharField(blank=True, choices=[('approved', 'Approved'), ('rejected', 'Rejected'), ('pending', 'Pending'), ('requesting_changes', 'Requesting Changes')], default='pending', help_text='Status of the review process', max_length=255)),
                ('created_by', models.ManyToManyField(related_name='curation_requests', to=settings.AUTH_USER_MODEL)),
                ('hackathon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hackathon')),
            ],
        ),
        migrations.AddField(
            model_name='hacker',
            name='saved',
            field=models.ManyToManyField(help_text='Hackathons the user is interested in and wants updates about.', related_name='interested_users', to='core.hackathon'),
        ),
        migrations.AddField(
            model_name='hackathonlocation',
            name='location',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='location', to='core.location'),
        ),
        migrations.AddField(
            model_name='hacker',
            name='notification_policy',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='core.notificationpolicy'),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(db_index=True, default=False, help_text='Is the school public (Is displayed on fields)')),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='schools_added', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_upvote', models.BooleanField(default=True)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('hackathon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='core.hackathon')),
                ('hacker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='hackathon',
            constraint=models.CheckConstraint(condition=models.Q(('start_date__lte', models.F('end_date'))), name='start_date_lte_end_date'),
        ),
        migrations.AddConstraint(
            model_name='hackathon',
            constraint=models.CheckConstraint(condition=models.Q(('application_start__lt', models.F('application_deadline'))), name='application_start_lt_application_deadline'),
        ),
        migrations.AddConstraint(
            model_name='hackathon',
            constraint=models.CheckConstraint(condition=models.Q(('application_deadline__lt', models.F('start_date'))), name='application_deadline_lt_start_date'),
        ),
        migrations.AddConstraint(
            model_name='vote',
            constraint=models.UniqueConstraint(fields=('hackathon', 'hacker'), name='unique_hackathon_hacker_vote'),
        ),
    ]
