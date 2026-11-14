from celery import shared_task
from .models import Candidate, UserCredentials
from django.contrib.auth.models import User
from .email_service import WebmailIngestionService
from .resume_parser import ResumeParserService
from .google_sheets_service import GoogleSheetsService
import os
from digitalmarketing.models import *

def run_pipeline(user_id=None):
    if user_id is None:
        processed = 0
        for user in User.objects.all():
            if hasattr(user, 'usercredentials'):
                process_new_resumes_for_user(user)
                processed += 1
        return f"Started processing for {processed} configured users"
    else:
        try:
            user = EmployeeRegister_Details.objects.get(id=user_id)
            if hasattr(user, 'usercredentials'):
                return process_new_resumes_for_user(user)
            else:
                return f"No credentials configured for {user.name}"
        except User.DoesNotExist:
            return "User not found"

@shared_task
def process_new_resumes(user_id=None):
    return run_pipeline(user_id)

def process_new_resumes_for_user(user):
    user_creds = user.usercredentials
    
    # Init Services with user_creds
    mail_service = WebmailIngestionService(user_creds)
    parser_service = ResumeParserService(user_creds)
    sheets_service = GoogleSheetsService(user_creds)
    
    # 1. Fetch Resumes
    print(f"Checking for new emails for user: {user.name}...")

    downloaded_files = mail_service.fetch_new_resumes()
    
    if not downloaded_files:
        print("No new resumes found.")
        return "No new resumes found."

    processed_count = 0
    
    for file_info in downloaded_files:
        file_path = file_info['file_path']
        original_filename = file_info['original_filename']
        print(f"Processing downloaded attachment: {original_filename}")
        
        # 2. Extract Data
        extracted_data = parser_service.parse_resume(file_path)
        
        if not extracted_data:
            print(f"Failed to parse resume content from {original_filename}")
            continue

        # AI Verification & Cleaning Pass (transforms meaningless data into meaningful data)
        print("Running AI Verification pass to correct meaningless data...")
        extracted_data = parser_service.verify_and_correct_data(extracted_data)

        email = extracted_data.get('Email ID')
        if not email or email == 'Nil':
            print("Extracted Data did not yield an email candidate string. Skipping database save to prevent constraint failure.")
            continue
            
        # 3. Store locally in Django Database
        candidate, created = Candidate.objects.get_or_create(
            user=user,
            email=email,
            defaults={
                'name': extracted_data.get('Candidate Name', ''),
                'phone': extracted_data.get('Phone Number', ''),
                'location': extracted_data.get('Location', ''),
                'qualification': extracted_data.get('Qualification', ''),
                'year_of_pass_out': extracted_data.get('Year of Pass Out', ''),
                'job_role': extracted_data.get('Job Role Applied For', ''),
                'internship_start_date': extracted_data.get('Internship Start Date', ''),
                'internship_end_date': extracted_data.get('Internship End Date', ''),
                'internship_topic': extracted_data.get('Internship Topic', ''),
                'work_experience': extracted_data.get('Work Experience', ''),
            }
        )
        
        if not created:
            print(f"Candidate {email} already exists for user {user.name}. Might just be a duplicate submission.")
            continue

        # 4. Push to Google Sheets dataset
        print(f"Syncing {email} to Google Sheets...")
        
        # Format list to map row columns (Adjust to your exact sheet mapping!)
        sheet_row_data = [
            candidate.name,
            candidate.email,
            candidate.phone,
            candidate.location,
            candidate.qualification,
            candidate.year_of_pass_out,
            candidate.job_role,
            candidate.internship_start_date,
            candidate.internship_end_date,
            candidate.internship_topic,
            candidate.work_experience,
            str(candidate.created_at)
        ]
        
        sync_success = sheets_service.append_candidate_data(sheet_row_data)
        
        if sync_success:
            candidate.processed_to_sheets = True
            candidate.save()
            print("Synced to Google Sheets Successfully")
        else:
            print("Failed to sync to Google Sheets (Likely missing credentials or target file)")
            
        processed_count += 1
            
    return f"Processed {processed_count} new resumes successfully for {user.name}."
