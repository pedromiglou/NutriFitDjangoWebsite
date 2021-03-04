from .models import Macronutrientes,Micronutrientes,Alimento,Refeicao,Profile,Composta, Categoria
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#edidar dados da conta no profile
class Profile_pro(forms.Form):
    first_name = forms.CharField(max_length=100, help_text='First Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'readonly': True}))
    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'readonly': True}))

#editar caracteristicas do utilizador no profile
class Profile_obj(forms.Form):
    objetivos = [('gain', 'gain'), ('maintain', 'maintain'),
                 ('lose', 'lose')]

    objetivo = forms.ChoiceField(label="Objective", choices=objetivos)
    peso = forms.DecimalField(label="Weight(kg)", max_digits=5, decimal_places=2)
    altura = forms.IntegerField(label="Height(cm)")
    idade = forms.IntegerField(label="Age")
    imc = forms.DecimalField(label="BMI", max_digits=5, decimal_places=2, widget=forms.TextInput(attrs={'readonly': True}))
    caloric_intake = forms.IntegerField(label="Caloric Intake", widget=forms.TextInput(attrs={'readonly': True}))

#criar conta
class SignIn(UserCreationForm):
    first_name = forms.CharField(max_length=100, help_text='First Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=200)

    objetivos = [('gain', 'gain'), ('maintain', 'maintain'),
                 ('lose', 'lose')]

    peso = forms.DecimalField(label="Weight(kg)", max_digits=5, decimal_places=2)
    altura = forms.IntegerField(label="Height(cm)")
    idade = forms.IntegerField(label="Age")
    sexo = forms.ChoiceField(label="Sex", choices=(('masculino', 'Male'), ('feminino', 'Female')))
    objetivo = forms.ChoiceField(label="Objective", choices=objetivos)
    activity = forms.ChoiceField(
        choices=(('none', 'Little to no exercise'), ('light', 'Light exercise (1–3 days per week)'),
                 ('moderate', 'Moderate exercise (3–5 days per week)'), ('heavy', 'Heavy exercise (6–7 days per week)'),
                 ('very_heavy', 'Very heavy exercise (twice per day, extra heavy workouts)')))


    class Meta:
        model = User

        fields = ["email", "username", "first_name", "last_name",  "password1", "password2", "altura","peso", "idade", "sexo", "objetivo", "activity"]


#calcular BMI
class CalculateBMIform(forms.Form):
    peso = forms.DecimalField(label='Weight(kg):', max_digits=5)
    altura = forms.IntegerField(label='Height(cm):')
    idade = forms.IntegerField(label='Age:')
    save = forms.BooleanField(label='save', required=False)

#calcular CI
class CalculateCIform(forms.Form):
    peso = forms.DecimalField(label='Weight(kg):', max_digits=5)
    altura = forms.IntegerField(label='Height(cm)')
    idade = forms.IntegerField(label='Age:')
    sexo = forms.ChoiceField(label='Sex', choices=(('masculino', 'Male'), ('feminino', 'Female')))
    activity = forms.ChoiceField(choices=(('none', 'Little to no exercise'), ('light', 'Light exercise (1–3 days per week)'),
                                             ('moderate', 'Moderate exercise (3–5 days per week)'), ('heavy', 'Heavy exercise (6–7 days per week)'),
                                             ('very_heavy', 'Very heavy exercise (twice per day, extra heavy workouts)')))
    save = forms.BooleanField(label='save', required=False)

#filtrar alimentos
class FilterMeal(forms.Form):
    all_categorias = Categoria.objects.all()
    categorias = []
    for categoria in all_categorias:
        categorias.append((categoria.nome, categoria.nome))

    nome_alimento = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Search'}), required=False)
    categoria = forms.MultipleChoiceField(label='Category', choices=categorias, required=False)
    protein_higher = forms.IntegerField(label='Protein', widget=forms.TextInput(attrs={'placeholder': 'Higher'}), required=False)
    protein_lower = forms.IntegerField(label='', widget=forms.TextInput(attrs={'placeholder': 'Lower'}), required=False)
    hc_higher = forms.IntegerField(label='Carbohydrates', widget=forms.TextInput(attrs={'placeholder': 'Higher'}), required=False)
    hc_lower = forms.IntegerField(label='', widget=forms.TextInput(attrs={'placeholder': 'Lower'}), required=False)
    fat_higher = forms.IntegerField(label='Fat', widget=forms.TextInput(attrs={'placeholder': 'Higher'}), required=False)
    fat_lower = forms.IntegerField(label='', widget=forms.TextInput(attrs={'placeholder': 'Lower'}), required=False)

#selecionar a quantidade de um alimento
class ValidateFood(forms.Form):
    quantity = forms.IntegerField(label='Quantity(g):')

#adicionar/editar os dados de um alimento
class Add_Edit_Food(forms.Form):
    all_categorias = Categoria.objects.all()
    categorias = []
    for categoria in all_categorias:
        categorias.append((categoria.nome, categoria.nome))

    name = forms.CharField(max_length=30)
    calories = forms.IntegerField()
    category = forms.ChoiceField(choices=categorias)
    carbohydrates = forms.DecimalField(max_digits=4, decimal_places=1)
    protein = forms.DecimalField(max_digits=4, decimal_places=1)
    fat = forms.DecimalField(max_digits=4, decimal_places=1)
    vitamin_b7 = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    vitamin_c = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    vitamin_d = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    vitamin_e = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    vitamin_k = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    potassium = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    iron = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    calcium = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    magnesium = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    zinc = forms.DecimalField(max_digits=4, decimal_places=1, required=False)

#filtrar o utilizador por nome
class filterUser(forms.Form):
    name = forms.CharField(max_length=30)
