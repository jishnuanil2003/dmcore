#DMCORE with buffer

# Create your models here.
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from datetime import date
from django.core.validators import FileExtensionValidator
from datetime import timedelta
from .interview_questions import MAX_QUESTION_ID, MIN_QUESTION_ID, QUESTION_BY_ID, QUESTION_CHOICES

# Create your models here.
class LogRegister_Details(models.Model):  
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Digital_Marketing_Head', 'Digital_Marketing_Head'),
        ('Team_Lead', 'Team_Lead'),
        ('Executive', 'Executive'),
        ('Data_Manager', 'Data_Manager'),
        ('Telecaller', 'Telecaller'),
        ('HR', 'HR'),
        ('Graphics Designer','Graphics Designer')

    ]
    
    log_username = models.CharField(max_length=255, null=True, blank=True)
    log_password = models.CharField(max_length=255, blank=True, null=True, default='')
    log_date = models.DateField(auto_now_add=True)
    log_time = models.TimeField(auto_now_add=True)
    position = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True, blank=True)
    is_staff = models.BooleanField(default=False) 
    status = models.IntegerField(default=1) 
    active_status = models.BooleanField(default=True)  

    def __str__(self):
        return self.log_username or "Unnamed User"
    
    
class DistributorRegister_Details(models.Model):
    login = models.ForeignKey('LogRegister_Details', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_no = models.CharField(max_length=255, blank=True, null=True, default='')
    email = models.EmailField(max_length=255, blank=True, null=True)
    agencies = models.CharField(max_length=255, blank=True, null=True, default='')
    profile = models.FileField(upload_to='profiles/', blank=True, null=True)
    file = models.FileField(upload_to='employee_files/', blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True, default='')
    address2 = models.CharField(max_length=255, blank=True, null=True, default='')
    address3 = models.CharField(max_length=255, blank=True, null=True, default='')
    pin = models.CharField(max_length=50, blank=True, null=True, default='')
    location = models.CharField(max_length=150, blank=True, null=True, default='')
    district = models.CharField(max_length=150, blank=True, null=True, default='')
    state = models.CharField(max_length=150, blank=True, null=True, default='')
    active_status = models.BooleanField(default=False)
    reg_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name or "Unnamed Distributor"
    
    
class BusinessRegister_Details(models.Model):
    login = models.ForeignKey('LogRegister_Details', on_delete=models.CASCADE, null=True, blank=True)
    distributor = models.ForeignKey('DistributorRegister_Details', on_delete=models.CASCADE, null=True, blank=True)
    owner_fname = models.CharField(max_length=255, blank=True, null=True, default='')
    owner_lname = models.CharField(max_length=255, blank=True, null=True, default='')
    company_name = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_number = models.CharField(max_length=255, blank=True, null=True, default='')
    email = models.EmailField(max_length=255, blank=True, null=True)
    logo = models.FileField(upload_to='profiles/', blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True, default='')
    address_line1 = models.CharField(max_length=255, blank=True, null=True, default='')
    address_line2 = models.CharField(max_length=255, blank=True, null=True, default='')
    address_line3 = models.CharField(max_length=255, blank=True, null=True, default='')
    pin = models.CharField(max_length=50, blank=True, null=True, default='')
    location = models.CharField(max_length=150, blank=True, null=True, default='')
    district = models.CharField(max_length=150, blank=True, null=True, default='')
    state = models.CharField(max_length=150, blank=True, null=True, default='')
    active_status = models.BooleanField(default=True)
    reg_date = models.DateField(auto_now_add=True)
    company_code = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.company_name or "Unnamed Business"

class DepartmentRegister_Details(models.Model):
    business = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    active_status = models.BooleanField(default=True)
    description = models.TextField(default='', null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'department_register_details'

    def __str__(self):
        return self.name or "Unnamed Department"
    
class DesignationRegister_Details(models.Model):
    ROLE_CHOICES = [
        ('Digital_Marketing_Head', 'Digital_Marketing_Head'),
        ('Team_Lead', 'Team_Lead'),
        ('Executive', 'Executive'),
        ('Data_Manager', 'Data_Manager'),
        ('Telecaller', 'Telecaller'),
        ('HR', 'HR'),
        ('Graphics Designer','Graphics Designer')
    ]
    
    business = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(DepartmentRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    dashboard_id = models.CharField(max_length=50, choices=ROLE_CHOICES,null=True, blank=True) 
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)
    active_status = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'designation_register_details'

    def __str__(self):
        return self.name or "Unnamed Designation"
    
class EmployeeRegister_Details(models.Model):
    login = models.ForeignKey(LogRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(DepartmentRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.ForeignKey(DesignationRegister_Details, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255, default='', null=True, blank=True)
    employee_code = models.CharField(max_length=255, default='EMP001', null=True, blank=True)
    contact_number = models.CharField(max_length=255, default='', null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles', default='')
    documents = models.FileField(upload_to='employee_files', default='')

    address_line1 = models.CharField(max_length=255, default='', null=True, blank=True)
    address_line2 = models.CharField(max_length=255, default='', null=True, blank=True)
    address_line3 = models.CharField(max_length=255, default='', null=True, blank=True)
    pin = models.CharField(max_length=50, default='', null=True, blank=True)
    location = models.CharField(max_length=150, default='', null=True, blank=True)
    district = models.CharField(max_length=150, default='', null=True, blank=True)
    state = models.CharField(max_length=150, default='', null=True, blank=True)
    STATUS_CHOICES = (
        ('Approved','Approved'),
        ('Pending','Pending'),
    )
    active_status = models.CharField(max_length=50,choices=STATUS_CHOICES,null=True,default='Pending')
    verification_status = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'employee_register_details'

    def __str__(self):
        return self.name or "Unnamed Employee"
    
class EmployeeSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey('EmployeeRegister_Details', on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    schedule_head = models.CharField(max_length=255, null=True, blank=True)
    todo_content = models.TextField(null=True, blank=True)
    log_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    schedule_date = models.DateField(null=True, blank=True)
    schedule_status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')

    def __str__(self):
        return f"{self.employee} - {self.schedule_head or 'Schedule'} ({self.schedule_status})"
    
    
class Feedback(models.Model):
    employee = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)  # Receiver of feedback
    from_id = models.IntegerField(default=0)  # ID of the person giving feedback
    from_name = models.CharField(max_length=255, null=True, blank=True)  # Name of the sender
    feedback_content = models.TextField(null=True, blank=True)  # Feedback content
    feedback_date = models.DateField(null=True, blank=True)  # Feedback date

    def __str__(self):
        return f"Feedback by {self.from_name or 'Unknown'} to {self.employee}"
    
    
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )

    employee = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True) # Employee who submitted the complaint
    compaint_head = models.CharField(max_length=255, null=True, blank=True) # Title or subject of the complaint
    compaint_content = models.TextField(null=True, blank=True)  # Detailed complaint content
    complaint_date = models.DateField(auto_now_add=True, null=True)
    action = models.TextField(null=True, blank=True) # Action taken on complaint (if any)
    action_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending') # Current status of the complaint

    def __str__(self):
        return f"Complaint by {self.employee} - {self.get_status_display()}"
    
    
class ActionTaken(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    employee = models.ForeignKey(EmployeeRegister_Details,on_delete=models.CASCADE,null=True,blank=True)
    from_id = models.IntegerField(default=0) # ID of the person who took the action
    from_name = models.CharField(max_length=255,null=True,blank=True) # Name of the person who took the action
    act_reason = models.TextField(null=True,blank=True) # Reason for the action
    act_head = models.CharField(max_length=255,null=True,blank=True) # Short title/headline of the action
    act_content = models.TextField(null=True,blank=True) # Detailed description of the action
    action_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Action on {self.employee} - {self.title or 'No Title'}"
    
    
class EmployeeLeave(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'), 
        ('approved', 'Approved'), 
        ('rejected', 'Rejected'),
    )
    
    employee = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    leave_type = models.CharField(max_length=255, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    number_of_days = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateField(auto_now_add=True, null=True)
    status_changed_date = models.DateField(null=True, blank=True)
    request_file = models.FileField(upload_to='leave/files/', null=True, blank=True)

    def __str__(self):
        return f"Leave Request by {self.employee} ({self.start_date} to {self.end_date})"

class AllocationDetails(models.Model):
    employee = models.ForeignKey(EmployeeRegister_Details,on_delete=models.CASCADE,null=True,blank=True)  # The employee being allocated
    team_lead = models.ForeignKey(EmployeeRegister_Details,on_delete=models.CASCADE,related_name="allocated_employees",null=True,blank=True) 
    # The team lead to whom the employee is allocated
    allocate_status = models.IntegerField(default=0)
    allocation_date = models.DateField(auto_now_add=True, null=True, blank=True)

    def _str_(self):
        return f"{self.employee} -> {self.team_lead} ({self.allocate_status})"
    
#================================================= DM Head models ===============================================

class Work_Task(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    task_name = models.CharField(max_length=255, null=True, blank=True)
    task_description = models.TextField(null=True, blank=True)
    task_add_time = models.TimeField(auto_now_add=True)
    task_add_date = models.DateField(auto_now=True)
    task_status = models.IntegerField(default=0)

    def __str__(self):
        return self.task_name or "Unnamed Task"
    
class ClientRegister(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    # Client personal info
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_email_primary = models.EmailField(null=True, blank=True)
    client_email_alter = models.EmailField(null=True, blank=True)
    client_phone = models.CharField(max_length=20, null=True, blank=True)
    client_phone_alter = models.CharField(max_length=20, null=True, blank=True)
    client_address1 = models.CharField(max_length=255, null=True, blank=True)
    client_address2 = models.CharField(max_length=255, null=True, blank=True)
    client_address3 = models.CharField(max_length=255, null=True, blank=True)
    client_place = models.CharField(max_length=255, null=True, blank=True)
    client_district = models.CharField(max_length=255, null=True, blank=True)
    client_state = models.CharField(max_length=255, null=True, blank=True)
    client_profile = models.ImageField(upload_to='client/profile/', null=True, blank=True)

    # Business details
    client_business_name = models.CharField(max_length=255, null=True, blank=True)
    client_business_email_primary = models.EmailField(null=True, blank=True)
    client_business_email_alter = models.EmailField(null=True, blank=True)
    client_business_phone = models.CharField(max_length=20, null=True, blank=True)
    client_business_phone_alter = models.CharField(max_length=20, null=True, blank=True)
    client_business_website = models.CharField(max_length=255, null=True, blank=True)
    client_business_address1 = models.CharField(max_length=255, null=True, blank=True)
    client_business_address2 = models.CharField(max_length=255, null=True, blank=True)
    client_business_address3 = models.CharField(max_length=255, null=True, blank=True)
    client_business_place = models.CharField(max_length=255, null=True, blank=True)
    client_business_district = models.CharField(max_length=255, null=True, blank=True)
    client_business_state = models.CharField(max_length=255, null=True, blank=True)
    client_business_file = models.ImageField(upload_to='client/files/', null=True, blank=True)
    business_logo = models.ImageField(upload_to='client/logo/', null=True, blank=True)

    more_description = models.TextField(null=True, blank=True)
    client_add_time = models.TimeField(auto_now_add=True)
    client_status = models.IntegerField(default=0)
    work_reg_status = models.IntegerField(default=0)
    client_reg_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.client_name or "Unnamed Client"
    
class WorkRegister(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(ClientRegister, on_delete=models.CASCADE, null=True, blank=True)
    allocated_employees = models.ManyToManyField(EmployeeRegister_Details, related_name='works_allocated')
    work_description = models.TextField(null=True, blank=True)
    work_file = models.FileField(upload_to='work/files/', null=True, blank=True)
    work_create_time = models.TimeField(auto_now_add=True)
    work_create_date = models.DateField(auto_now_add=True)
    work_end_date = models.DateField(null=True, blank=True)
    work_progress = models.IntegerField(default=0)  # e.g., 0 to 100
    work_allocate_status = models.IntegerField(default=0)  
    work_status = models.IntegerField(default=0)  

    def __str__(self):
        return f"Work for {self.client} - {self.company}"
    
class ClientTask_Register(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(ClientRegister, on_delete=models.CASCADE, null=True, blank=True)
    work = models.ForeignKey(WorkRegister, on_delete=models.CASCADE, null=True, blank=True)
    task_name = models.CharField(max_length=255, null=True, blank=True)
    task_description = models.TextField(null=True, blank=True)
    task_file = models.FileField(upload_to='work/task/files/', null=True, blank=True)
    task_allocate_status = models.IntegerField(default=0)
    task_total_progress = models.IntegerField(default=0)
    task_status = models.IntegerField(default=0)
    task_create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_name} for {self.client}"
    
class LeadCategory_Register(models.Model):
    client_task = models.ForeignKey(ClientTask_Register, on_delete=models.CASCADE, null=True, blank=True)
    assign_date = models.DateField(auto_now=True, null=True, blank=True)
    collection_for = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    target = models.IntegerField(default=0)
    target_achieved = models.IntegerField(default=0)
    file = models.FileField(upload_to='work/files/', null=True, blank=True)
    progress = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.collection_for} ({self.progress}%)"
    
class LeadField_Register(models.Model):
    client = models.ForeignKey(ClientRegister, on_delete=models.CASCADE, null=True, blank=True)
    work = models.ForeignKey(WorkRegister, on_delete=models.CASCADE, null=True, blank=True)
    lead_category = models.ForeignKey(LeadCategory_Register, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    question_id = models.IntegerField(null=True, blank=True, choices=QUESTION_CHOICES)
    add_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    status = models.IntegerField(default=0)
    add_date = models.DateField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(question_id__isnull=True) | Q(
                    question_id__gte=MIN_QUESTION_ID,
                    question_id__lte=MAX_QUESTION_ID,
                ),
                name='leadfield_question_id_range',
            ),
            models.UniqueConstraint(
                fields=['work', 'question_id'],
                condition=Q(work__isnull=False, question_id__isnull=False),
                name='uniq_lead_question_work',
            ),
        ]

    def clean(self):
        super().clean()
        if (not self.work_id or not self.client_id) and self.lead_category_id:
            cat_task = getattr(self.lead_category, 'client_task', None)
            if cat_task:
                if not self.work_id and cat_task.work_id:
                    self.work_id = cat_task.work_id
                if not self.client_id and cat_task.client_id:
                    self.client_id = cat_task.client_id
        errors = {}
        if self.question_id is not None and self.question_id not in QUESTION_BY_ID:
            errors['question_id'] = f'Choose one of the {len(QUESTION_BY_ID)} available interview questions.'
        if self.question_id is not None and self.work_id:
            duplicate = type(self).objects.filter(
                work_id=self.work_id, question_id=self.question_id
            ).exclude(pk=self.pk).exists()
            if duplicate:
                errors['question_id'] = 'This interview question is already assigned to another field in this work.'
        if errors:
            raise ValidationError(errors)

    @property
    def question_label(self):
        if self.question_id is None:
            return 'Not asked'
        return QUESTION_BY_ID.get(self.question_id, ('', 'Not asked'))[1]

    def __str__(self):
        return f"{self.name or 'Unnamed Field'}"
        
class WorkAssign(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(ClientRegister, on_delete=models.CASCADE, null=True, blank=True)
    work_register = models.ForeignKey(WorkRegister, on_delete=models.CASCADE, null=True, blank=True)
    team_lead = models.ForeignKey(EmployeeRegister_Details,on_delete=models.CASCADE,null=True,blank=True,related_name='allocated_tl')
    client_task = models.ManyToManyField(ClientTask_Register, related_name='task_allocated')
    co_workers = models.ManyToManyField(EmployeeRegister_Details, related_name='co_works_allocated')
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='work/files', null=True, blank=True)
    progress = models.IntegerField(default=0)
    assign_date = models.DateField(default=date.today, null=True, blank=True)                       #! =============== edited
    accept_date = models.DateField(null=True, blank=True)                                           #! =============== new field
    from_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(default=0)
    assign_type = models.IntegerField(default=0)
    target = models.IntegerField(default=0)
    target_achieved = models.IntegerField(default=0)
    
    # new added fields
    criteria = models.TextField(null=True, blank=True)

    is_instagram = models.BooleanField(default=False)
    is_facebook = models.BooleanField(default=False)
    is_x = models.BooleanField(default=False)

    instagram_target = models.IntegerField(default=0)
    facebook_target = models.IntegerField(default=0)
    x_target = models.IntegerField(default=0)

    def __str__(self):
        return f"Assignment for {self.client} - Progress: {self.progress}%"

class TaskAssign(models.Model):
    work_assign = models.ForeignKey(WorkAssign, on_delete=models.CASCADE, null=True, blank=True)
    executive = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    client_task = models.ForeignKey(ClientTask_Register, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='work/files', null=True, blank=True)
    progress = models.IntegerField(default=0)
    allocate_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    target = models.IntegerField(default=0)
    target_achieved = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    accept_status = models.IntegerField(default=0)
    accept_date = models.DateField(null=True, blank=True)
    type = models.IntegerField(default=0)

    def __str__(self):
        if self.client_task and self.executive:
            return f"Task {self.client_task} assigned to {self.executive}"
        return f"TaskAssign #{self.pk}"

class LeadCateogry_TeamAllocate(models.Model):
    team_lead = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    lead_category = models.ForeignKey(LeadCategory_Register, on_delete=models.CASCADE, null=True, blank=True)
    work_assign = models.ForeignKey(WorkAssign, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    accept_date = models.DateField(null=True, blank=True)                                              #! =========== new field
    target = models.IntegerField(default=0)
    target_achieved = models.IntegerField(default=0)
    file = models.FileField(upload_to='work/files', null=True, blank=True)
    progress = models.IntegerField(default=0)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.team_lead} assigned to {self.lead_category} (Progress: {self.progress}%)"
        
class LeadCategory_Assign(models.Model):
    executive = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    team_allocation = models.ForeignKey(LeadCateogry_TeamAllocate, on_delete=models.CASCADE, null=True, blank=True)
    task_assign = models.ForeignKey(TaskAssign, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    target = models.IntegerField(default=0)
    target_achieved = models.IntegerField(default=0)
    file = models.FileField(upload_to='work/files', null=True, blank=True)
    progress = models.IntegerField(default=0)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.executive} - {self.team_allocation}"
        
class WorkProgress(models.Model):
    employee = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    add_date = models.DateField(auto_now=True, null=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    progress_type = models.CharField(max_length=255, null=True, blank=True)
    progress = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    files = models.JSONField(default=list,blank=True)

    def __str__(self):
        return f"{self.employee or f'WorkProgress #{self.pk}'} - {self.progress}% on {self.add_date}"

#================================================= end DM Head models ===============================================

#================================================= team Leader models ===============================================

class TaskDetails(models.Model):
    is_category = models.BooleanField(default=False)
    work_assign = models.ForeignKey(WorkAssign, null=True, blank=True, on_delete=models.CASCADE)
    category_assign = models.ForeignKey(LeadCateogry_TeamAllocate, null=True, blank=True, on_delete=models.CASCADE)
    task_assign = models.ForeignKey(TaskAssign, on_delete=models.CASCADE, null=True, blank=True) 
    collect_date = models.DateField(auto_now=True, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='daily_work/files/', null=True, blank=True)
    target = models.IntegerField(default=0)
    achieved_target = models.IntegerField(default=0)
    verified_target = models.IntegerField(default=0)
    status = models.IntegerField(default=0)

    def _str_(self):
        return f"{self.title or 'Task Detail'}"

class Leads(models.Model):
    work = models.ForeignKey(WorkRegister, on_delete=models.CASCADE, null=True, blank=True)
    collected_by = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    task_assign = models.ForeignKey(TaskAssign, on_delete=models.CASCADE, null=True, blank=True)
    lead_category = models.ForeignKey(LeadCategory_Register, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    added_date = models.DateField(auto_now_add=True, null=True, blank=True)
    added_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    waste_data = models.IntegerField(default=0)
    waste_data_reason = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=0)
    transfer_date = models.DateField(auto_now_add=True, null=True, blank=True)
    transfer_status = models.IntegerField(default=0)
    incomplete_status = models.IntegerField(default=0)
    target_update_status = models.IntegerField(default=0)
    repeated_status = models.IntegerField(default=0)

    def __str__(self):
        return self.name or "Unnamed Lead"

    @property
    def has_valid_email_or_phone(self):
        from .validators import has_valid_email_or_phone
        return has_valid_email_or_phone(self)

    def clean(self):
        super().clean()
        if self.pk:
            from .models import LeadConfused
            if LeadConfused.objects.filter(lead_id=self.pk).exists():
                from .validators import has_valid_email_or_phone
                if not has_valid_email_or_phone(self):
                    raise ValidationError("Add an email or a phone number before marking this lead as confused")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
class LeadDetails(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    field_name = models.CharField(max_length=255, null=True, blank=True)
    field_data = models.CharField(max_length=855, null=True, blank=True)

    def __str__(self):
        return f"{self.field_name}: {self.field_data}"
        
class SocialMediaPromotion(models.Model):
    task_detail = models.ForeignKey(TaskDetails, on_delete=models.CASCADE, null=True, blank=True, related_name='social_promotions')
    work_assign = models.ForeignKey(WorkAssign, on_delete=models.CASCADE, null=True, blank=True)
    category_assign = models.ForeignKey(LeadCateogry_TeamAllocate, on_delete=models.SET_NULL, null=True, blank=True)
    platform = models.CharField(max_length=20)
    achieved_text = models.TextField()
    urls = models.TextField()
    screenshots = models.FileField(upload_to='uploads/social/screenshots/')
    remarks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.platform.capitalize()} Promotion for TaskDetail {self.task_detail_id}"
        
class TargetAssign(models.Model):

    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]

    company = models.ForeignKey('BusinessRegister_Details', on_delete=models.CASCADE, null=True, blank=True)
    executive = models.ForeignKey('EmployeeRegister_Details', on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    target_count = models.IntegerField()
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if not self.executive:
            return f"TargetAssign #{self.pk}"
        employee_name = self.executive.name or f"Employee #{self.executive_id}"
        return f"{employee_name} - {self.target_count} ({self.month or 'No month'}-{self.year or 'No year'})"
    

class PromotionalWork(models.Model):

    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )

    
    title = models.CharField(max_length=255)
    content = models.TextField()
    media = models.FileField(upload_to='promotional_work/', null=True, blank=True)  
    created_by = models.ForeignKey('EmployeeRegister_Details', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Posters(models.Model):

    STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )

    
    title = models.CharField(max_length=255)
    content = models.TextField()
    media = models.ImageField(upload_to='poster/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        null=True,
        blank=True
    )  
    created_by = models.ForeignKey('EmployeeRegister_Details', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#================================================= end Team leader models ===============================================
#=================================================  DM Head models ===============================================
# new
class DataBank(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    generated_date = models.DateField(auto_now_add=True, null=True, blank=True)
    used_count = models.IntegerField(default=0)
    lead_allocate_status = models.IntegerField(default=0)
    current_status = models.CharField(max_length=150, default='No update')
    allocated_date = models.DateField(null=True, blank=True)
    followup_date = models.DateField(null=True, blank=True)
    lead_status = models.CharField(max_length=150, default='Not Allocated')

    def _str_(self):
        return f"{self.lead} - {self.lead_status}"
    
class Platforms(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True, null=True, blank=True)
    platform_name = models.CharField(max_length=150, default='')
    platform_total_count = models.IntegerField(default=0)

    def _str_(self):
        return f"{self.platform_name} ({self.platform_total_count})"
    
class PlatformData(models.Model):
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    data_add_date = models.DateField(auto_now_add=True, null=True, blank=True)
    platform_name = models.CharField(max_length=150, default='')
    platform_data_count = models.IntegerField(default=0)

    def _str_(self):
        return f"{self.platform_name} - {self.platform_data_count}"

#================================================= end DM Head models ===============================================
    
#================================================= Data Manager models ===============================================

class LeadAssignedToTC(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    databank = models.ForeignKey(DataBank, on_delete=models.CASCADE, null=True, blank=True)
    telecaller = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    response = models.CharField(max_length=255, default='No Data Availale', null=True, blank=True)
    reason = models.CharField(max_length=255, default='', null=True, blank=True)
    assign_date = models.DateField(auto_now_add=True, null=True, blank=True)
    allocate_time = models.TimeField(auto_now_add=True)
    update_date = models.DateField(null=True, blank=True)
    next_update_date = models.DateField(null=True, blank=True)
    update_action = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    client = models.ForeignKey(ClientRegister, on_delete=models.CASCADE, null=True, blank=True)

    def _str_(self):
        return f"{self.lead} - {self.telecaller}"

class FollowupStatus(models.Model):
    status_name = models.CharField(max_length=150, default='')
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.status_name
    
#================================================= end Data Manager models ===============================================
    
#================================================= telecaller models ===================================================
class FollowupHistory(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    telecaller = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    allocated_date = models.DateField(null=True, blank=True)
    note = models.TextField(default='', null=True, blank=True)
    final_status = models.CharField(max_length=150, default='')

class WasteLead(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    assignment = models.ForeignKey(LeadAssignedToTC, on_delete=models.CASCADE, null=True, blank=True)
    databank = models.ForeignKey(DataBank, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(ClientRegister, on_delete=models.CASCADE, null=True, blank=True)
    telecaller = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    waste_marked_date = models.DateField(auto_now_add=True, null=True, blank=True)
    reason = models.TextField(default='', blank=True)
    status = models.IntegerField(default=0)
    head_reason = models.TextField(default='', blank=True)
    confirmation = models.IntegerField(default=0)

    def __str__(self):
        return f"WasteLead - {self.lead}"
        
class FollowupDetails(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(BusinessRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    telecaller = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    response_date = models.DateField(auto_now_add=True, null=True, blank=True)
    response = models.TextField(default='', null=True, blank=True)
    next_followup_date = models.DateField(null=True, blank=True)
    response_status = models.CharField(max_length=150, default='')
    is_notified_dm = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.lead} - {self.response_status}"

class LeadCallRecord(models.Model):
    assignment = models.ForeignKey(LeadAssignedToTC, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE, null=True, blank=True)
    record_date = models.DateField(auto_now_add=True, null=True, blank=True)
    record_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    record_file = models.FileField(upload_to='record/', null=True, blank=True)

    def __str__(self):
        return f"{self.lead} - {self.record_date} {self.record_time}"

#================================================= end telecaller models ===============================================
    
class LeadMeet(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE)
    assign = models.ForeignKey(LeadAssignedToTC, on_delete=models.CASCADE, null=True, blank=True)
    meet_date = models.DateField()
    mode = models.CharField(max_length=50)
    created_by = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    status = models.IntegerField(default=0)

    joining_chance = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_seen_hr = models.BooleanField(default=False)
    is_seen_dm = models.BooleanField(default=False)

    updated_at = models.DateTimeField(null=True, blank=True)
    is_update_notification = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.lead.name} - {self.meet_date}"

class LeadConfused(models.Model):
    lead = models.ForeignKey(Leads, on_delete=models.CASCADE)
    reason = models.TextField(null=True)
    executive_id = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    interview_email_sent = models.BooleanField(default=False)

    def clean(self):
        super().clean()
        from .validators import has_valid_email_or_phone
        if not self.lead or not has_valid_email_or_phone(self.lead):
            raise ValidationError("Add an email or a phone number before marking this lead as confused")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    

class TargetAction(models.Model):
    company = models.ForeignKey('BusinessRegister_Details', on_delete=models.CASCADE, null=True, blank=True)
    target = models.ForeignKey('TargetAssign', on_delete=models.CASCADE)
    executive = models.ForeignKey('EmployeeRegister_Details',on_delete=models.CASCADE)
    action_taken = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.executive.name} - {self.target.month} {self.target.year}"
    



class MarketingImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='marketing_images/')
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    target_audience = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    call_to_action = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    # NEW: self-referential FK so edited versions point back to the original
    edited_version_of = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='edited_versions',
    )

    def __str__(self):
        return self.title
    


class ImageAnalysis(models.Model):
    marketing_image = models.OneToOneField(MarketingImage, on_delete=models.CASCADE)
    
    # Visual scores (0-100)
    visual_clarity_score = models.IntegerField(default=0)
    color_usage_score = models.IntegerField(default=0)
    layout_score = models.IntegerField(default=0)
    balance_score = models.IntegerField(default=0)
    visual_overall_score = models.IntegerField(default=0)
    
    # Marketing scores (0-100)
    brand_consistency_score = models.IntegerField(default=0)
    message_clarity_score = models.IntegerField(default=0)
    visual_hierarchy_score = models.IntegerField(default=0)
    emotional_impact_score = models.IntegerField(default=0)
    conversion_optimization_score = models.IntegerField(default=0)
    audience_relevance_score = models.IntegerField(default=0)
    marketing_overall_score = models.IntegerField(default=0)
    overall_score = models.IntegerField(default=0)
    
    # Strategic insights (original fields)
    marketing_strategy_insights = models.TextField(blank=True)
    competitive_positioning = models.TextField(blank=True)
    psychological_triggers = models.TextField(blank=True)
    cultural_considerations = models.TextField(blank=True)
    platform_optimization = models.TextField(blank=True)
    visual_improvements = models.TextField(blank=True)
    marketing_improvements = models.TextField(blank=True)
    strategic_recommendations = models.TextField(blank=True)
    accessibility_compliance = models.TextField(blank=True)
    legal_considerations = models.TextField(blank=True)
    platform_guidelines = models.TextField(blank=True)
    
    # NEW: Dedicated suggestion fields for comparison
    visual_clarity_suggestion = models.TextField(blank=True)
    font_size_suggestion = models.TextField(blank=True)
    font_style_suggestion = models.TextField(blank=True)
    font_color_suggestion = models.TextField(blank=True)
    text_alignment_suggestion = models.TextField(blank=True)
    background_color_suggestion = models.TextField(blank=True)
    text_visibility_suggestion = models.TextField(blank=True)
    color_harmony_suggestion = models.TextField(blank=True)
    element_placement_suggestion = models.TextField(blank=True)
    text_image_balance_suggestion = models.TextField(blank=True)
    spacing_white_space_suggestion = models.TextField(blank=True)
    
    # NEW: Comparison status fields (for edited images)
    visual_clarity_improved = models.CharField(max_length=20, default='not_analyzed', 
                                              choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    font_size_improved = models.CharField(max_length=20, default='not_analyzed',
                                         choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    font_style_improved = models.CharField(max_length=20, default='not_analyzed',
                                          choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    font_color_improved = models.CharField(max_length=20, default='not_analyzed',
                                          choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    text_alignment_improved = models.CharField(max_length=20, default='not_analyzed',
                                               choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    background_color_improved = models.CharField(max_length=20, default='not_analyzed',
                                                choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    text_visibility_improved = models.CharField(max_length=20, default='not_analyzed',
                                                choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    color_harmony_improved = models.CharField(max_length=20, default='not_analyzed',
                                             choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    element_placement_improved = models.CharField(max_length=20, default='not_analyzed',
                                                choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    text_image_balance_improved = models.CharField(max_length=20, default='not_analyzed',
                                                  choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    spacing_white_space_improved = models.CharField(max_length=20, default='not_analyzed',
                                                   choices=[('not_analyzed', 'Not Analyzed'), ('yes', 'Yes'), ('no', 'No'), ('partial', 'Partial')])
    
    # Metadata
    analysis_duration = models.FloatField(null=True, blank=True)
    llm_tokens_used = models.IntegerField(null=True, blank=True)
    poster_concept_prompt = models.TextField(blank=True)  # NEW: Store generated poster concept
    design_improvement_prompt = models.TextField(blank=True)  # NEW: Store design-only prompt
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.marketing_image.title}"
        
class EmployeeAttendance(models.Model):
    employee = models.ForeignKey(
        EmployeeRegister_Details,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    first_login_time = models.DateTimeField(
        null=True,
        blank=True
    )

    last_logout_time = models.DateTimeField(
        null=True,
        blank=True
    )

    total_working_hours = models.DurationField(
        default=timedelta
    )
    

class EmployeeSession(models.Model):
    employee = models.ForeignKey(
        EmployeeRegister_Details,
        on_delete=models.CASCADE
    )

    attendance = models.ForeignKey(
        EmployeeAttendance,
        on_delete=models.CASCADE
    )

    login_time = models.DateTimeField()

    logout_time = models.DateTimeField(
        null=True,
        blank=True
    )

    duration = models.DurationField(
        null=True,
        blank=True
    )




class Candidate(models.Model):
    user = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    year_of_pass_out = models.CharField(max_length=50, null=True, blank=True)
    job_role = models.CharField(max_length=255, null=True, blank=True)
    
    # Can be DateField or CharField; sticking to CharField for easier initial parsing matching
    internship_start_date = models.CharField(max_length=100, null=True, blank=True)
    internship_end_date = models.CharField(max_length=100, null=True, blank=True)
    internship_topic = models.CharField(max_length=255, null=True, blank=True)
    
    work_experience = models.TextField(null=True, blank=True)
    
    # System Tracking fields
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    processed_to_sheets = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


class ProcessedEmail(models.Model):
    user = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    message_id = models.CharField(max_length=255)
    subject = models.CharField(max_length=500, null=True, blank=True)
    sender = models.EmailField(null=True, blank=True)
    date_received = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='SUCCESS') # 'SUCCESS', 'FAILED'
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.message_id

class UserCredentials(models.Model):
    user = models.OneToOneField(EmployeeRegister_Details, on_delete=models.CASCADE)
    
    # IMAP Configuration
    imap_server = models.CharField(max_length=255, blank=True, null=True)
    imap_email = models.CharField(max_length=255, blank=True, null=True)
    imap_password = models.CharField(max_length=255, blank=True, null=True)
    
    # API Configurations
    groq_api_key = models.CharField(max_length=255, blank=True, null=True)
    
    # Google Sheets Configuration
    google_credentials_json = models.TextField(blank=True, null=True)
    spreadsheet_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.name}'s Credentials"
    

class BottleAdd(models.Model):

    name = models.CharField(max_length=255, blank=True, null=True, default='')
    created_by = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Bottle"
    

from django.utils import timezone

class KeywordConfig(models.Model):
    """Configurable keyword list managed via admin."""
    keyword = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword

    class Meta:
        ordering = ['keyword']
        verbose_name = 'Keyword'
        verbose_name_plural = 'Keywords'


class AudioRecord(models.Model):
    """Stores uploaded audio files and their processing results."""



    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    # File info
    caller_name = models.CharField(max_length=200, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    audio_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)  # bytes

    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    # AI Results
    transcript = models.TextField(blank=True, default='')
    detected_keywords = models.JSONField(default=list, blank=True)
    career_bucket = models.ForeignKey(BottleAdd, on_delete=models.CASCADE, null=True, blank=True)
    classification_reason = models.TextField(blank=True, default='')
    confidence_score = models.FloatField(default=0.0)

    # Error tracking
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        name = self.caller_name or self.file_name or f"Record #{self.pk}"
        bucket = self.career_bucket.name if self.career_bucket else "No Bottle"
        return f"{name} — {bucket}"

    @property
    def keyword_count(self):
        return len(self.detected_keywords)

    @property
    def total_keyword_hits(self):
        """Total number of keyword occurrences across all keywords."""
        if not self.detected_keywords:
            return 0
        if isinstance(self.detected_keywords[0], dict):
            return sum(k.get('count', 1) for k in self.detected_keywords)
        return len(self.detected_keywords)

    @property
    def has_keywords(self):
        return self.keyword_count > 0

    @property
    def file_size_display(self):
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        return f"{self.file_size / (1024*1024):.1f} MB"

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Audio Record'
        verbose_name_plural = 'Audio Records'
        
class GoogleFormApplication(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    source = models.CharField(max_length=255, blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    year_of_passout = models.CharField(max_length=10, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    applied_for = models.CharField(max_length=255, blank=True, null=True)

    done_any_internship = models.CharField(max_length=10, blank=True, null=True)

    internship_startdate = models.DateField(blank=True, null=True)
    internship_enddate = models.DateField(blank=True, null=True)

    experience = models.TextField(blank=True, null=True)

    # Email account connected to the Google Form
    google_form_owner_email = models.EmailField(blank=True, null=True)

    employee = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    transferred_status = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

class ExecutiveGoogleForm(models.Model):
    employee = models.ForeignKey(EmployeeRegister_Details, on_delete=models.CASCADE)
    credentials_file = models.FileField(upload_to='google_credentials/')
    sheet_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.employee.name
