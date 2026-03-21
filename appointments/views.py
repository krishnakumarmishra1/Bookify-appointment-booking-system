from django.shortcuts import render, redirect, get_object_or_404
from .models import Service, TimeSlot, Appointment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum


# 🔥 SERVICE LIST
def service_list(request):
    category = request.GET.get('category')
    query = request.GET.get('q')

    services = Service.objects.all()

    if category:
        services = services.filter(category=category)

    if query:
        services = services.filter(name__icontains=query)

    return render(request, 'appointments/service_list.html', {
        'services': services
    })


# 🔥 BOOK APPOINTMENT
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

        booked_slots = Appointment.objects.filter(
            date=selected_date_obj,
            service=service
        ).values_list('time_slot_id', flat=True)

        if selected_date_obj == now.date():
            for slot in time_slots:
                slot_time = datetime.combine(now.date(), slot.start_time)
                slot_time = timezone.make_aware(slot_time)

                if slot_time < now:
                    disabled_slots.append(slot.id)

    if request.method == 'POST':
        date = request.POST.get('date')
        time_slot_id = request.POST.get('time_slot')

        if not date or not time_slot_id:
            return redirect(request.path)

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        exists = Appointment.objects.filter(
            date=date_obj,
            time_slot=time_slot,
            service=service
        ).exists()

        if exists:
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


# 🔥 PAYMENT PAGE
def payment_page(request, appointment_id):

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        payment_type = request.POST.get('payment_type')

        appointment.payment_type = payment_type
        appointment.save()

        return redirect(f'/success/{appointment.id}/')

    return render(request, 'appointments/payment.html', {
        'appointment': appointment
    })


# 🔥 PAYMENT SUCCESS
def payment_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/payment_success.html', {
        'appointment': appointment
    })


# 🔥 MY BOOKINGS
def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments/my_bookings.html', {
        'appointments': appointments
    })


# 🔥 CANCEL BOOKING
def cancel_booking(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.payment_type == 'cash':
        appointment.status = 'cancelled'
        appointment.save()

    return redirect('/my-bookings/')


# 🔥 LOGIN
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


# 🔥 SIGNUP
def user_signup(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        login(request, user)
        return redirect('/')
    return render(request, 'appointments/signup.html')


# 🔥 LOGOUT
def user_logout(request):
    logout(request)
    return redirect('/')


# ================================
# 🚀 ADMIN DASHBOARD (NEW)
# ================================
def admin_dashboard(request):

    # ❗ OPTIONAL: सिर्फ admin access
    if not request.user.is_superuser:
        return redirect('/')

    today = timezone.localdate()

    total_bookings = Appointment.objects.count()

    today_bookings = Appointment.objects.filter(date=today).count()

    # 💰 revenue = only online payments
    total_revenue = sum(
        a.service.price
        for a in Appointment.objects.filter(payment_type='online')
    )

    recent_bookings = Appointment.objects.select_related('service', 'user').order_by('-id')[:10]

    return render(request, 'appointments/admin_dashboard.html', {
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    })
def reset_bookings(request):

    if not request.user.is_superuser:
        return redirect('/')

    Appointment.objects.all().delete()

    return redirect('/admin-dashboard/')