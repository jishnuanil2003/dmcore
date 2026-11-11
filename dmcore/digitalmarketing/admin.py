from django.contrib import admin

from .interview_questions import INTERVIEW_QUESTIONS
from .models import (
    BusinessRegister_Details,
    ClientRegister,
    EmployeeRegister_Details,
    LeadCategory_Register,
    LeadConfused,
    LeadDetails,
    LeadField_Register,
    Leads,
    TaskAssign,
    WorkRegister,
)


@admin.register(LeadField_Register)
class LeadField_RegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'question_id', 'question_display', 'work', 'client')
    list_display_links = ('id', 'name')
    list_editable = ('question_id',)
    list_filter = ('work', 'client')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'add_date', 'add_time')

    @admin.display(description='Mapped Question')
    def question_display(self, obj):
        if obj.question_id is None:
            return 'Not asked'
        return f'{obj.question_id} - {obj.question_label}'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'question_id' and formfield is not None:
            formfield.choices = [('', 'Not asked in interview')] + [
                (qid, f'{qid} - {label}') for qid, _key, label in INTERVIEW_QUESTIONS
            ]
        return formfield


class LeadDetailsInline(admin.TabularInline):
    model = LeadDetails
    extra = 0
    fields = ('field_name', 'field_data')


class LeadConfusedInline(admin.TabularInline):
    model = LeadConfused
    extra = 0
    fields = ('reason', 'executive_id', 'interview_email_sent', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Leads)
class LeadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'contact', 'status', 'client_or_work', 'field_values')
    list_display_links = ('id', 'name')
    list_filter = ('status', 'work', 'work__client', 'lead_category')
    search_fields = ('name', 'email', 'contact')
    readonly_fields = ('id', 'added_date', 'added_time', 'field_values')
    inlines = [LeadDetailsInline, LeadConfusedInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('work__client', 'lead_category__client_task__work__client')
            .prefetch_related('leaddetails_set')
        )

    @admin.display(description='Client / Work')
    def client_or_work(self, obj):
        work = obj.work
        if not work and obj.lead_category and obj.lead_category.client_task:
            work = obj.lead_category.client_task.work
        if work:
            if work.client:
                return f'{work.client} (Work #{work.id})'
            return f'Work #{work.id}'
        if obj.lead_category and obj.lead_category.client_task and obj.lead_category.client_task.client:
            return str(obj.lead_category.client_task.client)
        return '-'

    @admin.display(description='Field Values')
    def field_values(self, obj):
        items = [f'{d.field_name}: {d.field_data}' for d in obj.leaddetails_set.all()]
        return ' | '.join(items) if items else '-'


@admin.register(LeadDetails)
class LeadDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'field_name', 'field_data')
    list_filter = ('field_name',)
    search_fields = ('lead__name', 'lead__email', 'field_name', 'field_data')
    readonly_fields = ('id',)


@admin.register(WorkRegister)
class WorkRegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'company', 'work_progress', 'work_allocate_status', 'work_status', 'work_create_date')
    list_filter = ('company', 'client', 'work_status')
    search_fields = ('client__client_name', 'work_description')
    readonly_fields = ('id', 'work_create_date', 'work_create_time')


@admin.register(ClientRegister)
class ClientRegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'client_business_name', 'client_email_primary', 'client_phone', 'company')
    list_filter = ('company', 'client_status')
    search_fields = ('client_name', 'client_business_name', 'client_email_primary', 'client_phone')
    readonly_fields = ('id', 'client_reg_date', 'client_add_time')


admin.site.register(BusinessRegister_Details)
admin.site.register(EmployeeRegister_Details)
admin.site.register(TaskAssign)
admin.site.register(LeadCategory_Register)
admin.site.register(LeadConfused)
