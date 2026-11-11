#DMCORE with buffer


from django.urls import path,re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

urlpatterns = [
    path('', views.home, name='home'),  # example view
    path('compsignup',views.compsignup),
    path('registerbusiness', views.registerbusiness, name='registerbusiness'),
    path('login',views.login,name='login'),
    path('check-email/', views.check_email, name='check_email'),
    path('check-company-id/', views.check_company_id, name='check_company_id'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('dmhead',views.dmhead,),
    path('teamlead',views.teamlead),
    path('executive',views.executive),
    path('manager',views.manager,name='manager'),
    path('telecaller',views.telecaller, name="telecaller"),
    
    path('departments',views.departments,name='departments'),
    path('departments/edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path('view_designations',views.view_designations,name='view_designations'),
    path('designation/edit/<int:designation_id>/', views.edit_designation, name='edit_designation'),
    path('designation/delete/<int:designation_id>/', views.delete_designation, name='delete_designation'),
    path('empsignup',views.empsignup,name='empsignup'),
    path('ajax/load-departments/', views.ajax_load_departments, name='ajax_load_departments'),
    path('ajax/load-designations/', views.ajax_load_designations, name='ajax_load_designations'),
    path('validate-email/', views.validate_email, name='validate_email'),
    path('login_requests',views.login_requests,name='login_requests'),
    path('accept-user/<int:login_id>/', views.accept_user, name='accept_user'),
    path('decline-user/<int:login_id>/', views.decline_user, name='decline_user'),
    
    path('employees',views.employees,name='employees'),
    path('view_employees',views.view_employees,name='view_employees'),
    path('update_designation/<int:emp_id>/', views.update_designation, name='update_designation'),
    path('assign_team_lead',views.assign_team_lead,name='assign_team_lead'),
    path('show_reallocation_page',views.show_reallocation_page,name='show_reallocation_page'),
    path('reallocate_executives',views.reallocate_executives,name='reallocate_executives'),
    path('feedbacks',views.feedbacks,name='feedbacks'),
    path('Leave',views.Leave,name='Leave'),
    path('schedules',views.schedules,name='schedules'),
    path('actiontaken',views.actiontaken,name='actiontaken'),
    path('complaint',views.complaint,name='complaint'),
    path('dm/works',views.dm_works,name='dm_works'),
    path('resigned-employees/', views.resigned_employees_list, name='resigned_employees_list'),
    
    ##executive##
    path('schedule',views.schedule,name='schedule'),
    path('add-schedule/', views.add_employee_schedule, name='add_employee_schedule'),
    path('edit-schedule/<int:schedule_id>/', views.edit_employee_schedule, name='edit_employee_schedule'),
    path('edit_schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('update-schedule-status/', views.update_schedule_status, name='update_schedule_status'),
    path('leave_apply/',views.leave_apply, name='leave_apply'),
    path('schedule/delete/<int:pk>/', views.delete_employee_schedule, name='delete_employee_schedule'),
    
    path('executive_action_taken/',views.executive_action_taken,name='executive_action_taken'),
    path('executive_feedback',views.executive_feedback,name='executive_feedback'),
    path('executive_add_feedback/',views.executive_add_feedback,name='executive_add_feedback'),
    path('executive_complaints/',views.executive_complaints,name='executive_complaints'),
    path('executive_add_complaints/',views.executive_add_complaints,name='executive_add_complaints'),
    
    path('emp_works/', views.emp_works, name='emp_works'),
    path('emp_new_works/', views.emp_new_works, name='emp_new_works'),
    path('accept-task/<int:task_id>/', views.accept_task, name='accept_task'),
    path('emp_ongoing_works/', views.emp_ongoing_works, name='emp_ongoing_works'),
    path('save-daily-work/', views.save_daily_work, name='save_daily_work'),
    path('emp_completed_works/', views.emp_completed_works, name='emp_completed_works'),
    path('view_detail_ongoing_works/<int:task_id>/', views.view_detail_ongoing_works, name='view_detail_ongoin_works'),
    path('add_daily_lead_collection/<int:task_id>/', views.add_daily_lead_collection, name='add_daily_lead_collection'),
    path('add_daily_lead_collection_work/<int:task_id>/', views.add_daily_work, name='add_daily_work'),
    path('lead-category/<int:task_id>/', views.lead_cat_view, name='lead_cat'),
    path('lead-list/<int:category_id>/', views.lead_list, name='lead_list'),
    path('leads/remove_duplicates/<int:category_id>/', views.remove_duplicates, name='remove_duplicates'),
    path('leads/download/<int:category_id>/', views.download_leads, name='download_leads'),
    path('leads/upload/<int:category_id>/', views.upload_leads, name='upload_leads'),
    path('leads/delete/<int:lead_id>/', views.delete_lead, name='delete_lead'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    
    #Excecutive End
    
    # ===================================================== DM head =====================================================
    path('work/', views.dm_work, name='dm_work'),

    path('tasks/', views.task_list, name='task_list'),
    path('tasks/delete/<int:task_id>/', views.delete_task_main, name='delete_task_main'),

    path('register-client/', views.register_client, name='register_client'),
    path('delete-client/<int:client_id>/', views.delete_client, name='delete_client'),

    path('register-work/', views.register_work, name='register_work'),
    path('create-work/', views.create_work, name='create_work'),
    path('edit-work/', views.edit_work, name='edit_work'),
    path('delete-work/<int:work_id>/', views.delete_work, name='delete_work'),
    path('edit-task/', views.edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('add-more-task/', views.add_more_task, name='add_more_task'),
    path('add-lead-category/', views.add_lead_category, name='add_lead_category'),
    path('edit-category/', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('fields/<int:work_id>/', views.field_page, name='field_page'),
    path('add-field/', views.add_field, name='add_field'),
    path('edit-field/', views.edit_field, name='edit_field'),
    path('edit-field/', views.edit_field, name='edit_field'),

    # DM head (validations, and data fetch)
    path('check-unique/', views.check_unique_field, name='check_unique_field'),
    path('get-client/<int:client_id>/', views.get_client, name='get_client'),
    path('get-work/<int:work_id>/', views.get_work, name='get_work'),
    path('get-task/<int:task_id>/', views.get_task, name='get_task'),
    path('get-category/<int:category_id>/', views.get_category, name='get_category'),
    path('get-tasks/', views.get_available_tasks, name='get_available_tasks'),
    path('get-field/<int:field_id>/', views.get_field, name='get_field'),
    
    path('allocate-work/', views.allocate_work_page, name='allocate_work_page'),
    path('get-tasks-for-work/<int:work_id>/', views.get_tasks_for_work, name='get_tasks_for_work'),
    path('submit-work-allocation/', views.submit_work_allocation, name='submit_work_allocation'),
    path('add-category-to-work/', views.add_lead_category_to_existing_assignment, name='add_lead_category_to_existing_assignment'),
    path('delete-lead-category/<int:category_id>/', views.delete_lead_category, name='delete_lead_category'),
    path('delete-all-tasks-for-tl/<int:work_id>/<int:tl_id>/', views.delete_all_tasks_for_tl, name='delete_all_tasks_for_tl'),
    path('assign-to-exec/', views.assign_to_exec_page, name='assign_to_exec_page'),
    path('assign-to-executives/', views.assign_to_executives, name='assign_to_executives'),

    path('teamlead-tasks/<int:tl_id>/', views.teamlead_tasks, name='teamlead_tasks'),
    path('update-lead-category/', views.update_lead_category, name='update_lead_category'),
    path('remove-task-from-assignment/', views.remove_task_from_assignment, name='remove_task_from_assignment'),
    
    path('get-lead-categories/<int:assign_id>/', views.get_lead_categories_for_task, name='get_lead_categories_for_task'),
    path('get-teamlead-name/<int:tl_id>/', views.get_teamlead_name, name='get_teamlead_name'),
    path('get-employees-for-tl/<int:tl_id>/', views.get_employees_for_tl, name='get_employees_for_tl'),
    path('get-lead-categories-for-tl-task/<int:assign_id>/', views.get_lead_categories_for_tl_task, name='get_lead_categories_for_tl_task'),
    
    path('dmh_schedule/',views.dmh_schedule,name='dmh_schedule'),
    path('dmh_add_my_schedule/',views.dmh_add_my_schedule,name='dmh_add_my_schedule'),
    path('dmh_update_schedule_status/',views.dmh_update_schedule_status,name='dmh_update_schedule_status'),
    path('dmh_edit_schedule_fun/<int:schedule_id>',views.dmh_edit_schedule_fun,name='dmh_edit_schedule_fun'),
    path('get_schedule_details/<int:schedule_id>/',views.get_schedule_details,name='get_schedule_details'),
    path('dmh_edit_schedule/<int:schedule_id>/',views.dmh_edit_schedule,name='dmh_edit_schedule'),
    path('dmh_delete_schedule/<int:schedule_id>/',views.dmh_delete_schedule,name='dmh_delete_schedule'),
    path('dmh_schedule_search/',views.dmh_schedule_search,name='dmh_schedule_search'),
    path('dmh_employee_schedule/',views.dmh_employee_schedule,name='dmh_employee_schedule'),
    path('dmh_add_employee_schedule/',views.dmh_add_employee_schedule,name='dmh_add_employee_schedule'),
    path('dmh_edit_employee_schedule/<int:schedule_id>/',views.dmh_edit_employee_schedule,name='dmh_edit_employee_schedule'),
    path('get_employee_schedule_details/<int:schedule_id>/',views.get_employee_schedule_details,name='get_employee_schedule_details'),
    path('dmh_delete_employee_schedule/<int:schedule_id>/',views.dmh_delete_employee_schedule,name='dmh_delete_employee_schedule'),
    path('dmh_employee_schedule_search/',views.dmh_employee_schedule_search,name='dmh_employee_schedule_search'),
    path('dmh_employee_schedule_filter_list/',views.dmh_employee_schedule_filter_list,name='dmh_employee_schedule_filter_list'),
    
    path('get-lead-team-alloc-desc/<int:category_id>/<int:assign_id>/', views.get_lead_team_alloc_desc, name='get_lead_team_alloc_desc'),
    path('get-workassign-desc/<int:assign_id>/', views.get_workassign_desc, name='get_workassign_desc'),
    path('get-full-workassign/<int:assign_id>/', views.get_full_workassign, name='get_full_workassign'),
    
    path('list/', views.leave_list, name='myleave'),
    path('apply/', views.apply_leave, name='apply-leave'),
    path('search-leaves/', views.search_leaves, name='search_leaves'),
    path('leave_req/', views.leave_req, name='leave_req'),
    path('approve_leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject_leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('action_take/', views.action_take, name='action_take'),
    path('feedback/', views.feedback, name='feedback'),
    path('dm_complaint/', views.dm_complaint, name='dm_complaint'),
    path('filter/', views.filter_leaves, name='filter_leaves'),
    path('submit-action/', views.submit_action_taken, name='submit_action_taken'),
    path('edit-action/<int:action_id>/', views.edit_action, name='edit_action'),

    path('dmhead/leads/', views.dmhead_leads_page, name='dmhead_leads_page'),
    path('verify-leads/<int:team_alloc_id>/<int:lead_category_id>/', views.verify_leads_page, name='verify_leads_page'),
    path('transfer-leads/', views.head_lead_transfer_page, name='head_lead_transfer_page'),
    path('transferred-leads/', views.transferred_leads_page, name='transferred_leads_page'),

    path('upload-leads-dmhead/', views.upload_leads_excel_dmhead, name='upload_leads_excel_dmhead'),
    path("change-lead-status/", views.change_lead_status, name="change_lead_status"),
    path('download-excel-format/<int:lead_category_id>/', views.download_lead_excel_format, name='download_lead_excel_format'),
    path('transfer-selected-leads/', views.transfer_selected_leads, name='transfer_selected_leads'),
    path("send_lead_pdf_mail/", views.send_lead_pdf_mail, name="send_lead_pdf_mail"),
    path("upload_temp_pdf/", views.upload_temp_pdf, name="upload_temp_pdf"),
    
    path('leads-tracker/', views.leads_tracker_page, name='leads_tracker_page'),
    path('waste-leads-dmhead/', views.waste_leads, name='waste_leads'),
    path('repeated-leads/', views.repeated_leads_page, name='repeated_leads_page'),
    path('lead-reports/', views.lead_reports_page, name='lead_reports_page'),
    path('leads-tracker/fetch/<int:lead_id>/', views.get_lead_tracking_details, name='get_lead_tracking_details'),
    path('delete_repeated_leads/', views.delete_repeated_leads, name='delete_repeated_leads'),

    #! ============  helper functions ==============
    path('dm/works/search/', views.dm_works_search, name='dm_works_search'),
    path('dm/works/<int:work_id>/', views.dm_work_details, name='dm_work_details'),
    path('dm/works/task-details/', views.dm_task_details, name='dm_task_details'),
    path("dm/works/search-multi/", views.dm_works_search_multi, name="dm_works_search_multi"),

    # ===================================================== end DM head =====================================================
    
    path('tl_employees_section/',views.tl_employees_section,name='tl_employees_section'),
    path('tl_employees_view/',views.tl_employees_view,name='tl_employees_view'),
    path('tl_employees_leaves/',views.tl_employees_leaves,name='tl_employees_leaves'),
    path('tl_employees_schedules/',views.tl_employees_schedules,name='tl_employees_schedules'),
    path('tl_employees_action_taken/',views.tl_employees_action_taken,name='tl_employees_action_taken'),
    path('tl_employees_feedback/',views.tl_employees_feedback,name='tl_employees_feedback'),
    path('tl_employees_complaints/',views.tl_employees_complaints,name='tl_employees_complaints'),
    path('tl/employees/work/', views.teamlead_works, name='teamlead_works'),

    #! ============  helper function ==============
    path("TL/work/search/", views.tl_works_search, name="tl_works_search"),
    path("tl/works/search-multi/", views.tl_works_search_multi, name="tl_works_search_multi"),

    
    ##admin_employee##
    path('admin_employee',views.admin_employee,name='admin_employee'),
    path('view_emp',views.view_emp,name='view_emp'),
    path('inactivate-employee/<int:emp_id>/', views.inactivate_employee, name='inactivate_employee'),
    path('employee/verify/<int:emp_id>/', views.verify_employee, name='verify_employee'),
    path('allocations/', views.allocation_view, name='allocation_list'),
    path('employee_leaves/', views.employee_leaves, name='employee_leaves'),
    path('employee_schedules/', views.employee_schedules, name='employee_schedules'),
    path('action_taken/', views.action_taken, name='action_taken'),
    path('employee_feedbacks/', views.employee_feedbacks, name='employee_feedbacks'),
    path('complaints/', views.complaints, name='complaints'),
    
    path('hr_leave/', views.hr_leave, name='hr_leave'),
    path('apply-leave/', views.apply_leavehr, name='apply_leavehr'),
    path('feedback/', views.add_feedbackhr, name='add_feedbackhr'),
    path('add-complaint/', views.add_complaints, name='add_complaints'),
    path('actions/', views.action_list, name='action_list'),
    
    # ===================================================== teamlead =====================================================
    path('TL/work/', views.teamlead_work, name='teamlead_work'),
    path('individual-work/', views.individual_work_main, name='individual_work_main'),
    path('tl-new-works/', views.tl_new_works, name='tl_new_works'),
    path('tl-ongoing-works/', views.tl_ongoing_works, name='tl_ongoing_works'),
    path('tl-daily-work-leads/<int:team_alloc_id>/', views.tl_daily_work_leads, name='tl_daily_work_leads'),
    path('tl_view_daily_work/<int:task_assign_id>/', views.tl_view_daily_work, name='tl_view_daily_work'),
    path('add-daily-work/task/<int:task_assign_id>/', views.add_daily_work_task, name='add_daily_work_task'),
    path('add-daily-work/lead/<int:team_alloc_id>/<int:category_id>/', views.add_daily_work_lead, name='add_daily_work_lead'),
    path('tl-completed-works/', views.tl_completed_works, name='tl_completed_works'),
    path('manage-leads/<int:team_alloc_id>/<int:lead_category_id>/', views.manage_leads_page, name='manage_leads_page'),
    path('add-lead/', views.add_lead_manual, name='add_lead_manual'),
    path('upload-leads/', views.upload_leads_excel, name='upload_leads_excel'),
    path('download_leads_excel/<int:lead_category_id>/<int:team_alloc_id>/', views.download_leads_excel, name='download_leads_excel'),
    
    # fetch calls
    path('tl-get-data-workassign/', views.tl_get_data_workassign, name='tl_get_data_workassign'),
    path('tl-get-data-leadcateogry-teamallocate/', views.tl_get_data_leadcateogry_teamallocate, name='tl_get_data_leadcateogry_teamallocate'),
    path('get-lead-details/<int:lead_id>/', views.get_lead_details, name='get_lead_details'),
    
    # teamlead - Employee schedule
    path('teamlead_employeeschedule',views.teamlead_employeeschedule,name='teamlead_employeeschedule'),
    path('tl_employee_schedule/', views.tl_employee_schedule, name='tl_employee_schedule'),
    path('teamlead_employee_schedule_list', views.teamlead_employee_schedule_list, name='teamlead_employee_schedule_list'),
    path('teamlead_employee_edit_schedule/', views.teamlead_employee_edit_schedule, name='teamlead_employee_edit_schedule'),
    path('teamlead_employee_delete_schedule/<int:schedule_id>/',views.teamlead_employee_delete_schedule, name='teamlead_employee_delete_schedule'),
    path('get_current_day_schedules_teamlead/', views.get_current_day_schedules_teamlead, name='get_current_day_schedules_teamlead'),
    path('teamlead_empschedule_status/', views.teamlead_empschedule_status, name='teamlead_empschedule_status'),

    # teamlead - Leave
    path('teamlead_leave', views.teamlead_leave, name='teamlead_leave'),
    path('teamlead_employee_leave_data/', views.teamlead_employee_leave_data, name='teamlead_employee_leave_data'),
    path('teamlead_apply_leave/', views.teamlead_apply_leave, name='teamlead_apply_leave'),
    path('teamlead_view_leaves/', views.teamlead_view_leaves, name='teamlead_view_leaves'),

    # teamlead - Myschedule
    path('teamlead_myschedule',views.teamlead_myschedule,name='teamlead_myschedule'),
    path('teamlead_myschedule_add/', views.teamlead_myschedule_add, name='teamlead_myschedule_add'),
    path('get_teamlead_schedules/', views.get_teamlead_schedules, name='get_teamlead_schedules'),
    path('get_teamleadschedule_details/', views.get_teamleadschedule_details, name='get_schedule_details'),
    path('update_teamlead_myschedule/', views.update_teamlead_myschedule, name='update_teamlead_myschedule'),
    path('delete_teamlead_myschedule/', views.delete_teamlead_myschedule, name='delete_teamlead_myschedule'),
    path('teamlead_myschedule_status/', views.teamlead_myschedule_status, name='teamlead_myschedule_status'),
    path('get_teamlead_currentday_schedules/', views.get_teamlead_currentday_schedules, name='get_teamlead_currentday_schedules'),

    # teamlead - Messages
    path('teamlead_complaints', views.teamlead_complaints, name='teamlead_complaints'),
    path('teamlead_submit_complaint_action/', views.teamlead_submit_complaint_action, name='teamlead_submit_complaint_action'),
    path('teamlead_view_complaints/', views.teamlead_view_complaints, name='teamlead_view_complaints'),
    path('teamlead_feedback', views.teamlead_feedback, name='teamlead_feedback'),
    path('teamlead_add_feedback/', views.teamlead_add_feedback, name='teamlead_add_feedback'),
    path('teamlead_view_feedback/', views.teamlead_view_feedback, name='teamlead_view_feedback'),

    # teamlead - Action Taken
    path('teamlead_actiontaken', views.teamlead_actiontaken, name='teamlead_actiontaken'),
    path('teamlead_submit_action/',views.teamlead_submit_action, name='teamlead_submit_action'),
    path("teamlead_view_actions/", views.teamlead_view_actions, name="teamlead_view_actions"),
    path('teamlead_received_actions/', views.teamlead_received_actions, name='teamlead_received_actions'),
    path('teamlead_edit_action/', views.teamlead_edit_action, name='teamlead_edit_action'),
    
    path('tl_work_allocate_view',views.tl_work_allocate_view,name='tl_work_allocate_view'),
    path('tl_assign_task_employee/<int:work_id>/',views.tl_assign_task_employee,name='tl_assign_task_employee'),
    path('tl_pending_works_view',views.tl_pending_works_view,name='tl_pending_works_view'),
    path('tl_remove_task/<int:work_id>/',views.tl_remove_task,name='tl_remove_task'),
    path('tl_work_progress',views.tl_work_progress,name='tl_work_progress'),
    path('tl_completed_work',views.tl_completed_work,name='tl_completed_work'),

    # ===================================================== teamlead =====================================================

    
    path('exe_work',views.exe_work,name='exe_work'),
    path('weekly_pro',views.weekly_pro,name='weekly_pro'),
    path('monthly_pro',views.monthly_pro,name='monthly_pro'),
    path('tl_progress',views.tl_progress,name='tl_progress'),
    path('tl_week_pro',views.tl_week_pro,name='tl_week_pro'),
    path('verify_progress/<int:progress_id>/', views.verify_progress, name='verify_progress'),
    path('tl_mon_pro',views.tl_mon_pro,name='tl_mon_pro'),
    path('verify_mon_progress/<int:progress_id>/', views.verify_mon_progress, name='verify_mon_progress'),
    path('dm_week_pro',views.dm_week_pro,name='dm_week_pro'),
    path('dm_week_progress/<int:progress_id>/',views.dm_week_progress,name='dm_week_progress'),
    path('update_work_progress',views.update_work_progress,name='update_work_progress'),
    path('dm_mon_pro',views.dm_mon_pro,name='dm_mon_pro'),
    path('dm_mon_progress/<int:progress_id>/',views.dm_mon_progress,name='dm_mon_progress'),
    path('update_mon_progress',views.update_mon_progress,name='update_mon_progress'),
    
    # ===================================================== Data Manager =====================================================
    # !====================== new 13 june ==================
    path('databank/', views.data_bank_view, name='data_bank_view'),
    path('api/leads/', views.data_bank_leads_api, name='data_bank_leads_api'),
    path('api/leads/<int:pk>/send-interview/', views.send_lead_interview, name='send_lead_interview'),
    path('api/interview/session/', views.InterviewSessionAPIView.as_view(), name='interview_session'),
    path('api/interview/answer/', views.InterviewAnswerAPIView.as_view(), name='interview_answer'),
    path('api/interview/complete/', views.InterviewCompleteAPIView.as_view(), name='interview_complete'),
    path('allocation-leads/', views.allocation_leads_page, name='allocation_leads_page'),
    path('follow-up/', views.follow_up_view, name='follow_up_view'),
    path('hr-telecallers/', views.hr_telecallers_view, name='hr_telecallers_view'),
    path('data-executives/', views.data_executives_view, name='data_executives_view'),
    
    path('get-categories-for-client/<int:client_id>/', views.get_categories_for_client, name='get_categories_for_client'),
    path('get_lead_details/<int:lead_id>/', views.get_lead_details_dm, name='get_lead_details_dm'),
    path('allocate-leads/', views.allocate_leads, name='allocate_leads'),

    path('deallocate-followups/', views.deallocate_followups, name='deallocate_followups'),
    path('add-followup-status/', views.add_followup_status, name='add_followup_status'),
    path('get-followup-statuses/', views.get_followup_statuses, name='get_followup_statuses'),
    path('delete-followup-status/<int:status_id>/', views.delete_followup_status, name='delete_followup_status'),

    # ===================================================== Data Manager =====================================================
    
    # ======================================================== telecaller ========================================================
    # !====================== new 19 june ==================
    path('telecaller/all-leads/', views.telecaller_all_leads, name='telecaller_all_leads'),
    path('telecaller/followups/', views.telecaller_followups_page, name='telecaller_followups_page'),
    path('waste-leads/', views.telecaller_waste_leads, name='telecaller_waste_leads'),
    path('closed-leads/', views.closed_leads_page, name='closed_leads_page'),
    path('telecaller/leads-report/', views.telecaller_leads_report, name='telecaller_leads_report'),

    path('accept-leads/', views.accept_leads, name='accept_leads'),
    path('lead_data_collection_hr/<int:lead_id>/', views.lead_data_collection_hr, name='lead_data_collection_hr'),
    path('get-leads-by-date/', views.get_leads_by_date, name='get_leads_by_date'),
    path('get-lead-details-hr/<int:lead_id>/', views.get_lead_details_hr, name='get_lead_details_hr'),
    path("submit-followup-update/", views.submit_followup_update, name="submit_followup_update"),
    path("get-followup-data/<int:lead_id>/", views.get_followup_data, name="get_followup_data"),
    path("update-lead-status/", views.update_lead_status, name="update_lead_status"),
    path('bulk-update-leads/', views.bulk_update_leads, name='bulk_update_leads'),
    path('recall-lead/<int:lead_id>/', views.recall_lead, name='recall_lead'),
    path('get-all-leads-telecaller/', views.get_all_leads_for_telecaller, name='get_all_leads_telecaller'),

    # ====================================================== end telecaller ======================================================

    path('data_reports',views.data_reports,name='data_reports'),
    path('get_telecaller_stats/<int:telecaller_id>/', views.get_telecaller_stats, name='get_telecaller_stats'),
    path('get_telecaller_dates/<int:telecaller_id>/', views.get_telecaller_dates, name='get_telecaller_dates'),
    path('get_telecaller_stats_by_date/<int:telecaller_id>/<str:selected_date>/', views.get_telecaller_stats_by_date, name='get_telecaller_stats_by_date'),
    path('get_telecaller_leads_by_date/<int:telecaller_id>/<str:selected_date>/', views.get_telecaller_leads_by_date, name='get_telecaller_leads_by_date'),
    path('dm_employees',views.dm_employees,name='dm_employees'),
    path('dm_emp_leads/<int:emp_id>/', views.dm_emp_leads, name='dm_emp_leads'),
    path('dm-delete-lead/<int:lead_id>/', views.dm_delete_lead, name='dm_delete_lead'),
    path('dm_lead_details/<int:assign_id>/', views.dm_lead_details, name='dm_lead_details'),
    path('dm_notification_management',views.dm_notification_management,name='dm_notification_management'),
    path('dm_today_new_lead',views.dm_today_new_lead,name='dm_today_new_lead'),
    path('dm_today_allocated_lead',views.dm_today_allocated_lead,name='dm_today_allocated_lead'),
    path('dm_today_followup',views.dm_today_followup,name='dm_today_followup'),
    
    path('dm_clients',views.dm_clients,name='dm_clients'),
    path('get-lead-categories-dm/<int:client_id>/', views.get_lead_categories_dm, name='get_lead_categories_dm'),
    path('dm_platform',views.dm_platform,name='dm_platform'),
    path("platform/save/", views.save_dm_platform, name="save_dm_platform"),
    path('dm_platform_lead_details',views.dm_platform_lead_details,name='dm_platform_lead_details'),
    path('dm_platform_report',views.dm_platform_report,name='dm_platform_report'),
    path('dm_wastedata',views.dm_wastedata,name='dm_wastedata'),
    path('dm_approved_wastedata',views.dm_approved_wastedata,name='dm_approved_wastedata'),
    path('dm_pending_wastedata',views.dm_pending_wastedata,name='dm_pending_wastedata'),
    path('dm/wastelead/approve/', views.dm_wastelead_approve, name='dm_wastelead_approve'),
    path('dm/wastelead/reject/', views.dm_wastelead_reject, name='dm_wastelead_reject'),
    path('dm_repeat_data',views.dm_repeat_data,name='dm_repeat_data'),
    path('update_repeated_status/', views.update_repeated_status, name='update_repeated_status'),
    path('dm-delete-lead2/<int:lead_id>/', views.dm_delete_lead2, name='dm_delete_lead2'),
    
    path('tl_all_leads',views.tl_all_leads,name='tl_all_leads'),
    path("get-lead-details-tl/<int:lead_id>/", views.get_lead_details_tl, name="get_lead_details_tl"),
    path('export-leads-excel/', views.export_leads_excel, name='export_leads_excel'),
    path('export-leads-pdf/', views.export_leads_pdf, name='export_leads_pdf'),
    path('lead-details/<int:lead_id>/', views.lead_details, name='lead_details'),
    path('tl_waste_leads',views.tl_waste_leads,name='tl_waste_leads'),
    path('tl_leads_tracker',views.tl_leads_tracker,name='tl_leads_tracker'),
    
    path('exec_all_leads',views.exec_all_leads,name='exec_all_leads'),
    path('exec_leads_tracker',views.exec_leads_tracker,name='exec_leads_tracker'),
    path('exec_waste_leads',views.exec_waste_leads,name='exec_waste_leads'),
    
    path('pendingworks',views.pendingworks,name='pendingworks'),
    path('dm_completedwork',views.dm_completedwork,name='dm_completedwork'),
    path('workprogress',views.workprogress,name='workprogress'),
    path('clientworkdetails/<int:pk>',views.clientworkdetails,name='clientworkdetails'),
    path('clienttaskdetails/<int:pk>',views.clienttaskdetails,name='clienttaskdetails'),
    
    path('ad/resigned-employees/', views.admin_resigned_employees_list, name='admin_resigned_employees_list'),
    path("ad/employee/details/", views.admin_employee_details, name="admin_employee_details"),
    path("ad/employee/update/", views.admin_employee_update, name="admin_employee_update"),
    path("ad/works/", views.admin_works, name="admin_works"),
    path("ad/works/counts/", views.admin_works_counts, name="admin_works_counts"),
    # ! admin : Head
    path("ad/works/head/", views.admin_head_works_page, name="admin_head_works_page"),
    path("ad/works/head/api/heads/", views.admin_head_works_heads_api, name="admin_head_works_heads_api"),
    path("ad/works/head/api/clients/", views.admin_head_works_clients_api, name="admin_head_works_clients_api"),
    path("ad/works/head/api/client-works/", views.admin_head_works_client_works_api, name="admin_head_works_client_works_api"),
    path("ad/works/head/api/assigned/", views.admin_head_works_assigned_api, name="admin_head_works_assigned_api"),
    # ! Admin - Team Lead Works
    path("ad/teamlead/works/", views.admin_team_lead_works, name="admin_team_lead_works"),
    path("ad/teamlead/works/assigned/", views.admin_tl_works_assigned, name="admin_tl_works_assigned"),
    path("ad/teamlead/works/ongoing/", views.admin_tl_works_ongoing, name="admin_tl_works_ongoing"),
    path("ad/teamlead/works/completed/", views.admin_tl_works_completed, name="admin_tl_works_completed"),
    path("ad/teamlead/works/daily-details/", views.admin_tl_work_daily_details, name="admin_tl_work_daily_details"),
    # ! Executive works
    path('ad/employees/works/executive/', views.executive_works, name='executive_works'),
    path('ad/employees/works/executive/list/', views.executive_works_list, name='executive_works_list'),
    path('ad/employees/works/executive/daily/', views.executive_daily_works, name='executive_daily_works'),
    # ! Admin - Clients
    path("ad/clients/", views.admin_clients, name="admin_clients"),
    path("ad/clients/new/", views.admin_clients_new, name="admin_clients_new"),
    path("ad/api/clients/new/", views.admin_clients_new_data, name="admin_clients_new_data"),  
    path("ad/clients/ongoing/", views.admin_ongoing_clients_page, name="admin_ongoing_clients_page"),
    path("ad/api/ongoing-clients/dropdown/", views.admin_api_ongoing_clients_dropdown, name="admin_api_ongoing_clients_dropdown"),
    path("ad/api/ongoing-clients/registered-works/", views.admin_api_oc_registered_works, name="admin_api_oc_registered_works"),
    path("ad/api/ongoing-clients/client-tasks/", views.admin_api_oc_client_tasks, name="admin_api_oc_client_tasks"),
    path("ad/api/ongoing-clients/assigned-works/", views.admin_api_oc_assigned_works, name="admin_api_oc_assigned_works"),
    path("ad/api/ongoing-clients/ongoing-works/", views.admin_api_oc_ongoing_works, name="admin_api_oc_ongoing_works"),
    path("ad/api/ongoing-clients/completed-works/", views.admin_api_oc_completed_works, name="admin_api_oc_completed_works"),
    path('ad/clients/completed/', views.admin_completed_clients_page, name='admin_completed_clients_page'),
    path('ad/clients/completed/data/', views.admin_completed_clients_data, name='admin_completed_clients_data'),
    
    path("work/tl-individual/", views.tl_individual_works_page, name="tl_individual_works_page"),
    path("work/tl-individual/data/", views.tl_individual_works_data, name="tl_individual_works_data"),
    path("work/tl-individual/task-details/<int:work_id>/", views.tl_individual_task_details, name="tl_individual_task_details"),
    path("work/tl-individual/work-details/<int:work_id>/", views.tl_individual_work_details, name="tl_individual_work_details"),
    path("work/tl-individual/promotion-details/<int:task_detail_id>/", views.tl_individual_promotion_details, name="tl_individual_promotion_details"),
    path("work/tl-individual/verify/", views.tl_individual_verify_save, name="tl_individual_verify_save"),
    path("work/tl-individual/remove/", views.tl_individual_remove_task, name="tl_individual_remove_task"),
    
    path('admin_databank/',views.admin_databank,name='admin_databank'),
    path('admin_db_leads/',views.admin_db_leads,name='admin_db_leads'),
    path('get-client-data/', views.get_client_related_data, name='get_client_data'),
    path('ajax/get-databank-leads/', views.get_client_databank_leads, name='get_databank_leads'),
    path('admin_db_foolowup_leads/',views.admin_db_foolowup_leads,name='admin_db_foolowup_leads'),
    path('get-followup-leads/', views.get_followup_leads_by_client, name='get_followup_leads'),
    path('followup-lead-details/<int:followup_id>/', views.followup_lead_details, name='followup_lead_details'),
    path('admin_db_waste_leads/',views.admin_db_waste_leads,name='admin_db_waste_leads'),
    path('ajax/get-waste-leads/', views.get_client_waste_leads, name='get_waste_leads'),
    path('databank_platform/',views.databank_platform,name='databank_platform'),
    path('admin_db_platform_lead_details',views.admin_db_platform_lead_details,name='admin_db_platform_lead_details'),
    path('admin_report/',views.admin_report,name='admin_report'),
    path('databank-lead-details/<int:followup_id>/', views.databank_lead_details, name='databank_lead_details'),

    path('admin_hr_analysis/',views.admin_hr_analysis,name='admin_hr_analysis'),
    path('admin_employee_analysis/',views.admin_employee_analysis,name='admin_employee_analysis'),
    path('admin_comparison_analysis/',views.admin_comparison_analysis,name='admin_comparison_analysis'),
    path('analysis_lead_details/<int:followup_id>/',views.analysis_lead_details,name='analysis_lead_details'),
    
    # Admin cards 
    path('admindash_client_details/<int:client_id>/',views.admindash_client_details,name='admindash_client_details'),
    path('admindash_executives/<int:company_id>/<int:client_id>/',views.admindash_executives,name='admindash_executives'),
    path('admindash_telecallers/<int:company_id>/<int:client_id>/',views.admindash_telecallers,name='admindash_telecallers'),
    path('admindash_executive_leads/<int:exec_id>/<int:client_id>/',views.admindash_executive_leads,name='admindash_executive_leads'),
    path('admindash_executive_leads_list/<int:exec_id>/<int:client_id>/',views.admindash_executive_leads_list,name='admindash_executive_leads_list'),
    path('executive_get_lead_details/<int:lead_id>/',views.executive_get_lead_details,name='executive_get_lead_details'),
    path('admindash_telecaller_leads_list/<int:tele_id>/<int:client_id>/',views.admindash_telecaller_leads_list,name='admindash_telecaller_leads_list'),
    path('telecaller_get_lead_details/<int:lead_id>/',views.telecaller_get_lead_details,name='telecaller_get_lead_details'),
    # End Admin cards 

    path('hr',views.hr, name="hr"),
    path('save-meet/', views.save_meet, name='save_meet'),
    path('meeting_details/', views.meeting_details, name='meeting_details'),
    path('meeting_hr/', views.meeting_hr, name='meeting_hr'),
    path('save-meeting-details/', views.save_meeting_details, name='save_meeting_details'),
    path('mark-hr-seen/', views.mark_hr_notifications_seen, name='mark_hr_seen'),
    path('mark-dm-seen/', views.mark_dm_notifications_seen, name='mark_dm_seen'),
    path('dmhead_meetings/',views.dmhead_meetings,name='dmhead_meetings'),
    path('dmhead_leads_meet/<int:emp_id>/',views.dmhead_leads_meet,name='dmhead_leads_meet'),
    
    path('module_unlock_dmhead/',views.module_unlock_dmhead,name='module_unlock_dmhead'),
    path('unlock-employee/<int:id>/', views.unlock_employee_dmhead, name='unlock_employee_dmhead'),
    path('add_target_dmhead/',views.add_target_dmhead,name='add_target_dmhead'),
    path('view_target_dmhead/',views.view_target_dmhead,name='view_target_dmhead'),
    path('add_promtwork_exec/',views.add_promtwork_exec,name='add_promtwork_exec'),
    path('view_promtwork_exec/',views.view_promtwork_exec,name='view_promtwork_exec'),
    path('promotional_works_tl/',views.promotional_works_tl,name='promotional_works_tl'),
    path('update-promotional-status/<int:id>/<int:status>/',views.update_promotional_status,name='update_promotional_status'),
    path('poster_upload_tl/',views.poster_upload_tl,name='poster_upload_tl'),
    path('view_posters_tl/',views.view_posters_tl,name='view_posters_tl'),
    path('poster_upload_exec/',views.poster_upload_exec,name='poster_upload_exec'),
    path('view_posters_exec/',views.view_posters_exec,name='view_posters_exec'),
    path('viewposters_dmhead/',views.viewposters_dmhead,name='viewposters_dmhead'),
    path('update-posters-status/<int:id>/<int:status>/',views.update_posters_status,name='update_posters_status'),
    
    # Admin Cards Balance
    path('admindash_telecaller_leads/<int:telecaller_id>/<int:client_id>/',views.admindash_telecaller_leads,name='admindash_telecaller_leads'),
    path('admindash_telecaller_meet_details/<int:telecaller_id>/<int:client_id>/',views.admindash_telecaller_meet_details,name='admindash_telecaller_meet_details'),
    path('admindash_telecaller_joined_leads/<int:telecaller_id>/<int:client_id>/',views.admindash_telecaller_joined_leads,name='admindash_telecaller_joined_leads'),
    path('excutive_lead_mark_confused/',views.excutive_lead_mark_confused,name='excutive_lead_mark_confused'),
    path('admindash_executive_confused_leads/<int:exec_id>/<int:client_id>/',views.admindash_executive_confused_leads,name='admindash_executive_confused_leads'),
    path('admindash_convert_confused_lead/',views.admindash_convert_confused_lead,name='admindash_convert_confused_lead'),
    path('admindash_leads_report/',views.admindash_leads_report,name='admindash_leads_report'),
    path('admindash_get_lead__report_details/<int:lead_id>/',views.admindash_get_lead__report_details,name='admindash_get_lead__report_details'),
    path('admindash_telecaller_joined_leads_follow_up_details/<int:lead_id>/',views.admindash_telecaller_joined_leads_follow_up_details,name='admindash_telecaller_joined_leads_follow_up_details'),
    # End Admin Cards Balance
    
    path('admin_target_executive/',views.admin_target_executive,name='admin_target_executive'),
    path('get-target-actions/<int:id>/', views.get_target_actions, name='get_target_actions'),
    path('admin_target_telecaller/',views.admin_target_telecaller,name='admin_target_telecaller'),

    path('graphics_designer/',views.graphics_designer,name='graphics_designer'),
    path('image_analysis/',views.image_analysis,name='image_analysis'),
    path('image_analyzer_page/',views.image_analyzer_page,name='image_analyzer_page'),
    path("upload-image/", views.upload_image, name="upload_image"),
    path("analysis-results/<int:image_id>/", views.analysis_results, name="analysis_results"),
    path("retry-analysis/<int:image_id>/", views.retry_analysis, name="retry_analysis"),
    path("api/analyze-image/", views.api_analyze_image, name="api_analyze_image"),
    path("upload-edited/<int:image_id>/", views.upload_edited_image, name="upload_edited_image"),
    path("compare/<int:original_id>/<int:edited_id>/", views.compare_images, name="compare_images"),
    path("image-history/", views.image_history, name="image_history"),
    path("poster/",views.poster,name='poster'),
    path("poster_generator/", views.poster_generator, name="poster_generator"),
    
    path('employee_logout',views.employee_logout,name='employee_logout'),
    path('employee_attendance/',views.employee_attendance,name='employee_attendance'),
    path('exec_attendence/',views.exec_attendence,name='exec_attendence'),
    path('telecaller_attendence/',views.telecaller_attendence,name='telecaller_attendence'),

    path('settings/', views.settings_view, name='settings'),
    path('resume_extract/',views.resume_extract,name='resume_extract'),
    path('trigger-extraction/', views.trigger_resume_processing, name='trigger-extraction'),
    

    path('bottle_add/',views.bottle_add,name='bottle_add'),
    path('bottle_view/',views.bottle_view,name='bottle_view'),
    path('bottle-edit/<int:id>/', views.bottle_edit, name='bottle_edit'),
    path('bottle-delete/<int:id>/', views.bottle_delete, name='bottle_delete'),

    path('upload/', views.upload_audio, name='upload_audio'),
    path('records/', views.records_list, name='records_list'),
    path('records/<int:pk>/', views.record_detail, name='record_detail'),
    path('records/<int:pk>/reprocess/', views.reprocess_record, name='reprocess_record'),
    path('records/<int:pk>/delete/', views.delete_record, name='delete_record'),
    
    path('get-lead-tracker-details/<int:lead_id>/', views.get_lead_tracker_details,name='get_lead_tracker_details'),
    path('tl_work_details_ajax/<int:task_id>/', views.tl_work_details_ajax, name='tl_work_details_ajax'),
    path('verify-task-detail-tl/<int:detail_id>/', views.verify_task_detail_tl, name='verify_task_detail_tl'),

    path('wastelead_confirmation/',views.wastelead_confirmation, name='wastelead_confirmation'),
    path('update-waste-lead/', views.update_waste_lead, name='update_waste_lead'),
    
    path('download-lead-template/<int:category_id>/', views.download_lead_template, name='download_lead_template'),

    path('download-lead-template_tl/<int:team_alloc_id>/',views.download_lead_template_tl, name='download_lead_template_tl'),

    path('google_form_leads_exec/',views.google_form_leads_exec,name='google_form_leads_exec'),
    path('google_form_leads_dmhead/',views.google_form_leads_dmhead,name='google_form_leads_dmhead'),
    path('transfer_google_form_leads/', views.transfer_google_form_leads, name='transfer_google_form_leads'),

    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('logout',views.logout,name='logout'),
    
    path("confirm-excel-duplicates/", views.confirm_excel_duplicates, name="confirm_excel_duplicates"),

    path('get-google-form-lead-details/<int:lead_id>/', views.get_google_form_lead_details, name='get_google_form_lead_details'),
    
    path('Get_Repeated_Leads/<int:id>/', views.Get_Repeated_Leads, name='Get_Repeated_Leads'),
    
    path('remove_duplicate_TL/<int:category_id>/', views.remove_duplicate_TL, name='remove_duplicate_TL'),
    
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
