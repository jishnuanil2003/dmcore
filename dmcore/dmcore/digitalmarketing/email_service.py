import os
import uuid
from datetime import datetime
from imap_tools import MailBox, AND
from django.conf import settings
from .models import ProcessedEmail

class WebmailIngestionService:
    def __init__(self, user_creds):
        self.imap_server = user_creds.imap_server
        self.email_account = user_creds.imap_email
        self.password = user_creds.imap_password
        self.user = user_creds.user
        self.download_dir = os.path.join(settings.BASE_DIR, 'media', 'resumes')
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def fetch_new_resumes(self):
        """
        Connects to IMAP mailbox, searches for unread emails,
        and extracts PDF/DOC/DOCX attachments.
        """
        downloaded_files = []
        
        try:
            with MailBox(self.imap_server).login(self.email_account, self.password, initial_folder='INBOX') as mailbox:
                # Explicitly ensure we are only reading from the INBOX
                mailbox.folder.set('INBOX')
                # Fetch all emails in INBOX (since we check DB for already processed ones)
                for msg in mailbox.fetch(AND(all=True)):
                    # Check if already processed
                    if ProcessedEmail.objects.filter(user=self.user, message_id=msg.uid).exists():
                        continue
                    
                    has_resume = False
                    for att in msg.attachments:
                        ext = os.path.splitext(att.filename.lower())[1]
                        if ext in ['.pdf', '.doc', '.docx']:
                            # Generate safe filename
                            safe_filename = f"{uuid.uuid4().hex}{ext}"
                            file_path = os.path.join(self.download_dir, safe_filename)
                            
                            with open(file_path, 'wb') as f:
                                f.write(att.payload)
                                
                            downloaded_files.append({
                                'file_path': file_path,
                                'original_filename': att.filename,
                                'message_uid': msg.uid,
                                'sender': msg.from_,
                                'date': msg.date
                            })
                            has_resume = True
                            
                    # Mark email as processed in DB
                    if has_resume:
                        ProcessedEmail.objects.create(
                            user=self.user,
                            message_id=msg.uid,
                            subject=msg.subject,
                            sender=msg.from_,
                            date_received=msg.date,
                            status='SUCCESS'
                        )
                    else:
                        ProcessedEmail.objects.create(
                            user=self.user,
                            message_id=msg.uid,
                            subject=msg.subject,
                            sender=msg.from_,
                            date_received=msg.date,
                            status='IGNORED_NO_ATTACHMENT'
                        )
                        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            
        return downloaded_files
