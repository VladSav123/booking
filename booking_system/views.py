from django.shortcuts import render,redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .constants import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
from random import choice
import pytz,threading
from django.utils import timezone
from django.db.models import Q

def main(request):
    return render(request, 'main.html')

def trains(request):
    return render(request, 'trains_tickets.html')

def airplanes(request):
    return render(request, 'airplanes_tickets.html')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        return render(request, 'register_page.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        return render(request, 'login_page.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            if not len(password) >= 8:
                messages.error(request, 'Пароль повинен містити 8 або більше символів')
                
                return redirect('/register/')


            if User.objects.filter(email=email).exists():
                messages.error(request, 'Користувач з такою поштою вже існує!') 
                
                return redirect('/register/')
            
            hashed_password = make_password(password)
            user = form.save(commit=False)
            user.password = hashed_password
            user.save()
            
            # Після успішної реєстрації автоматично автентифікуйте користувача і створіть сесію
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                return redirect('/')
        else:
            print("13221")
            messages.error(request, 'Користувач з такою поштою вже існує!')    
    else:
        form = RegistrationForm()
    return render(request, 'register_page.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"{email}\n{password}")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Ви успішно увійшли в систему!')
            return redirect('/')
        else:
            messages.error(request, 'Неправильна електронна пошта або пароль!')
            return redirect('/login/')  # перенаправлення на сторінку входу у разі невдалої авторизації

    return render(request, 'login_page.html')

@csrf_exempt
def subscribe(request):
    response = redirect("/")
    if request.method == 'POST':
            recipient = request.POST.get('email')
            if "@" in recipient and ".com" in recipient:
                subject = "Ваш промокод на знижку!"
                available_promocodes = Promocodes.objects.filter(available=True)
                random_promocode = choice(available_promocodes)
                print(random_promocode.promocode)
                body = f"Вітаємо!\n\nВаш промокод на знижку 35% на покупку першого білету: {random_promocode.promocode}\n\n(Промокод дійсний 48 годин)"
                if not Subscribed_users.objects.filter(email=recipient).exists():
                    subscribed_user = Subscribed_users(email=recipient)
                    subscribed_user.save()
                    
                    thread = threading.Thread(target=send_email(subject,body,recipient))
                    thread.start()
                    

                        
                    response.set_cookie('subbed', 'true', max_age=30*24*60*60)  
    return response


def get_directions(request):
    # Отримати список доступних напрямків з бази даних
    available_directions = Ticket_plane.objects.values_list('departure', flat=True).distinct()
    directions = list(available_directions)
    # Повернути список напрямків у форматі JSON
    return JsonResponse({'directions': directions})
departure_time = timezone.now()

# Встановити часовий пояс UTC
departure_time_utc = departure_time.astimezone(pytz.utc)
@csrf_exempt
def search_ticket_plane(request):
    if request.method == 'POST':
        # Отримати дані з форми
        departure = request.POST.get('departure')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure-date')
        print(f"{departure}\n{destination}\n{departure_date}")
        # Перевірити наявність місця відправлення та місця призначення
        if Ticket_plane.objects.filter(Q(destination=destination) & Q(departure=departure)).exists():
            tickets = Ticket_plane.objects.filter(Q(departure=departure) & Q(destination=destination)).values_list('available_seats', flat=True)
            
            departure_date_db = Ticket_plane.objects.filter(Q(departure=departure) & Q(destination = destination)).values_list('departure_date',flat=True)
            departure_date_db = departure_date_db.first()
            available_seats = tickets.first()
            if available_seats >= 1:
                print("date")
                print(departure_date)
                print(departure_date_db)
                if str(departure_date) == str(departure_date_db):
                    plane_name = Ticket_plane.objects.filter(Q(departure=departure) & Q(destination=destination)).values_list('plane_name', flat=True)
                    price = Ticket_plane.objects.filter(Q(departure=departure) & Q(destination=destination)).values_list('price', flat=True)
                    plane_name = plane_name.first()
                    price = price.first()
                    messages.success(request,"Ви успішно забронювали квиток! \nІнформація щодо бронювання вже відправлена на вашу пошту!")
                    
                    body = f"Дякуємо за бронювання! Квиток ви можете оплатити в нас на сайті в кошику<br><br>Відправка з : {departure}<br>Шлях до: {destination}<br>Час виліту: {departure_time}<br>Літак: {plane_name}<br> Ціна: {price}$ <br><br><br><br><br><br> **квиток**"
                    thread = threading.Thread(target=send_email("Ваш квиток!",body,request.user.email))
                    thread.start()
                    
                    return redirect("/airplanes/")
                else:
                    messages.error(request,"Нажаль, ми не знайшли потрібних вам рейсів")
                    
                    return redirect("/airplanes/")
            
            else:
                messages.error(request,"Нажаль, всі місця зайняті!")
                
                return redirect("/airplanes/")
        else:
                messages.error(request,"Нажаль, ми не знайшли потрібних вам рейсів")
                
                return redirect("/airplanes/")
    else:

       messages.error(request,"Помилка,спробуйте пізніше")
       
       return redirect("/airplanes/")
    
    
def send_email(subject,body,recipient):
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient
    html_content = f"""
    <html>
    <body>
        <h1>{subject}</h1>
        <p>{body}</p>
    </body>
    </html>
    """
    message.attach(MIMEText(html_content, 'html'))
    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, message.as_string())