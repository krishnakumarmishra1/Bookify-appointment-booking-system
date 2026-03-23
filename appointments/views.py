from django.shortcuts import render, redirect, get_object_or_404
from .models import Service, TimeSlot, Appointment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime


def service_list(request):

    # 🔥 SERVICES AUTO INSERT (ONLY FIRST TIME)
    if not Service.objects.exists():
        services_data = [
            ("General Checkup", "doctor", "Doctor", "Basic health consultation", 30, 500),
            ("Haircut", "salon", "Salon", "Stylish haircut", 30, 120),
            ("Hair Spa", "salon", "Salon", "Hair spa treatment", 45, 600),
            ("Beard Trim", "salon", "Salon", "Beard grooming", 20, 80),
            ("Career Guidance", "consult", "Consultancy", "Career advice", 60, 500),
            ("Business Consulting", "consult", "Consultancy", "Business advice", 60, 1500),
            ("Legal Advice", "consult", "Consultancy", "Legal consultation", 45, 800),
            ("Fitness Coaching", "consult", "Consultancy", "Fitness guidance", 45, 500),
        ]

        for name, category, sub, desc, dur, price in services_data:
            Service.objects.create(
                name=name,
                category=category,
                sub_category=sub,
                description=desc,
                duration=dur,
                price=price
            )

    # 🔥 TIMESLOTS FIX (10 AM → 8 PM, 30 mins gap)
    if not TimeSlot.objects.exists():
        from datetime import time

        start_hour = 10
        end_hour = 20  # 8 PM

        for hour in range(start_hour, end_hour):
            # 00 → 30
            TimeSlot.objects.create(
                start_time=time(hour, 0),
                end_time=time(hour, 30)
            )

            # 30 → next hour 00
            TimeSlot.objects.create(
                start_time=time(hour, 30),
                end_time=time(hour + 1, 0)
            )

    # 🔥 CATEGORY FILTER FIX
    category = request.GET.get('category')

    if category:
        services = Service.objects.filter(category=category)
    else:
        services = Service.objects.all()

    return render(request, 'appointments/service_list.html', {
        'services': services
    })

# 🔥 BOOK APPOINTMENT (FIXED FULL LOGIC)
def book_appointment(request, service_id):

    if not request.user.is_authenticated:
        return redirect('/login/')

    service = get_object_or_404(Service, id=service_id)
    time_slots = TimeSlot.objects.all()

    selected_date = request.GET.get('date')
    booked_slots = []
    disabled_slots = []

    now = timezone.localtime()

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # booked slots
        booked_slots = Appointment.objects.filter(
            date=selected_date_obj,
            service=service
        ).values_list('time_slot_id', flat=True)

        # past time disable
        if selected_date_obj == now.date():
            for slot in time_slots:
                slot_time = datetime.combine(now.date(), slot.start_time)
                slot_time = timezone.make_aware(slot_time)

                if slot_time < now:
                    disabled_slots.append(slot.id)

    # 🔥 POST FIX (booking issue fix)
    if request.method == 'POST':

        date = request.POST.get('date')
        time_slot_id = request.POST.get('time_slot')

        if not date or not time_slot_id:
            return redirect(request.path)

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        # double booking protection
        if Appointment.objects.filter(
            date=date_obj,
            time_slot=time_slot,
            service=service
        ).exists():
            return redirect(request.path + f'?date={date}')

        appointment = Appointment.objects.create(
            user=request.user,
            service=service,
            date=date_obj,
            time_slot=time_slot
        )

        return redirect(f'/payment/{appointment.id}/')

    return render(request, 'appointments/book.html', {
        'service': service,
        'time_slots': time_slots,
        'booked_slots': booked_slots,
        'disabled_slots': disabled_slots
    })


# 🔥 PAYMENT
def payment_page(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        appointment.payment_type = request.POST.get('payment_type')
        appointment.save()
        return redirect(f'/success/{appointment.id}/')

    return render(request, 'appointments/payment.html', {
        'appointment': appointment
    })


def payment_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/payment_success.html', {
        'appointment': appointment
    })


# 🔥 BOOKINGS
def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/my_bookings.html', {
        'appointments': appointments
    })


# 🔥 CANCEL
def cancel_booking(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.payment_type == 'cash':
        appointment.status = 'cancelled'
        appointment.save()

    return redirect('/my-bookings/')


# 🔥 ADMIN DASHBOARD
from django.db.models import Sum

def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_staff:
        return redirect('/')

    appointments = Appointment.objects.select_related('user', 'service', 'time_slot').all().order_by('-id')

    # 🔥 TOTAL REVENUE CALCULATION
    total_revenue = sum([a.service.price for a in appointments if a.status != 'cancelled'])

    return render(request, 'appointments/admin_dashboard.html', {
        'total_services': Service.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_users': User.objects.count(),
        'appointments': appointments,
        'total_revenue': total_revenue
    })
# 🔥 RESET BOOKINGS
def reset_bookings(request):

    if not request.user.is_authenticated:
        return redirect('/login/')

    if not request.user.is_staff:
        return redirect('/')

    Appointment.objects.all().delete()
    return redirect('/admin-dashboard/')


# 🔥 AUTH
def user_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('/')
    return render(request, 'appointments/login.html')


def user_signup(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        login(request, user)
        return redirect('/')
    return render(request, 'appointments/signup.html')


def user_logout(request):
    logout(request)
    return redirect('/')