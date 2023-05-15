import json
import smtplib, os
from email.message import EmailMessage


def notification(message):
    """
    Using https://www.wpoven.com/tools/free-smtp-server-for-testing#
    """
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        sender_address = os.environ.get("MAIL_ADDRESS")

        receiver_address = message["username"]
        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
        msg["Subject"] = "MP3 Download"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP("smtp.freesmtpservers.com", 25)
        # session.starttls()
        # session.login(sender_address, sender_password)
        session.send_message(msg, sender_address, receiver_address)
        session.quit()
        print("Mail sent")
    except Exception as err:
        print(err)
        return f"Internal error {err}", 500
