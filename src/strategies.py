import os
import sys
from dotenv import load_dotenv
import smtplib
import zipfile
from loguru import logger as log
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from abc import ABC, abstractmethod

from cryptography.fernet import Fernet

ENV_FILE = '../.env'
load_dotenv(ENV_FILE)

class Strategy(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError
    

class SendEmail(Strategy):
    def __init__(self, email_address: str, sender_password: str, path: str|None = None):
        self.sender_email = email_address
        self.recipient_email = email_address
        self.sender_password = sender_password
        self.path = path
        
    
    def execute(self, subject: str = "Automated Email", body: str ="Attached file (if any)") -> None:
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


    @staticmethod
    def _zip_path(path: str) -> str:
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


    def _attach_file(self, msg, file_path) -> None:
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"
        maintype, subtype = mime_type.split("/", 1)
        with open(file_path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=Path(file_path).name)
            
        return
    
    
    
class EncryptData(Strategy):
    def __init__(self, file_path: str):
        self.file_path = file_path
        key = eval(self._load_cryptography_key())
        self.cipher = Fernet(key)
    
    
    def execute(self) -> None:
        if self.file_path and os.path.exists(self.file_path):
            zip_path = SendEmail._zip_path(self.file_path)
            with open(zip_path, 'rb') as f:
                data = f.read()
                
            encrypted = self.cipher.encrypt(data)
            encrypted_path = zip_path + '.enc'
            
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted)
                
        return
    
    
    def _load_cryptography_key(self,) -> bytes:
        key = os.getenv('cryptography_key')
        
        if not key:
            log.info('no cryptography key found. Creating one...')
            key = Fernet.generate_key()
            with open(ENV_FILE, 'a') as f:
                f.write(f'\ncryptography_key={repr(key)}')
            log.success('Create new cryptography key')

        return key


class DecryptData(Strategy):
    def __init__(self, file_path: str):
        self.encrypted_path = file_path
        key = eval(self._load_cryptography_key())
        self.cipher = Fernet(key)
        
    
    def execute(self) -> None:
        if not os.path.exists(self.encrypted_path):
            raise FileNotFoundError(f"{self.encrypted_path} not found")

        with open(self.encrypted_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)

        zip_path = self.encrypted_path.replace('.enc', '')
        with open(zip_path, 'wb') as f:
            f.write(decrypted_data)

        extract_path = zip_path.replace('.zip', '')
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_path)

        os.remove(zip_path)

        return 
    
    
    def _load_cryptography_key(self,) -> bytes:
        key = os.getenv('cryptography_key')
        if not key:
            raise ValueError('Cryptography key not found in environment')
        
        return key
        

    
class DeleteData(Strategy):
    def __init__(self):
        pass
    
    
    def execute(self):
        pass