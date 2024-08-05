import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def sendmail():
    sender_email = "testid141203@gmail.com"
    sender_password = "bdcd dodb gmke gmmr"


    recipient_email = "adithya0420@gmail.com"


    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "test"


    body = "This is the body of the test email."
    message.attach(MIMEText(body, "plain"))

    
    excel_file_path = "data.xlsx"
    attachment = open(excel_file_path, "rb")
    part = MIMEApplication(attachment.read(), Name="data.xlsx")
    attachment.close()
    part["Content-Disposition"] = f'attachment; filename="{excel_file_path}"'
    message.attach(part)

    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        
        server.starttls()

        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

    print("Email with attachment sent successfully.")
