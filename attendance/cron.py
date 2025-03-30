
from django_cron import CronJobBase, Schedule
from attendance.utils import check_and_send_teacher_attendance_warnings
from attendance.utils import check_and_send_attendance_warnings
class AttendanceWarningCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Run every 60 minutes (Change as needed)

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "attendance.attendance_warning_cron"

    def do(self):
        
        check_and_send_teacher_attendance_warnings()
        check_and_send_attendance_warnings()
