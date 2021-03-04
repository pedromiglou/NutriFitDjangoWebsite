# Generated by Django 3.1 on 2020-11-18 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alimento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=30)),
                ('calorias', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Composta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.IntegerField()),
                ('alimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NutriFit.alimento')),
            ],
        ),
        migrations.CreateModel(
            name='Macronutrientes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidratos_carbono', models.DecimalField(decimal_places=1, default='', max_digits=4)),
                ('proteina', models.DecimalField(decimal_places=1, default='', max_digits=4)),
                ('gordura', models.DecimalField(decimal_places=1, default='', max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Micronutrientes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vitaminaB7', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('vitaminaC', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('vitaminaD', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('vitaminaE', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('vitaminaK', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('potassio', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('ferro', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('calcio', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('magnesio', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
                ('zinco', models.DecimalField(blank=True, decimal_places=1, default='', max_digits=4, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Utilizador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('username', models.CharField(max_length=20)),
                ('primeiro_nome', models.CharField(max_length=100)),
                ('ultimo_nome', models.CharField(max_length=100)),
                ('peso', models.DecimalField(decimal_places=2, max_digits=5)),
                ('altura', models.DecimalField(decimal_places=2, max_digits=3)),
                ('idade', models.IntegerField()),
                ('sexo', models.CharField(max_length=20)),
                ('objetivo', models.CharField(max_length=20)),
                ('imc', models.DecimalField(decimal_places=2, max_digits=4)),
                ('ci', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Refeicao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=30)),
                ('data', models.DateField()),
                ('alimentos', models.ManyToManyField(through='NutriFit.Composta', to='NutriFit.Alimento')),
                ('utilizador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NutriFit.utilizador')),
            ],
        ),
        migrations.AddField(
            model_name='composta',
            name='refeicao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='NutriFit.refeicao'),
        ),
        migrations.AddField(
            model_name='alimento',
            name='categoria',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='NutriFit.categoria'),
        ),
        migrations.AddField(
            model_name='alimento',
            name='macro_nutrientes',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='NutriFit.macronutrientes'),
        ),
        migrations.AddField(
            model_name='alimento',
            name='micro_nutrientes',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='NutriFit.micronutrientes'),
        ),
    ]
