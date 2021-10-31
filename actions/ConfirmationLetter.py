from __future__ import print_function
import os
import re

import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
SCOPES = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/documents','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/gmail.compose']
SERVICE_ACCOUNT_FILE="service_key.json"
class Confirmation():
    cred = None
    cred = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service_docs = build('docs', 'v1', credentials=cred)
    service_sheets = build("sheets", "v4", credentials=cred)
    service_drive = build("drive", "v3", credentials=cred)
    drive_ID=os.environ.get("DRIVE_ID")
    letter_template_ID=os.environ.get("TEMPLATE_ID")
    from_email = os.environ.get("MY_EMAIL")
    my_password=os.environ.get("MY_PASSWORD")
    student_database_ID=os.environ.get("DB_ID")
    student_database = service_sheets.spreadsheets().values().get(spreadsheetId=student_database_ID, range="students database!A1:L13")
    def __init__(self,student_name,student_matric,student_id,letter_address):
        self.student_name=student_name
        self.student_matric=student_matric
        self.student_id=student_id
        self.letter_address=letter_address
    def get_student_detail(self):
        data_columns = self.student_database.get("values")[0]
        data_rows = self.student_database.get("values")[1:]
        df=pd.DataFrame(data=data_rows,columns=data_columns)
        student_detail_frame=df.loc[df["Student ID"]==self.student_matric]
        return student_detail_frame.iloc[0].to_dict()

    def getGender(self,student_detail):
        if (student_detail.get("Sex") == "F"):
            her_or_his = "Her"
            he_or_she = "She"
        else:
            her_or_his = "His"
            he_or_she = "He"
        return her_or_his, he_or_she
    def getCurrentYear(self):
        current_year = datetime.today().year
        current_month = datetime.today().month
        if 1 < current_month or current_month < 8:
            return f"{current_year - 1}/{(current_year)}"
        else:
            return f"{current_year}/{(current_year) + 1}"
    def getCurrentSem(self):
        if (datetime.today().month <= 9):
            current_sem = "I"
        else:
            current_sem = "II"
        return current_sem

    def getExpectedGrad(self,student_detail):
        str_grad_year = student_detail.get("To Be Graduated").split(",")[1]
        if (student_detail.get("To Be Graduated").split(",")[0] == "Sem2"):
            str_grad_sem = "II"
        else:
            str_grad_sem = "I"
        return str_grad_sem, str_grad_year
    def getMaxDur(self,student_detail):
        str_max_year = student_detail.get("Maximum Study Duration").split(",")[1]
        if (student_detail.get("Maximum Study Duration").split(",")[0] == "Sem2"):
            str_max_sem = "II"
        else:
            str_max_sem = "I"
        return str_max_sem, str_max_year

    def getIntake(self,student_detail):
        str_intake_year = student_detail.get("Intake").split(",")[1]
        if (student_detail.get("Intake").split(",")[0] == "Sem2"):
            str_intake_sem = "II"
        else:
            str_intake_sem = "I"
        return str_intake_sem, str_intake_year
    def get_addrress_lines(self):
        postal_regex=re.compile(r"(\d{5,7})")
        add_line_1_regex=re.compile(r"(.*?)")
        state_regex=re.compile(r"([a-zA-Z]{1,2}\d+\s?\d+[a-zA-Z]{1,2}|\D*)")
        for pattern in self.letter_address:
            if add_line_1_regex.fullmatch(pattern):
                add_line_1=pattern
            elif postal_regex.fullmatch(pattern):
                postal_code=pattern
            elif state_regex.fullmatch(pattern):
                state_name=pattern
            else:
                add_line_1,postal_code,state_name=None
        return add_line_1,postal_code,state_name
    def get_sem_number(self,student_detail):
        student_intake_year=student_detail.get("Intake").split(",")[1]
        student_intake_sem=student_detail.get("Intake").split(",")[0]
        current_month=datetime.today().month
        if (student_intake_sem=="Sem2"):
            intake_year=student_intake_year.split("/")[1]
        else:
            intake_year=student_intake_year.split("/")[0]
        if ( 1 < current_month or current_month < 8):
            current_year=datetime.today().year
            current_sem="Sem2"
        else:
            current_year=(datetime.today().year)+1
            current_sem="Sem1"
        if (current_sem!=student_intake_sem):
            student_sem_no=(current_year-intake_year)*2
        else:
            student_sem_no=((current_year-intake_year)+0.5)*2
        return str(student_sem_no)
    def get_merge_field_Values(self, student_detail):
        her_or_his, he_or_she = self.getGender(student_detail)
        grad_sem, grad_year = self.getExpectedGrad(student_detail)
        max_sem, max_year = self.getMaxDur(student_detail)
        intake_sem, intake_year = self.getIntake(student_detail)
        student_current_semester_no=self.get_sem_number(student_detail)
        now = datetime.today()
        st_now = now.strftime("%d %B %Y")
        add_line_1,postal_code,state_name=self.get_addrress_lines()
        return {"Convo": student_detail.get("Convocation"),
                "Credits": str(student_detail.get("Fullfield Credit Hours")),
                "CurrentSem": self.getCurrentSem(),
                "CurrentYear": self.getCurrentYear(),
                "ExpSem": grad_sem,
                "ExpYear": grad_year,
                "HeorShe": he_or_she,
                "hisorher": her_or_his.lower(),
                "HisorHer": her_or_his,
                "Programme": student_detail.get("Programme"),
                "date": st_now,
                "Fullname": student_detail.get("Name of Student"),
                "Passport": student_detail.get("Pass No"),
                "address line 1": add_line_1,
                "address line 2": "",
                "postal-city": postal_code,
                "state-country": state_name,
                "Nationality": student_detail.get("Nationality"),
                "MatricNo": student_detail.get("Student ID"),
                "IntakeSem": intake_sem,
                "IntakeYear": intake_year,
                "MaxSem": max_sem,
                "MaxYear": max_year,
                "CurrentSemNo": student_current_semester_no,
                "cgpa": str(student_detail.get("CGPA"))
                }

    def mapping(self,merge_field={}):
        field_value_list = []
        for key in merge_field:
            json_representation = {
                "replaceAllText": {
                    "containsText": {
                        "text": '{{%s}}' % key,
                        "matchCase": True,
                    },
                    "replaceText": merge_field[key]
                }
            }
            field_value_list.append(json_representation)
        return field_value_list
    def prepare_confirmation_letter(self):
        student_detail=self.get_student_detail()
        merge_field_dict = self.get_merge_field_Values(student_detail)
        requests_body = self.mapping(merge_field_dict)
        new_doc = self.service_drive.files().copy(
            fileId=self.letter_template_ID,
            body={
                'parents': self.drive_ID,
                'name': student_detail.get("Name of Student")
            }

        ).execute()
        self.service_docs.documents().batchUpdate(documentId=new_doc["id"], body={"requests": requests_body}).execute()
        PDF_MIME_TYPE = 'application/pdf'
        byte_string = self.service_drive.files().export(
            fileId=new_doc["id"],
            mimeType=PDF_MIME_TYPE
        ).execute()
        media_object = MediaIoBaseUpload(io.BytesIO(byte_string), mimetype=PDF_MIME_TYPE)
        pdf_file_dict = self.service_drive.files().create(
            media_body=media_object,
            body={
                'parents': [self.drive_ID],
                'name': '{0} (Confirmation Letter).pdf'.format(student_detail.get("Name of Student"))
            }
        ).execute()
        return byte_string,pdf_file_dict
    def send_email(self,student_email):
        byte_string,pdf_file_dict=self.prepare_confirmation_letter()
        confirmation_letter = io.BytesIO(byte_string)
        to_email = student_email
        subject = 'Confirmation Letter'
        body = f'Dear {self.student_name}, \n Here is your requested letter.'
        message = MIMEMultipart()
        message['to'] = to_email
        message['from'] = self.from_email
        message['subject'] = subject
        msg = MIMEText(body)
        message.attach(msg)
        main_type, sub_type = pdf_file_dict['mimeType'].split('/', 1)
        fileName = (pdf_file_dict['name'])
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(confirmation_letter.getvalue())
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=fileName)
        message.attach(msg)
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(self.from_email, self.my_password)
        server.sendmail(self.from_email, to_email, message.as_string())
        server.quit()
