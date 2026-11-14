from datetime import datetime
from .models import GoogleFormApplication, ExecutiveGoogleForm


import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def get_google_sheet_data(credentials_path, sheet_name):

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        credentials_path,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open(sheet_name)

    rows = spreadsheet.sheet1.get_all_records()

    drive_service = build(
        "drive",
        "v3",
        credentials=creds
    )

    file_info = drive_service.files().get(
        fileId=spreadsheet.id,
        fields="owners"
    ).execute()

    owner_email = None

    if file_info.get("owners"):
        owner_email = file_info["owners"][0].get(
            "emailAddress"
        )

    return rows, owner_email

def import_google_form_data(employee):

    try:
        config = ExecutiveGoogleForm.objects.filter(
            employee=employee
        ).first()

        if not config:
            return

        if not config.credentials_file:
            return

        rows, owner_email = get_google_sheet_data(
            config.credentials_file.path,
            config.sheet_name
        )

        for row in rows:

            start_date = None
            end_date = None

            if row.get("Internship start date"):
                try:
                    start_date = datetime.strptime(
                        str(row.get("Internship start date")),
                        "%m/%d/%Y"
                    ).date()
                except Exception as e:
                    print("Start Date Error:", e)

            if row.get("Internship end date"):
                try:
                    end_date = datetime.strptime(
                        str(row.get("Internship end date")),
                        "%m/%d/%Y"
                    ).date()
                except Exception as e:
                    print("End Date Error:", e)

            GoogleFormApplication.objects.get_or_create(
                employee=employee,
                email=row.get("Email ID"),
                defaults={
                    "name": row.get("Full Name"),
                    "phone": str(row.get("Contact Number")),
                    "source": row.get("How do you know about this oppurtunity?"),
                    "qualification": row.get("Qualification"),
                    "year_of_passout": row.get("Year of passout"),
                    "location": row.get("Your location"),
                    "applied_for": row.get("Applied for"),
                    "done_any_internship": row.get("Have you done any internship ?"),
                    "internship_startdate": start_date,
                    "internship_enddate": end_date,
                    "experience": row.get("Experience If any"),
                    "google_form_owner_email": owner_email,
                }
            )
    except Exception as e:
        print("Google Form Import Error:", str(e))


def import_all_google_forms():

    configs = ExecutiveGoogleForm.objects.all()

    for config in configs:
        try:
            import_google_form_data(config.employee)
        except Exception as e:
            print(e)