# Generated by Django 3.1 on 2020-11-18 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('NutriFit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refeicao',
            name='utilizador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='NutriFit.utilizador'),
        ),
    ]
