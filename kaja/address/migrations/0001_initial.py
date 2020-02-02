# Generated by Django 3.0.2 on 2020-02-02 19:56

import core.mixin_model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=512)),
                ('street', models.CharField(max_length=512)),
                ('zip_code', models.CharField(max_length=10)),
                ('formated_address', models.CharField(max_length=1024)),
                ('city', models.CharField(max_length=256)),
                ('region', models.CharField(max_length=32)),
                ('country', models.CharField(default='Romania', max_length=32)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.UserProfile')),
            ],
            bases=(models.Model, core.mixin_model.TimestampMixin),
        ),
    ]
