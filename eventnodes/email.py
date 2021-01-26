from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, ListParam, BoolParam, PARAM, SUBTYPE_PASSWORD
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class Email(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Email'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='sender', value='vicken.mavlian@gmail.com', pluggable=PARAM | INPUT_PLUG))
        self.params.append(ListParam(name='recipients',
                                     value=[StringParam(name='', value='vicken.mavlian@gmail.com')],
                                     pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='subject', value='test', pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='message', value='cool', pluggable=PARAM | INPUT_PLUG))
        self.params.append(ListParam(name='attachments', value=[], pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='server', value='smtp.gmail.com', pluggable=PARAM | INPUT_PLUG))
        self.params.append(IntParam(name='port', value=587, pluggable=PARAM | INPUT_PLUG))
        self.params.append(StringParam(name='username', value='vicken.mavlian@gmail.com', pluggable=PARAM | INPUT_PLUG))
        self.params.append(
            StringParam(name='password', value='', subtype=SUBTYPE_PASSWORD,
                        pluggable=PARAM | INPUT_PLUG))
        self.params.append(BoolParam(name='use_tls', value=True, pluggable=PARAM | INPUT_PLUG))

    def send_mail(self, send_from, send_to, subject, message, files=[], server="localhost", port=587, username='',
                  password='', use_tls=True):
        import smtplib
        from pathlib import Path
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate
        from email import encoders

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(message))

        for path in files:
            part = MIMEBase('application', "octet-stream")
            with open(path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="{}"'.format(Path(path).name))
            msg.attach(part)

        smtp = smtplib.SMTP(server, port)
        if use_tls:
            smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()

    def compute(self):
        sender = self.get_first_param('sender')
        recipients = self.get_first_param('recipients')
        subject = self.get_first_param('subject')
        message = self.get_first_param('message')
        attachments = self.get_first_param('attachments')
        server = self.get_first_param('server')
        port = self.get_first_param('port')
        username = self.get_first_param('username')
        password = self.get_first_param('password')
        use_tls = self.get_first_param('use_tls')

        self.send_mail(
            send_from=sender(),
            send_to=[i.value for i in recipients()],
            files=[i.value for i in attachments()],
            subject=subject(),
            message=message(),
            server=server(),
            port=port(),
            username=username(),
            password=password(),
            use_tls=use_tls()
        )
        super().compute()