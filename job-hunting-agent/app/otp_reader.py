import os
import imaplib
import email
import re
import time
from email.header import decode_header

def fetch_latest_otp(sender_filter: str = "", timeout_seconds: int = 60) -> str:
    gmail_user = os.getenv("GMAIL_USER_EMAIL")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_pass:
        raise ValueError("GMAIL_USER_EMAIL and GMAIL_APP_PASSWORD must be configured.")

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(gmail_user, gmail_pass)
            mail.select("inbox")

            status, messages = mail.search(None, '(UNSEEN)')
            if status != 'OK':
                time.sleep(5)
                continue

            for num in messages[0].split():
                res, msg_data = mail.fetch(num, '(RFC822)')
                if res != 'OK':
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8", errors="ignore")
                        
                        if sender_filter and sender_filter.lower() not in msg.get("From", "").lower():
                            continue

                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                        otp_match = re.search(r'\b\d{4,6}\b', body) or re.search(r'\b\d{4,6}\b', subject)
                        if otp_match:
                            mail.logout()
                            return otp_match.group(0)

            mail.logout()
        except Exception as e:
            print(f"IMAP error: {e}")
        
        time.sleep(5)
    
    raise TimeoutError("OTP not received within the timeout window.")