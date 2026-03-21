from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list),

    path('book/<int:service_id>/', views.book_appointment),

    path('payment/<int:appointment_id>/', views.payment_page),

    path('payment-success/<int:appointment_id>/', views.payment_success),

    path('my-bookings/', views.my_bookings),

    path('cancel/<int:appointment_id>/', views.cancel_booking),

    path('login/', views.user_login),
    path('signup/', views.user_signup),
    path('logout/', views.user_logout),

    path('success/<int:appointment_id>/', views.payment_success),

    # 🔥 DASHBOARD
    path('admin-dashboard/', views.admin_dashboard),

    # 🔥 RESET BOOKINGS (IMPORTANT)
    path('reset-bookings/', views.reset_bookings),
]