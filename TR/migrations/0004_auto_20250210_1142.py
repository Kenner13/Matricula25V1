# Generated by Django 3.0.6 on 2025-02-10 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TR', '0003_auto_20250205_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programacion',
            name='C_Periodo',
            field=models.CharField(choices=[('I', 'I'), ('II', 'II')], max_length=2),
        ),
        migrations.AlterField(
            model_name='programacion',
            name='C_Turno',
            field=models.CharField(choices=[('M', 'M'), ('T', 'T'), ('N', 'N')], max_length=2),
        ),
    ]
