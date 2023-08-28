from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateUserForm, EditProfileForm, LeaveCreationForm, UserUpdateForm
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Cast
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Attendance, Workday, Leave
from datetime import datetime, date, timedelta, time
from .utils import get_ordinal_suffix

# Create your views here.
@login_required(login_url="login")
def dashboard(request):
    user = request.user
    today = datetime.now().date()
    if user.is_staff:
        all_workers = User.objects.all()
        workers_count = all_workers.count()
        present = 0
        worker_attendances = []
        for worker in all_workers:
            attendance_today = Attendance.objects.filter(user=worker, workday__workday=today)
            worker_attendances.append((worker, attendance_today))
            if attendance_today.exists():
                present += 1
        
        leaves_count = Leave.objects.get_all_current_active_leaves_count()
        absent = workers_count - (leaves_count + present)

        weeks_attendances_count = Workday.objects.return_all_weeks_attendances_count()
        avg_week_attendance = weeks_attendances_count / (workers_count*7) * 100
        highest_attendance = Workday.objects.get_employees_with_highest_attendances(all_workers)


        today = today.strftime("%d %B, %Y")
        day, month, year = today.split()
        today = f"{day}{get_ordinal_suffix(int(day))} {month}, {year}"

        context = {
            'workers_count':workers_count,
            'present':present,
            'leaves_count':leaves_count,
            'absent':absent,
            'worker_attendances':worker_attendances,
            'all_workers':all_workers,
            'avg_week_attendance':round(avg_week_attendance),
            'highest_attendance':highest_attendance[:5],
            'today':today
        }

    else:   
        attended_today = False
        attendance_today = Attendance.objects.filter(user=user, workday__workday=today)
        weeks_attendances = Workday.objects.return_users_weeks_workdays(user)
        leaves = Leave.objects.all()
        user_leaves = leaves.filter(user=request.user).order_by('-start_date')
        user_active_vacation = Leave.objects.get_current_active_leave(user, "Vacation")
        user_active_sick_leave = Leave.objects.get_current_active_leave(user, "Sick leave")

        weeks_attendances_count = 0
        for att in weeks_attendances:
            if att[1]: weeks_attendances_count += 1

        if attendance_today.exists():
            attended_today = True

        avg_week_attendance = weeks_attendances_count / len(weeks_attendances) * 100

        context = {
            'attendance_today':attendance_today,
            'weeks_attendances':weeks_attendances,
            'user_active_vacation':user_active_vacation,
            'user_active_sick_leave':user_active_sick_leave,
            'leaves':leaves,
            'user_leaves':user_leaves,
            'attended_today':attended_today,
            'avg_week_attendance':round(avg_week_attendance),
            'today':today,
        }

    return render(request, "base/dashboard.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = CreateUserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data.get('username')
        user.save()
        messages.success(request, f"Account has been created for {username}")
        return redirect("login")
    else:
        messages.error(request, f"Invalid credentials! Username might be taken")

    context = {
        "form": form,
    }
    return render(request, "base/register.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.warning(request, "Invalid Username or Password!")
        except:
            messages.warning(request, "User does not exist!")

    return render(request, "base/login_page.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def profile_view(request):
    user = request.user

    context = {
        "user":user
    }
    return render(request, 'base/profile.html', context)


@login_required(login_url="login")
def edit_profile_view(request):
    user = request.user
    p_form = EditProfileForm(request.POST or None, request.FILES or None, instance=user.profile)
    u_form = UserUpdateForm(request.POST or None, instance=request.user)

    if request.method == "POST":
        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            messages.success(request, "Profile has updated successfully")
            return redirect('profile')
        else:
            messages.error(request, "Profile did not update. Please provide valid data for all fields")

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'base/edit_profile.html', context)


@login_required(login_url="login")
def timesheets(request):
    start_date = request.GET.get('start_date')
    stop_date = request.GET.get('stop_date')

    workday_objects = Workday.objects.all()
    if start_date and stop_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        stop_date = datetime.strptime(stop_date, '%Y-%m-%d').date()
        workday_objects = workday_objects.filter(workday__gte=start_date, workday__lte=stop_date)
    elif start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        stop_date = start_date + timedelta(days=30)
        workday_objects = workday_objects.filter(workday__gte=start_date)
    elif stop_date:
        stop_date = datetime.strptime(stop_date, '%Y-%m-%d').date()
        start_date = stop_date - timedelta(days=30)
        workday_objects = workday_objects.filter(workday__lte=stop_date)
    else:
        stop_date = date.today()
        start_date = stop_date - timedelta(days=30)
    
    
    user_attendances = []
    total_work_hours = 0
    regular, overtime = 0, 0
    for workday in workday_objects:
        workday_hour = workday.get_workday_hours()
        total_work_hours += workday_hour
        attendance = workday.get_user_workday_attendance(request.user)
        if attendance:
            user_workday_hour = attendance.get_work_hours()
            regular += user_workday_hour
            
            if user_workday_hour > workday_hour:
                overtime += (user_workday_hour - workday_hour)
        
        user_attendances.append((workday, attendance))

    vacations_days = Leave.objects.get_leave_type_in_time_range(request.user, start_date, stop_date, "Vacation")
    sick_leave_days = Leave.objects.get_leave_type_in_time_range(request.user, start_date, stop_date, "Sick leave")
    start_date = start_date.strftime('%Y-%m-%d')
    stop_date = stop_date.strftime('%Y-%m-%d')

    context = {
        'user_attendances':user_attendances,
        'total_work_hours':total_work_hours,
        'overtime':round(overtime, 2),
        'vacations_days':vacations_days,
        'sick_leave_days':sick_leave_days,
        'regular':round(regular,1),
        'start_date':start_date,
        'stop_date':stop_date,
    }
    return render(request, 'base/timesheets.html', context)


@login_required(login_url="login")
def request_leave(request):
    if request.method == "POST":
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('stop_date')
        note = request.POST.get('note')
        
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        today = datetime.now().date()

        if leave_type and start_date and end_date:
            if start_date >= today and start_date < end_date:
                leave_obj = Leave.objects.create(
                    user=request.user,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    note=note
                )
                messages.success(request, f"Leave requested, Waiting for approval")
                leave_obj.save()
                return redirect("home")
            else:
                messages.error(request, f"Please set your start date and date properly")
        else:
            messages.error(request, f"Please provide the leave type and duration of leave")

    context = {}
    return render(request, 'base/request_leave.html', context)


@login_required(login_url="login")
def employees(request):
    user = request.user
    if not user.is_staff:
        return redirect('home')

    q = request.GET.get("q") if request.GET.get("q") != None else ""
    category = request.GET.get("category")

    all_workers = User.objects.filter(
        Q(username__icontains=q) | Q(email__icontains=q)
    )

    if category == "Admin":
        all_workers = all_workers.filter(is_staff=True)
    elif category == "Employee":
        all_workers = all_workers.filter(is_staff=False)

    context = {
        'all_workers':all_workers,
        'category':category,
        'q':q
    }
    return render(request, 'base/employees.html', context)


@login_required(login_url="login")
def employee_details(request, pk):
    category = request.GET.get('category')
    user = request.user
    employee = User.objects.get(id=pk)
    if not user.is_staff:
        return redirect('home')

    workdays = Workday.objects.all()
    if category == "This year":
        current_year = datetime.now().year
        beginning_of_year = datetime(year=current_year, month=1, day=1).date()
        workdays = workdays.filter(workday__gte=beginning_of_year)
    elif category == "Last year":
        current_year = datetime.now().year
        beginning_of_last_year = datetime(year=current_year - 1, month=1, day=1).date()
        end_of_last_year = datetime(year=current_year - 1, month=12, day=31, hour=23, minute=59, second=59).date()
        workdays = workdays.filter(workday__range=(beginning_of_last_year, end_of_last_year))
    elif category == "Years before":
        current_year = datetime.now().year
        end_of_last_2_years = datetime(year=current_year - 2, month=12, day=31, hour=23, minute=59, second=59).date()
        workdays = workdays = workdays.filter(workday__lte=end_of_last_2_years)

    punctual = False
    attendances = []
    for workday in workdays:
        attendance = workday.get_user_workday_attendance(employee)
        attendances.append((workday, attendance))

    total_attendance = Attendance.objects.filter(user=employee).count()
    avg_check_in_time = Attendance.objects.get_average_check_in_time(employee)
    avg_check_out_time = Attendance.objects.get_average_check_out_time(employee)

    if avg_check_in_time:
        if avg_check_in_time <= time(8, 30):
            punctual = True

    context = {
        'employee':employee,
        'attendances':attendances,
        'total_attendance':total_attendance,
        'avg_check_in_time':avg_check_in_time,
        'avg_check_out_time':avg_check_out_time,
        'punctual':punctual,
        'category':category,
    }
    return render(request, 'base/employee_details.html', context)


@login_required(login_url="login")
def requests(request):
    pending_requests = Leave.objects.get_all_pending_leaves()
    requests_count = len(pending_requests)

    context = {
        'pending_requests':pending_requests,
        'requests_count':requests_count,
    }
    return render(request, 'base/requests.html', context)


@login_required(login_url="login")
def request_details(request, pk):
    curr_request = Leave.objects.get(id=pk)
    user_active_vacation = Leave.objects.get_current_active_leave(curr_request.user, "Vacation")
    user_active_sick_leave = Leave.objects.get_current_active_leave(curr_request.user, "Sick leave")

    context = {
        'curr_request':curr_request,
        'user_active_vacation':user_active_vacation,
        'user_active_sick_leave':user_active_sick_leave
    }
    return render(request, 'base/request_detail.html', context)


@login_required(login_url="login")
def accept_request(request):
    if request.method == "POST":
        today = datetime.now().date()
        request_id = request.POST.get('request_id')
        leave_request = Leave.objects.get(id=request_id)

        if request.user.is_staff:
            leave_request.status = "Accepted"
            leave_request.reviewed_on = today
            leave_request.reviewed_by = request.user
            leave_request.save()
            messages.success(request, f"Request has been accepted")
            return redirect('requests')
        else:
            messages.warning(request, f"You are not authorized to visit that page")
            return redirect('home')
    return redirect('home')


@login_required(login_url="login")
def decline_request(request):
    if request.method == "POST":
        today = datetime.now().date()
        request_id = request.POST.get('request_id')
        leave_request = Leave.objects.get(id=request_id)

        if request.user.is_staff:
            leave_request.status = "Declined"
            leave_request.reviewed_on = today
            leave_request.reviewed_by = request.user
            leave_request.save()
            messages.success(request, f"Request has been accepted")
            return redirect('requests')
        else:
            messages.warning(request, f"You are not authorized to visit that page")
            return redirect('home')
    return redirect('home')



