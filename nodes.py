import sys

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt, Slot, Signal


class Value(object):
    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


def list_nodes():
    return [
        'DirChanged',
        'Zip',
        'CopyFile',
        'Email',
        'ItemList'
    ]


class Node(QtCore.QObject):
    computed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params = {}  # private params that dont connect to inputs/outputs
        self.inputs = {}
        self.outputs = {}

        self.connections = 0
        self.count = 0

    @Slot()
    def trigger(self):
        self.compute()
        # self.count += 1
        # if self.count >= self.connections:
        #     self.compute()
        #     self.count = 0

    def connect_from(self, signal):
        signal.connect(self.trigger)
        self.connections += 1

    def disconnect_from(self, signal):
        signal.disconnect(self.trigger)
        self.connections -= 1

    def compute(self):
        print(self, self.count)
        self.computed.emit()

    def list_param_names(self):
        return list(self.params.keys())

    def get_param(self, param):
        return self.param[param]()

    def set_param(self, param, value):
        self.params[param].value = value

    def get_input_names(self):
        return list(self.inputs.keys())

    def get_input(self, output):
        return self.inputs[output]

    def get_output_names(self):
        return list(self.outputs.keys())

    def get_output(self, output):
        return self.outputs[output]


class Parameter(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params['param'] = Value('')
        self.outputs = {
            'value': self.params['param']
        }
        self.inputs = {}


class DirChanged(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params['directory'] = Value('d:\\temp')
        self.outputs = {
            'directory': self.params['directory'],
            'changed files': Value('')
        }
        self.inputs = {}


class Zip(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params['source'] = Value('D:\\dummy')
        self.params['zipfile'] = Value('D:\\temp\\output.zip')
        self.outputs = {
            'zipfile': self.params['zipfile']
        }
        self.inputs = {
            'source': None,
            'zipfile': self.params['zipfile']
        }

    def compute(self):
        source = self.inputs['source'] or self.params['source']
        zip_file = self.inputs['source'] or self.params['zipfile']

        # source = self.inputs['source']()

        from zipfile import ZipFile
        import os
        fullpaths = []
        for root, directories, files in os.walk(source()):
            for filename in files:
                fullpath = os.path.join(root, filename)
                fullpaths.append(fullpath)

        with ZipFile(zip_file(), 'w') as z:
            for fullpath in fullpaths:
                z.write(fullpath)

        super().compute()


class CopyFile(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params['destfile'] = Value('D:\\temp\\dummy.txt')
        self.outputs = {
            'destfile': self.params['destfile']
        }
        self.inputs = {
            'source': None,
            'destination': self.params['destfile']
        }

    def compute(self):
        import shutil

        source = self.inputs['source']()
        dest = self.inputs['destination'] or self.params['destfile']
        shutil.copyfile(source, dest())

        super().compute()


class Email(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sender = Value('')
        self.recipients = Value([])

        self.params = {
            'sender': Value(''),
            'recipients': Value([]),
            'subject': Value(''),
            'message': Value(''),
            'attachments': Value([]),
            'server': Value(''),
            'port': Value(0),
            'username': Value(''),
            'password': Value(''),
            'use_tls': Value(False),
        }
        self.outputs = {
        }
        self.inputs = {
            'recipients': None,
            'subject': None,
            'message': None,
            'attachments': None
        }

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
        attachments = self.inputs['attachments'] or self.params['attachments']
        print(attachments())

        self.send_mail(
            send_from=self.params['sender'](),
            send_to=self.params['recipients'](),
            files=attachments(),
            subject=self.params['subject'](),
            message=self.params['message'](),
            server=self.params['server'](),
            port=self.params['port'](),
            username=self.params['username'](),
            password=self.params['password'](),
            use_tls=self.params['use_tls']()
        )
        super().compute()


class ItemList(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params['items'] = Value([])

        self.outputs = {'items': self.params['items']}
        self.inputs = {'items': []}

    def compute(self):
        if self.inputs['items']:
            self.params['items'].value = [item() for item in self.inputs['items']]

        super().compute()


if __name__ == '__main__':
    d = DirChanged()
    d.set_param('directory', 'D:\\projects\\python\\node2\\tmp\\src')
    z = Zip()
    z.set_param('zipfile', 'D:\\projects\\python\\node2\\tmp\\output.zip')
    z.inputs['source'] = d.get_output('directory')
    c = CopyFile()
    c.set_param('destfile', 'D:\\projects\\python\\node2\\tmp\\output2.zip')
    c.inputs['source'] = z.get_output('zipfile')
    i = ItemList()
    i.inputs['items'].append(z.get_output('zipfile'))
    e = Email()
    e.set_param('sender', 'vicken.mavlian@gmail.com')
    e.set_param('recipients', ['vicken.mavlian@gmail.com'])
    e.set_param('subject', "wicked zip file")
    e.set_param('message', "whats up man, take this file")
    e.set_param('server', "smtp.gmail.com")
    e.set_param('port', 587)
    e.set_param('username', 'vicken.mavlian@gmail.com')
    e.set_param('password', '22 acacia avenue')
    e.set_param('use_tls', True)
    e.inputs['attachments'] = i.get_output('items')

    z.connect_from(d.computed)
    c.connect_from(z.computed)
    e.connect_from(z.computed)
    e.connect_from(i.computed)
    i.connect_from(z.computed)

    d.compute()
