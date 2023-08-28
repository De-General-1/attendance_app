from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
# Create your models here.

class Profile(models.Model):
    Employee_choices = (
        ('Employee', 'Employee'),
        ('Manager', 'Manager')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    profile_pic = models.ImageField(default="avatar.png", upload_to='profiles/')
    position = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    role = models.CharField(max_length=8, choices=Employee_choices, default="Employee")
    location = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class WorkdayManager(models.Manager):
    def return_users_weeks_workdays(self, user):
        weekly_workdays = Workday.objects.all()[:7:-1]

        weeks_attendances = []
        for workday in weekly_workdays:
            attendance = workday.get_user_workday_hours(user)
            weeks_attendances.append((workday, attendance))
        return weeks_attendances

    def return_all_weeks_attendances_count(self):
        weekly_workdays = Workday.objects.all()[:7:-1]

        weeks_attendances = 0
        for workday in weekly_workdays:
            attendances = Attendance.objects.filter(workday__workday=workday.workday)
            weeks_attendances += attendances.count()
        return weeks_attendances


    def get_employees_with_highest_attendances(self, employees):
        weekly_workdays = Workday.objects.all()[:7:-1]

        weeks_attendances = []
        for employee in employees:
            count = 0
            for workday in weekly_workdays:
                attendance = Attendance.objects.filter(user=employee, workday__workday=workday.workday)
                if attendance.exists():
                    count += 1
            percentage = (count/len(weekly_workdays))*100
            weeks_attendances.append((employee, round(percentage, 1)))

        # Sort the list of tuples based on the second element (the percentage)
        weeks_attendances = sorted(weeks_attendances, key=lambda x: x[1], reverse=True)
        return weeks_attendances


class Workday(models.Model):
    workday = models.DateField()
    late_time = models.TimeField()
    end_time = models.TimeField()
    updated = models.DateTimeField(auto_now=True)
    objects = WorkdayManager()

    def __str__(self):
        return f"{self.workday}"

    class Meta:
        ordering = ['-workday']

    def get_user_workday_attendance(self, user):
        attendance = Attendance.objects.filter(user=user, workday__workday=self.workday)
        if attendance.exists():
            return attendance[0]

    def get_short_form_date(self):
        return self.workday.strftime("%b %d") 

    def get_workday_weekday(self):
        my_datetime = self.workday
        day_of_week_index = my_datetime.weekday()

        day_names = ["Mon", "Tue", "Wed", "Thu", "Frid", "Sat", "Sun"]
        return day_names[day_of_week_index]

    def get_workday_hours(self):
        late_time = datetime.combine(datetime.today(), self.late_time)
        end_time = datetime.combine(datetime.today(), self.end_time)
        time_difference = end_time - late_time
        total_hours = time_difference.total_seconds() / 3600
        return round(total_hours, 2)
        
    def get_user_workday_hours(self, user):
        attendance = self.get_user_workday_attendance(user)
        if attendance:
            return attendance.get_work_hours()
        return 0


class AttendanceManager(models.Manager):
    def get_average_check_in_time(self, user):
        all_attendances = Attendance.objects.filter(user=user)
        total_minutes, count = 0, 0
        for attendance in all_attendances:
            check_in = attendance.check_in
            total_minutes += check_in.hour * 60 + check_in.minute
            count += 1
        if count > 0:
            average_minutes = int(total_minutes/count)
            average_hours = int(average_minutes // 60)
            average_minutes %= 60
            average_time = time(average_hours, int(average_minutes))
            return average_time

    def get_average_check_out_time(self, user):
        all_attendances = Attendance.objects.filter(user=user)
        total_minutes, count = 0, 0
        for attendance in all_attendances:
            check_out = attendance.check_out
            total_minutes += check_out.hour * 60 + check_out.minute
            count += 1
        if count > 0:
            average_minutes = int(total_minutes/count)
            average_hours = int(average_minutes // 60)
            average_minutes %= 60
            average_time = time(average_hours, int(average_minutes))
            return average_time
        

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    check_in = models.TimeField(auto_now_add=True)
    check_out = models.TimeField(blank=True)
    note = models.TextField(blank=True)
    workday = models.ForeignKey(Workday, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    objects = AttendanceManager()

    def __str__(self):
        return f"{self.user} attendance on {self.workday}"
    
    def get_work_hours(self):
        if self.check_in and self.check_out:
            common_date = datetime.now().date()
            start_datetime = datetime.combine(common_date, self.check_in)
            end_datetime = datetime.combine(common_date, self.check_out)

            time_difference = end_datetime - start_datetime
            total_hours = time_difference.total_seconds() / 3600
            return round(total_hours, 1)
        return 0

    def get_formated_checkin_time(self):
        return self.check_in.strftime("%I:%M %p").upper()

    def get_formated_checkout_time(self):
        return self.check_out.strftime("%I:%M %p").upper()

    def on_time(self):
        workday = self.workday
        if self.check_in <= workday.late_time:
            return True
        return False
    
    def get_over_time(self):
        workday_hours = self.workday.get_workday_hours()
        user_hours = self.get_work_hours()
        if user_hours > workday_hours:
            return round(user_hours - workday_hours, 2)
        return 0.0


class LeaveManager(models.Manager):
    def get_current_active_leave(self, user, type_):
        today = datetime.now().date()
        accepted = Leave.objects.filter(user=user, status="Accepted", leave_type=type_)

        for leave in accepted:
            if today >= leave.start_date and today <= leave.end_date:
                return leave
        return None

    def get_all_current_active_leaves_count(self):
        today = datetime.now().date()
        accepted = Leave.objects.filter(status="Accepted")

        active_leaves = 0
        for leave in accepted:
            if today >= leave.start_date and today <= leave.end_date:
                active_leaves += 1
        return active_leaves
    
    def get_all_pending_leaves(self):
        today = datetime.now().date()
        leaves_in_review = Leave.objects.filter(status="in Review")
        pending_leaves = []
        for leave in leaves_in_review:
            if leave.start_date > today:
                pending_leaves.append(leave)
        return pending_leaves

    def get_leave_type_in_time_range(self, user, start, end, type_):
        today = datetime.now().date()
        user_leaves = Leave.objects.filter(user=user, leave_type=type_)

        leave_duration = 0
        for leave in user_leaves:
            if leave.start_date >= start and leave.end_date <= end:
                leave_duration += leave.get_leave_duration()
            elif leave.start_date >= start and leave.start_date <= end:
                leave_duration += ((end - leave.start_date).days + 1)
            elif leave.end_date <= end and leave.end_date >= start:
                leave_duration += ((leave.end_date - start).days + 1)
        return leave_duration


class Leave(models.Model):
    Leave_type = (
        ('Sick leave', 'Sick leave'),
        ('Vacation', 'Vacation'),
    )

    Leave_status = (
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined'),
        ('in Review', 'in Review')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=10, choices=Leave_type)
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=Leave_status, default="in Review")
    reviewed_on = models.DateField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approved_leaves", blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    objects = LeaveManager()

    def get_leave_duration(self):
        time_difference = self.end_date - self.start_date
        return time_difference.days + 1

    def get_used_days(self):
        today = datetime.now().date()
        return (today - self.start_date).days

    def get_formatted_start_date(self):
        return self.start_date.strftime("%d %B, %Y")

    def get_formatted_end_date(self):
        return self.end_date.strftime("%d %B, %Y")

    def get_used_percentage(self):
        used = self.get_used_days()
        duration = self.get_leave_duration()
        used_percentage = used/duration * 100
        return used_percentage

    def get_remaining_days(self):
        duration = self.get_leave_duration()
        used_days = self.get_used_days()
        return duration - used_days

    def __str__(self):
        return f"{self.user}--{self.leave_type}--{self.status}"

    

