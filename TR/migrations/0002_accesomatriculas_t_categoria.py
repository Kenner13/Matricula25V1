# Generated by Django 3.0.6 on 2025-02-04 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TR', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesomatriculas',
            name='T_Categoria',
            field=models.CharField(choices=[('quinto_superior', 'Quinto Superior'), ('regulares', 'Regulares'), ('rezagados', 'Rezagados')], default=1, max_length=20),
            preserve_default=False,
        ),
    ]
