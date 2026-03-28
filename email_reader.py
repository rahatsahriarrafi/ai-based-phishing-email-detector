import imaplib
import email
from email.header import decode_header
import os


def decode_mime_words(s):
    """Decode encoded email headers."""
    decoded_parts = decode_header(s)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def get_email_body(msg):
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in disposition:
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")
    return body.strip()


def fetch_emails(email_address, password, imap_server="imap.gmail.com", num_emails=5):
    """
    Connect to email via IMAP and fetch recent emails.
    Returns a list of dicts with subject, sender, and body.
    """
    emails = []
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")

        # Search for all emails, get the latest N
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("No messages found.")
            return emails

        email_ids = messages[0].split()
        latest_ids = email_ids[-num_emails:]  # Get latest emails

        for eid in reversed(latest_ids):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = decode_mime_words(msg.get("Subject", "(No Subject)"))
            sender = decode_mime_words(msg.get("From", "(Unknown Sender)"))
            body = get_email_body(msg)

            emails.append({
                "subject": subject,
                "sender": sender,
                "body": body[:3000]  # Limit body length for API
            })

        mail.logout()

    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}")
    except Exception as e:
        print(f"Error fetching emails: {e}")

    return emails
