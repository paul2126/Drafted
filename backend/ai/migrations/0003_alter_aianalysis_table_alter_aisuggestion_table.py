# Generated by Django 5.2.4 on 2025-07-03 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='aianalysis',
            table='ai_analysis',
        ),
        migrations.AlterModelTable(
            name='aisuggestion',
            table='ai_suggestion',
        ),
    ]
