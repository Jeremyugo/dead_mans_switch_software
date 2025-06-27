import os
import smtplib
import zipfile
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError
    

class SendEmail(Strategy):
    def __init__(self, email_address, sender_password, path=None):
        self.sender_email = email_address
        self.recipient_email = email_address
        self.sender_password = sender_password
        self.path = path
        
    
    def execute(self, subject: str = "Automated Email", body: str ="Attached file (if any)"):
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = self.recipient_email
        msg["Subject"] = subject
        msg.set_content(body)

        zip_path = None
        if self.path and os.path.exists(self.path):
            zip_path = self._zip_path(self.path)
            self._attach_file(msg, zip_path)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.sender_email, self.sender_password)
            smtp.send_message(msg)

        if zip_path and os.path.exists(zip_path):
            os.remove(zip_path)
            
        return

    def _zip_path(self, path):
        zip_name = Path(path).stem + ".zip"
        zip_path = Path.cwd() / zip_name
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(path):
                zipf.write(path, arcname=Path(path).name)
            else:
                for root, _, files in os.walk(path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, start=path)
                        zipf.write(full_path, arcname=arcname)
        return str(zip_path)

    def _attach_file(self, msg, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        maintype, subtype = mime_type.split("/", 1)
        with open(file_path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=Path(file_path).name)
            
        return
    
    
    
class EncryptData(Strategy):
    def __init__(self, ):
        pass
    
    
    def execute(self):
        pass
    
    
    
class DeleteData(Strategy):
    def __init__(self):
        pass
    
    
    def execute(self):
        pass