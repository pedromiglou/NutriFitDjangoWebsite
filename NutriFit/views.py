from django.shortcuts import render,redirect
from NutriFit.forms import *
from NutriFit.models import *
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

#funcoes auxiliares
def calculateBMI(peso,altura):
    altura = altura / 100
    imc = peso / (altura * altura)
    imc = round(imc, 2)
    return imc

def calculateCI(sexo,peso,altura,idade,activity):
    bmr = 0
    if sexo == 'masculino':
        bmr = 66.4730 + (13.7516 * peso) + (5.0033 * altura) - (6.7550 * idade)
    elif sexo == 'feminino':
        bmr = 655.0955 + (9.5634 * peso) + (1.8496 * altura) - (4.6756 * idade)

    caloric_intake = 0
    if activity == 'none':
        caloric_intake = bmr * 1.2
    elif activity == 'light':
        caloric_intake = bmr * 1.375
    elif activity == 'moderate':
        caloric_intake = bmr * 1.55
    elif activity == 'heavy':
        caloric_intake = bmr * 1.725
    elif activity == 'very_heavy':
        caloric_intake = bmr * 1.9

    return caloric_intake, bmr

# Create your views here.
#enviar um user para a homepage
def base(request):
    return redirect('/home')

#renderizar homepage
def homepage(request):
    return render(request, 'homepage.html')

#renderizar pagina das calculadoras
def calculate(request):
    current_user_id = request.user.id
    if current_user_id:
        user = User.objects.get(id=current_user_id)
        user.refresh_from_db()

    if request.method == 'POST':
        if request.POST.get('calculateBMI'):
            form = CalculateBMIform(request.POST)
            if form.is_valid():
                peso = float(form.cleaned_data['peso'])
                altura = form.cleaned_data['altura']

                imc = calculateBMI(peso, altura)

                if request.user.is_authenticated:
                    save = bool(form.cleaned_data['save'])
                    if save:
                        user = User.objects.get(id=current_user_id)
                        user.refresh_from_db()
                        user.profile.altura = altura
                        user.profile.peso = peso
                        user.profile.idade = form.cleaned_data['idade']
                        user.profile.imc = round(imc,2)
                        user.profile.save()
                return render(request, 'calculateBMIresults.html', {'imc': imc})

        if request.POST.get('calculateCI'):
            form2 = CalculateBMIform(request.POST)
            if form2.is_valid():
                peso = float(form2.cleaned_data['peso'])
                altura = form2.cleaned_data['altura']
                idade = form2.cleaned_data['idade']
                sexo = request.POST.get('sexo')
                activity = request.POST.get('activity')

                caloric_intake, bmr = calculateCI(sexo, peso, altura, idade, activity)

                ci_lone = caloric_intake - 1000
                ci_lhalf = caloric_intake - 500
                ci_mone = caloric_intake + 1000
                ci_mhalf = caloric_intake + 500

                if request.user.is_authenticated:
                    save = bool(form2.cleaned_data['save'])
                    if save:
                        user = User.objects.get(id=current_user_id)
                        user.refresh_from_db()

                        if user.profile.objetivo == 'gain':
                            user.profile.ci = ci_mhalf
                        elif user.profile.objetivo == 'maintain':
                            user.profile.ci = caloric_intake
                        elif user.profile.objetivo == 'lose':
                            user.profile.ci = ci_lhalf

                        user.profile.altura = altura
                        user.profile.peso = peso
                        user.profile.idade = idade
                        user.profile.save()


                return render(request, 'calculateCIresults.html', {'bmr': int(bmr), 'caloric_intake': int(caloric_intake), 'ci_lone': int(ci_lone),
                                                                   'ci_lhalf': int(ci_lhalf), 'ci_mone': int(ci_mone), 'ci_mhalf': int(ci_mhalf)})
    else:
        if request.user.is_authenticated:
            form = CalculateBMIform(initial={'altura':user.profile.altura, 'idade': user.profile.idade, 'peso': user.profile.peso})
            form2 = CalculateCIform(initial={'altura':user.profile.altura, 'idade': user.profile.idade, 'peso': user.profile.peso})
        else:
            form = CalculateBMIform()
            form2 = CalculateCIform()
        return render(request, 'calculators.html', {'form': form, 'form2': form2})

#renderizar a pagina de registo de um user
def signIn(request):
    if request.method == 'POST':
        userform = SignIn(request.POST)
        if userform.is_valid():
            user = userform.save()
            user.refresh_from_db()
            user.profile.primeiro_nome = userform.cleaned_data.get('first_name')
            user.profile.ultimo_nome = userform.cleaned_data.get('last_name')
            user.profile.email = userform.cleaned_data.get('email')
            user.profile.altura = userform.cleaned_data.get('altura')
            user.profile.peso = userform.cleaned_data.get('peso')
            user.profile.idade = userform.cleaned_data.get('idade')
            user.profile.sexo = userform.cleaned_data.get('sexo')
            user.profile.objetivo = userform.cleaned_data.get('objetivo')
            user.profile.imc = calculateBMI(float(user.profile.peso), float(user.profile.altura))

            activity = userform.cleaned_data.get('activity')

            caloric_intake, bmr = calculateCI(user.profile.sexo, float(user.profile.peso), float(user.profile.altura),
                                         user.profile.idade, activity)

            if user.profile.objetivo == 'gain':
                user.profile.ci = caloric_intake + 500
            elif user.profile.objetivo == 'maintain':
                user.profile.ci = caloric_intake
            elif user.profile.objetivo == 'lose':
                user.profile.ci = caloric_intake - 500

            user.save()
            username = userform.cleaned_data.get('username')
            password = userform.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            messages.success(request,
                             'Account created!',
                             extra_tags='alert-success')

            return redirect('/daily')
        else:
            messages.error(request,
                           'Oops something happened!',
                           extra_tags='alert-error')
            return redirect('/signIn')

    else:
        userform = SignIn()
        return render(request, 'signin.html', {'userform': userform})


#renderizar a pagina de perfil do utillizador
@login_required(login_url='login')
def profile(request, tab):
    current_user_id = request.user.id
    user = User.objects.get(id=current_user_id)
    user.refresh_from_db()

    if request.method == 'POST':
        if tab == "obj":
            form = Profile_obj(request.POST)
            if form.is_valid():
                user.profile.altura = form.cleaned_data.get('altura')
                user.profile.peso = form.cleaned_data.get('peso')
                user.profile.idade = form.cleaned_data.get('idade')
                user.profile.objetivo = form.cleaned_data.get('objetivo')
                user.profile.imc = calculateBMI(float(user.profile.peso), float(user.profile.altura))
                user.save()
                messages.success(request,
                                 'Successfully updated!',
                                 extra_tags='alert-success')
            else:
                messages.error(request,
                               'Oops something happend!',
                               extra_tags='alert-error')
            return redirect('/profile/pro')
        elif tab == "pro":
            form = Profile_pro(request.POST)
            if form.is_valid():
                user.username = form.cleaned_data['username']
                user.profile.ultimo_nome = form.cleaned_data['last_name']
                user.profile.primeiro_nome = form.cleaned_data['first_name']
                user.save()
                messages.success(request,
                                 'Successfully updated!',
                                 extra_tags='alert-success')
            else:
                messages.error(request,
                               'Oops something happend!',
                               extra_tags='alert-error')
            return render(request, 'profile_pro.html', {'form': form})
        elif tab == "set":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                current_user = password_form.save()
                update_session_auth_hash(request, current_user)
                messages.success(request,
                                 'Your password was successfully updated!',
                                 extra_tags='alert-success')
            else:
                messages.error(request,
                                 'Oops the password was not updated!',
                                 extra_tags='alert-error')
            return redirect('/profile/pro')
    else:
        if tab == "obj":
            form = Profile_obj(initial={'objetivos': [user.profile.objetivo] , 'peso': user.profile.peso,'altura': user.profile.altura, 'idade' :user.profile.idade,
                                        'imc': user.profile.imc, 'caloric_intake': user.profile.ci})
            return render(request, 'profile_obj.html', {'form': form})
        elif tab == "pro":
            form = Profile_pro(initial={'first_name':user.profile.primeiro_nome, 'last_name':user.profile.ultimo_nome,
                                         'username':user.username, 'email': user.profile.email})

            return render(request, 'profile_pro.html', {'form': form})
        elif tab == "set":
            password_form = PasswordChangeForm(request.user, request.POST)
            return render(request, 'profile_set.html', {'form': password_form})

#renderizar a pagina com os dados diarios
@login_required(login_url='login')
def daily(request, data=None):
    '''
    Para o utilizador loggado, terá de se ir á data atual e ir buscar as refeições daquele dia e calcular
    os parâmetros lá apresentados
    Na parte das refeições apresentar o que o gajo já comeu (talvez ao carregar na foto)
    Para ver os dias anteriores, irá haver setas na parte 'daily' que irá buscar as refeições de outra data
    '''
    if request.method == 'POST':
        print("a")
    current_user_id = request.user.id
    user = User.objects.get(id=current_user_id)
    user.refresh_from_db()

    if data:
        data = data.split("-")
        data = date(int(data[0]), int(data[1]), int(data[2]))
    else:
        data = date.today()

    yesterday_date = data - timedelta(days=1)
    tomorrow_date = data + timedelta(days=1)

    if Refeicao.objects.filter(nome='breakfast', data=data, utilizador_id=current_user_id):
        meal1 = Refeicao.objects.get(nome='breakfast', data=data, utilizador_id=current_user_id)
    else:
        meal1 = Refeicao(nome='breakfast', data=data, utilizador=user)
        meal1.save()

    if Refeicao.objects.filter(nome='lunch', data=data, utilizador_id=current_user_id):
        meal2 = Refeicao.objects.get(nome='lunch', data=data, utilizador_id=current_user_id)
    else:
        meal2 = Refeicao(nome='lunch', data=data, utilizador=user)
        meal2.save()

    if Refeicao.objects.filter(nome='snack', data=data, utilizador_id=current_user_id):
        meal3 = Refeicao.objects.get(nome='snack', data=date.today(), utilizador_id=current_user_id)
    else:
        meal3 = Refeicao(nome='snack',data=data, utilizador=user)
        meal3.save()

    if Refeicao.objects.filter(nome='dinner',data=data, utilizador_id=current_user_id):
        meal4 = Refeicao.objects.get(nome='dinner', data=data, utilizador_id=current_user_id)
    else:
        meal4 = Refeicao(nome='dinner', data=data, utilizador=user)
        meal4.save()

    alimentos_breakfast = Composta.objects.filter(refeicao = meal1)

    alimentos_lunch = Composta.objects.filter(refeicao=meal2)

    alimentos_snack = Composta.objects.filter(refeicao=meal3)

    alimentos_dinner = Composta.objects.filter(refeicao=meal4)

    ci = Profile.objects.get(user = request.user).ci
    hi = 0.125*ci
    pi = 0.075*ci
    gi = 0.022*ci

    cc = 0
    hc = 0
    pc = 0
    gc = 0
    for x in alimentos_breakfast:
        cc += x.alimento.calorias * x.quantidade / 100
        hc += float(x.alimento.macro_nutrientes.hidratos_carbono) * x.quantidade / 100
        pc += float(x.alimento.macro_nutrientes.proteina) * x.quantidade / 100
        gc += float(x.alimento.macro_nutrientes.gordura) * x.quantidade / 100

    for x in alimentos_lunch:
        cc += x.alimento.calorias * x.quantidade / 100
        hc += float(x.alimento.macro_nutrientes.hidratos_carbono) * x.quantidade / 100
        pc += float(x.alimento.macro_nutrientes.proteina) * x.quantidade / 100
        gc += float(x.alimento.macro_nutrientes.gordura) * x.quantidade / 100

    for x in alimentos_snack:
        cc += x.alimento.calorias * x.quantidade / 100
        hc += float(x.alimento.macro_nutrientes.hidratos_carbono) * x.quantidade / 100
        pc += float(x.alimento.macro_nutrientes.proteina) * x.quantidade / 100
        gc += float(x.alimento.macro_nutrientes.gordura) * x.quantidade / 100

    for x in alimentos_dinner:
        cc += x.alimento.calorias * x.quantidade / 100
        hc += float(x.alimento.macro_nutrientes.hidratos_carbono) * x.quantidade / 100
        pc += float(x.alimento.macro_nutrientes.proteina) * x.quantidade / 100
        gc += float(x.alimento.macro_nutrientes.gordura) * x.quantidade / 100

    percentage_calories = cc/ci*100
    percentage_hidratos = hc / hi * 100
    percentage_proteina = pc / pi * 100
    percentage_gordura = gc / gi * 100

    percentage_calories = percentage_calories if percentage_calories < 100 else 100
    percentage_hidratos = percentage_hidratos if percentage_hidratos < 100 else 100
    percentage_proteina = percentage_proteina if percentage_proteina < 100 else 100
    percentage_gordura = percentage_gordura if percentage_gordura < 100 else 100

    cc = round(cc, 1)
    ci = round(ci, 1)
    hc = round(hc, 1)
    hi = round(hi, 1)
    pc = round(pc, 1)
    pi = round(pi, 1)
    gc = round(gc, 1)
    gi = round(gi, 1)

    return render(request, 'daily.html', {'meal1': meal1, 'meal2': meal2,
        'meal3': meal3, 'meal4': meal4, 'alimentos_breakfast': alimentos_breakfast, 'alimentos_lunch': alimentos_lunch,
        'alimentos_snack': alimentos_snack, 'alimentos_dinner': alimentos_dinner,
        'yesterday_date':str(yesterday_date.year) + "-" + str(yesterday_date.month)+"-"+str(yesterday_date.day),
        'tomorrow_date':str(tomorrow_date.year) + "-" + str(tomorrow_date.month)+"-"+str(tomorrow_date.day),
        'date': str(data.year) + "-" + str(data.month) + "-" + str(data.day),
        'percentage_calories': percentage_calories, 'calorias_consumidas':cc, 'calorias_restantes':ci-cc,
        'percentage_hidratos': percentage_hidratos, 'hidratos_consumidos':hc, 'hidratos_total':hi,
        'percentage_proteina': percentage_proteina, 'proteina_consumida':pc, 'proteina_total':pi,
        'percentage_gordura': percentage_gordura, 'gordura_consumida':gc, 'gordura_total':gi})


#renderizar a pagina onde o utilizador escolhe os alimentos
@login_required(login_url='login')
def meal(request, id):
    current_user_id = request.user.id
    user = User.objects.get(id=current_user_id)
    user.refresh_from_db()

    meal = Refeicao.objects.get(id=id)

    data = str(meal.data.year) + "-" + str(meal.data.month) + "-" + str(meal.data.day)


    if request.method == 'POST':

        form = FilterMeal(request.POST)

        if form.is_valid():
            filter_List = {'nome_alimento': "", 'categoria': [], 'protein_lower': 1000, 'protein_higher': 0,
                            'hc_lower': 1000, 'hc_higher': 0, 'fat_lower': 1000, 'fat_higher': 0}

            for key in filter_List.keys():
                if form.cleaned_data[key] is not None:
                    filter_List[key] = form.cleaned_data[key]

            alimentos = Alimento.objects.all()

            if filter_List.get('nome_alimento') != "":
                alimentos = alimentos.filter(nome__icontains=filter_List.get('nome_alimento'))
            if len(filter_List.get('categoria')) > 0:
                alimentos = alimentos.filter(categoria__nome__in=filter_List.get('categoria'))
            alimentos = alimentos.filter(macro_nutrientes__proteina__gte=filter_List.get('protein_higher')).filter(macro_nutrientes__proteina__lte=filter_List.get('protein_lower')).filter(macro_nutrientes__hidratos_carbono__gte=filter_List.get('hc_higher')).filter(macro_nutrientes__hidratos_carbono__lte=filter_List.get('hc_lower')).filter(macro_nutrientes__gordura__gte=filter_List.get('fat_higher')).filter(macro_nutrientes__gordura__lte=filter_List.get('fat_lower'))

            form = FilterMeal()
            return render(request, 'meal.html', {'alimentos': alimentos, 'meal': meal, 'form': form, 'data':data})
    else:
        form = FilterMeal()
        alimentos = Alimento.objects.all()
        return render(request, 'meal.html', {'alimentos': alimentos, 'meal': meal, 'form': form, 'data':data})

#renderizar a pagina onde o utilizador escolhe a quantidade
@login_required(login_url='login')
def validateFood(request, id_meal, id_food):
    meal = Refeicao.objects.get(id=id_meal)
    alimento = Alimento.objects.get(id=id_food)
    data = date.today()
    update=False

    if request.method == 'POST':
        form = ValidateFood(request.POST)
        if form.is_valid():
            quantidade = form.cleaned_data['quantity']

            if len(Composta.objects.filter(refeicao=meal, alimento=alimento))>0:
                c = Composta.objects.get(refeicao = meal, alimento=alimento)
                c.quantidade = quantidade
                c.save()
            else:
                c = Composta.objects.create(refeicao=meal, alimento=alimento, quantidade=quantidade)
                c.save()

            data = meal.data

            messages.success(request,
                             str(quantidade) + " of " + alimento.nome + " added/updated!",
                             extra_tags='alert-success')
        else:
            messages.error(request,
                           'Oops something happened!',
                           extra_tags='alert-error')

        return redirect('/daily/' + str(data.year) + "-" + str(data.month) + "-" + str(data.day))

    else:
        if len(Composta.objects.filter(refeicao=meal, alimento=alimento)) > 0:
            form = ValidateFood(initial={'quantity': Composta.objects.get(refeicao=meal, alimento=alimento).quantidade})
            update=True
        else:
            form = ValidateFood()

        return render(request, 'validateFood.html', {'alimento': alimento, 'meal': meal, 'data': data, 'form': form, 'update': update})

#apagar a associacao entre uma refeicao e um alimento e redirecionar para daily
@login_required(login_url='login')
def removeComposta(request, food_id, meal_id, data):
    Composta.objects.get(alimento=food_id, refeicao=meal_id).delete()
    messages.success(request,
                     "Removed successfully!",
                     extra_tags='alert-success')
    return redirect('/daily/'+data)

#renderizar a pagina de gestao dos alimentos
@login_required(login_url='login')
def food(request, food_id=''):
    if not request.user.is_staff:
        return redirect('/')

    current_user_id = request.user.id
    user = User.objects.get(id=current_user_id)
    user.refresh_from_db()

    if food_id != '':
        a = Alimento.objects.get(id=food_id)
        if a.micro_nutrientes != None:
            form2 = Add_Edit_Food(initial={'name': a.nome, 'category': a.categoria, 'calories': a.calorias,
                'carbohydrates':a.macro_nutrientes.hidratos_carbono, 'protein':a.macro_nutrientes.proteina,
                'fat': a.macro_nutrientes.gordura, 'vitamin_b7': a.micro_nutrientes.vitaminaB7,
                'vitamin_c' : a.micro_nutrientes.vitaminaC, 'vitamin_d': a.micro_nutrientes.vitaminaD,
                'vitamin_e' : a.micro_nutrientes.vitaminaE, 'vitamin_k' : a.micro_nutrientes.vitaminaK,
                'potassium' :a.micro_nutrientes.potassio, 'iron': a.micro_nutrientes.ferro,
                'calcium' : a.micro_nutrientes.calcio, 'magnesium': a.micro_nutrientes.magnesio,
                'zinc' : a.micro_nutrientes.zinco})
        else:
            form2 = Add_Edit_Food(initial={'name': a.nome, 'category': a.categoria, 'calories': a.calorias,
                'carbohydrates':a.macro_nutrientes.hidratos_carbono, 'protein':a.macro_nutrientes.proteina,
                'fat': a.macro_nutrientes.gordura})
        update = True
    else:
        form2 = Add_Edit_Food()
        update = False

    alimentos = Alimento.objects.all()

    if request.method == 'POST':

        if request.POST.get('addAlimento'):
            form = Add_Edit_Food(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']
                calories = form.cleaned_data['calories']
                category = form.cleaned_data['category']
                carbohydrates = form.cleaned_data['carbohydrates']
                protein = form.cleaned_data['protein']
                fat = form.cleaned_data['fat']
                vitamin_b7 = form.cleaned_data['vitamin_b7']
                vitamin_c = form.cleaned_data['vitamin_c']
                vitamin_d = form.cleaned_data['vitamin_d']
                vitamin_e = form.cleaned_data['vitamin_e']
                vitamin_k = form.cleaned_data['vitamin_k']
                potassium = form.cleaned_data['potassium']
                iron = form.cleaned_data['iron']
                calcium = form.cleaned_data['calcium']
                magnesium = form.cleaned_data['magnesium']
                zinc = form.cleaned_data['zinc']

                macros = Macronutrientes.objects.create(hidratos_carbono=carbohydrates, proteina=protein, gordura=fat)
                macros.save()
                micros = Micronutrientes.objects.create(vitaminaC=vitamin_c, vitaminaD=vitamin_d, vitaminaE=vitamin_e,
                                                        vitaminaB7=vitamin_b7, vitaminaK=vitamin_k, potassio=potassium,
                                                        ferro=iron, magnesio=magnesium, zinco= zinc, calcio=calcium)
                micros.save()
                a = Alimento.objects.create(nome=name, calorias=calories, categoria = Categoria.objects.get(nome=category), macro_nutrientes=macros, micro_nutrientes=micros)
                a.save()

                form = FilterMeal()

                messages.success(request,
                                 a.nome + " added!",
                                 extra_tags='alert-success')
            else:
                messages.error(request, "Error", extra_tags='alert-error')

            return render(request, 'food.html', {'alimentos': alimentos, 'form': form, 'form2': form2, 'update': update})

        elif request.POST.get('updateAlimento'):
            form = Add_Edit_Food(request.POST)

            alimento = Alimento.objects.get(id=food_id)

            if form.is_valid():
                alimento.nome = form.cleaned_data['name']
                alimento.calorias = form.cleaned_data['calories']
                alimento.categoria = Categoria.objects.get(nome=form.cleaned_data['category'])
                macro_nutrientes = alimento.macro_nutrientes
                macro_nutrientes.hidratos_carbono = form.cleaned_data['carbohydrates']
                macro_nutrientes.proteina = form.cleaned_data['protein']
                macro_nutrientes.gordura = form.cleaned_data['fat']
                macro_nutrientes.save()
                micro_nutrientes = alimento.micro_nutrientes
                micro_nutrientes.vitaminaB7 = form.cleaned_data['vitamin_b7']
                micro_nutrientes.vitaminaC = form.cleaned_data['vitamin_c']
                micro_nutrientes.vitaminaD = form.cleaned_data['vitamin_d']
                micro_nutrientes.vitaminaE = form.cleaned_data['vitamin_e']
                micro_nutrientes.vitaminaK = form.cleaned_data['vitamin_k']
                micro_nutrientes.potassio = form.cleaned_data['potassium']
                micro_nutrientes.ferro = form.cleaned_data['iron']
                micro_nutrientes.calcio = form.cleaned_data['calcium']
                micro_nutrientes.magnesio = form.cleaned_data['magnesium']
                micro_nutrientes.zinco = form.cleaned_data['zinc']
                micro_nutrientes.save()
                alimento.save()

                form = FilterMeal()

                messages.success(request,
                                 alimento.nome + " updated!",
                                 extra_tags='alert-success')
            else:
                messages.error(request, "Error", extra_tags='alert-error')
            return redirect('/food')

        elif request.POST.get("filterAlimentos"):
            form = FilterMeal(request.POST)

            if form.is_valid():
                filter_List = {'nome_alimento': "", 'categoria': [], 'protein_lower': 1000, 'protein_higher': 0,
                               'hc_lower': 1000, 'hc_higher': 0, 'fat_lower': 1000, 'fat_higher': 0}

                for key in filter_List.keys():
                    if form.cleaned_data[key] is not None:
                        filter_List[key] = form.cleaned_data[key]

                if filter_List.get('nome_alimento') != "":
                    alimentos = alimentos.filter(nome__icontains=filter_List.get('nome_alimento'))
                if len(filter_List.get('categoria')) > 0:
                    alimentos = alimentos.filter(categoria__nome__in=filter_List.get('categoria'))
                alimentos = alimentos.filter(macro_nutrientes__proteina__gte=filter_List.get('protein_higher')).filter(
                    macro_nutrientes__proteina__lte=filter_List.get('protein_lower')).filter(
                    macro_nutrientes__hidratos_carbono__gte=filter_List.get('hc_higher')).filter(
                    macro_nutrientes__hidratos_carbono__lte=filter_List.get('hc_lower')).filter(
                    macro_nutrientes__gordura__gte=filter_List.get('fat_higher')).filter(
                    macro_nutrientes__gordura__lte=filter_List.get('fat_lower'))

                return render(request, 'food.html', {'alimentos': alimentos, 'form': form, 'form2': form2, 'update': update})
    else:
        form = FilterMeal()
        alimentos = Alimento.objects.all()
        return render(request, 'food.html', {'alimentos': alimentos, 'form': form, 'form2': form2, 'update': update})

#apagar um alimento e redirecionar para food
@login_required(login_url='login')
def removeFood(request, food_id):
    if not request.user.is_staff:
        return redirect('/')

    Alimento.objects.get(id=food_id).delete()
    return redirect('/food')

#renderizar a pagina de gestao de utilizadores
@login_required(login_url='login')
def user_management(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == "POST":
        form = filterUser(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            users = User.objects.filter(username__icontains=name)
            return render(request, 'user_management.html', {'users': users, 'form': form})

    users = User.objects.all()
    form = filterUser()
    return render(request, 'user_management.html', {'users': users, 'form': form})

#promover um utilizador e redirecionar para user_management
@login_required(login_url='login')
def promoteUser(request, id):
    if not request.user.is_superuser:
        return redirect('/')

    user = User.objects.get(id=id)

    if user.is_staff:
        user.is_superuser = True
        user.save()
    else:
        user.is_staff = True
        user.save()

    return redirect('/user_management')

#demover um utilizador e redirecionar para user_management
@login_required(login_url='login')
def demoteUser(request, id):
    if not request.user.is_superuser:
        return redirect('/')

    user = User.objects.get(id=id)

    if user.is_superuser:
        user.is_superuser = False
        user.save()
    else:
        user.is_staff = False
        user.save()

    return redirect('/user_management')

#renderizar a pagina de "forget pasword" e efetuar esse pedido
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "email_message/password_reset_email.txt"
                    c = {
                    "email":user.email,
                    'domain':'127.0.0.1:8000',
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()

    return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})