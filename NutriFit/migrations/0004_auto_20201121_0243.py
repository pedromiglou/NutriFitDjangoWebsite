# Generated by Django 3.1 on 2020-11-21 02:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('NutriFit', '0003_auto_20201118_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('primeiro_nome', models.CharField(max_length=100)),
                ('ultimo_nome', models.CharField(max_length=100)),
                ('peso', models.DecimalField(decimal_places=2, max_digits=5)),
                ('altura', models.DecimalField(decimal_places=2, max_digits=3)),
                ('idade', models.IntegerField()),
                ('sexo', models.CharField(max_length=20)),
                ('objetivo', models.CharField(max_length=20)),
                ('imc', models.DecimalField(decimal_places=2, max_digits=4)),
                ('ci', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='refeicao',
            name='utilizador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Utilizador',
        ),
    ]
