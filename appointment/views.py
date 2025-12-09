from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from datetime import date, datetime, timedelta, time
from .models import Appointment
from .forms import UserRegisterForm, AppointmentForm


# ============== PUBLIC VIEWS ==============

def home(request):
    """
    Homepage - accessible to everyone
    """
    return render(request, 'appointment/home_page.html')


def register_user(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login_user')
    else:
        form = UserRegisterForm()
    
    return render(request, 'appointment/register_user.html', {'form': form})


def login_user(request):
    """
    User login view
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if not user.is_staff:  # Regular users only
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    return redirect('dashboard_user')
                else:
                    messages.error(request, 'Please use admin login.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'appointment/login_user.html', {'form': form})


def login_admin(request):
    """
    Admin login view - only for staff users
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_staff:  # Admin users only
                    login(request, user)
                    messages.success(request, f'Welcome, Admin {username}!')
                    return redirect('dashboard_admin')
                else:
                    messages.error(request, 'You do not have admin privileges.')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'appointment/login_admin.html', {'form': form})


def logout_view(request):
    """
    Logout view for both users and admins
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ============== USER VIEWS ==============

@login_required
def dashboard_user(request):
    """
    User dashboard - shows user menu
    """
    if request.user.is_staff:
        return redirect('dashboard_admin')
    
    return render(request, 'appointment/dashboard_user.html')

@login_required
def book_appointment(request):
    """
    Book a new appointment with properly formatted time slots
    """
    if request.user.is_staff:
        return redirect('dashboard_admin')
    
    # Generate available time slots (9 AM to 5 PM, every 30 minutes)
    available_slots = []
    start_hour = 9
    end_hour = 17
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            # Create time object
            time_obj = time(hour, minute)
            # Format for display (e.g., "9:00 AM")
            display_time = datetime.combine(date.today(), time_obj).strftime("%I:%M %p")
            # Format for value (e.g., "09:00")
            value_time = time_obj.strftime("%H:%M")
            
            available_slots.append({
                'value': value_time,
                'display': display_time
            })
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.status = 'active'
            
            # Check if slot is already booked
            existing = Appointment.objects.filter(
                date=appointment.date,
                time=appointment.time,
                status='active'
            ).exists()
            
            if existing:
                messages.error(request, 'This time slot is already booked. Please choose another.')
            else:
                appointment.save()
                messages.success(request, 'Appointment booked successfully!')
                return redirect('my_appointments')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
        'available_slots': available_slots,
        'today': date.today().isoformat()
    }
    return render(request, 'appointment/book_appointment.html', context)

@login_required
def my_appointments(request):
    """
    View user's own appointments
    """
    if request.user.is_staff:
        return redirect('dashboard_admin')
    
    appointments = Appointment.objects.filter(user=request.user).order_by('-date', '-time')
    
    return render(request, 'appointment/view_my_appointments.html', {
        'appointments': appointments
    })

@login_required
def reschedule_appointment(request, appointment_id):
    """
    Reschedule an existing appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check
    if not request.user.is_staff and appointment.user != request.user:
        messages.error(request, 'You do not have permission to modify this appointment.')
        return redirect('my_appointments')
    
    # Cannot reschedule cancelled appointments
    if appointment.status == 'cancelled':
        messages.error(request, 'Cannot reschedule a cancelled appointment.')
        return redirect('my_appointments')
    
    # Generate time slots
    available_slots = []
    start_hour = 9
    end_hour = 17
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            time_obj = time(hour, minute)
            display_time = datetime.combine(date.today(), time_obj).strftime("%I:%M %p")
            value_time = time_obj.strftime("%H:%M")
            
            available_slots.append({
                'value': value_time,
                'display': display_time
            })
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            
            # Check if new slot is available
            existing = Appointment.objects.filter(
                date=updated_appointment.date,
                time=updated_appointment.time,
                status='active'
            ).exclude(id=appointment_id).exists()
            
            if existing:
                messages.error(request, 'This time slot is already booked.')
            else:
                updated_appointment.save()
                messages.success(request, 'Appointment rescheduled successfully!')
                
                if request.user.is_staff:
                    return redirect('view_all_appointments')
                return redirect('my_appointments')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'available_slots': available_slots,
        'today': date.today().isoformat(),
        'is_reschedule': True
    }
    return render(request, 'appointment/book_appointment.html', context)



@login_required
def cancel_appointment(request, appointment_id):
    """
    Cancel an appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check
    if not request.user.is_staff and appointment.user != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('my_appointments')
    
    if appointment.status == 'cancelled':
        messages.info(request, 'This appointment is already cancelled.')
    else:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
    
    if request.user.is_staff:
        return redirect('view_all_appointments')
    return redirect('my_appointments')


# ============== ADMIN VIEWS ==============

@login_required
def dashboard_admin(request):
    """
    Admin dashboard with statistics
    """
    if not request.user.is_staff:
        return redirect('dashboard_user')
    
    total = Appointment.objects.count()
    active = Appointment.objects.filter(status='active').count()
    cancelled = Appointment.objects.filter(status='cancelled').count()
    
    context = {
        'total': total,
        'active': active,
        'cancelled': cancelled,
    }
    return render(request, 'appointment/dashboard_admin.html', context)


@login_required
def view_all_appointments(request):
    """
    Admin view - see all appointments
    """
    if not request.user.is_staff:
        return redirect('dashboard_user')
    
    appointments = Appointment.objects.select_related('user').order_by('-date', '-time')
    
    return render(request, 'appointment/view_all_appointments.html', {
        'appointments': appointments
    })