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

    def connect_from(self, signal):
        signal.connect(self.trigger)
        self.connections += 1

    def disconnect_from(self, signal):
        signal.disconnect(self.trigger)
        self.connections -= 1

    def compute(self):
        self.computed.emit()

    def list_param_names(self):
        return list(self.params.keys())

    def get_param(self, param):
        return self.params[param]()

    def set_param(self, param, value):
        self.params[param].value = value

    def get_input_names(self):
        return list(self.inputs.keys())

    def get_input(self, input_):
        # return self.inputs[input_]
        if not self.inputs[input_]:
            return None

        node_obj, output = self.inputs[input_]
        # print(self, node_obj, output, node_obj.get_output(output), node_obj.get_output(output)())
        return node_obj.get_output(output)

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
            'directory': None,
            'changed files': None
        }
        self.inputs = {}

    def compute(self):
        self.outputs['directory'] = self.params['directory']
        super().compute()


class Timer(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params['interval'] = Value(5000)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.trigger)

    @Slot()
    def trigger(self):
        self.compute()

    def set_param(self, param, value):
        super().set_param(param, value)
        self.timer.start(self.get_param('interval'))


class Zip(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params['source'] = Value('D:\\dummy')
        self.params['zipfile'] = Value('D:\\temp\\output.zip')
        self.outputs = {
            'zipfile': None
        }
        self.inputs = {
            'source': None,
        }

    def compute(self):
        source = self.get_input('source') or self.params['source']
        zip_file = self.params['zipfile']

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

        self.outputs['zipfile'] = self.params['zipfile']
        super().compute()


class CopyFile(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params['destfile'] = Value('D:\\temp\\dummy.txt')
        self.outputs = {
            'destfile': None
        }
        self.inputs = {
            'source': None,
            'destination': None
        }

    def compute(self):
        import shutil

        source = self.get_input('source')()
        dest = self.get_input('destination') or self.params['destfile']
        print(self.get_input('destination'))
        print(self.params['destfile'])
        shutil.copyfile(source, dest())

        self.outputs['destfile'] = dest

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
        attachments = self.get_input('attachments') or self.params['attachments']
        print(attachments())

        recipients = self.get_input('recipients') or self.params['recipients']
        subject = self.get_input('subject') or self.params['subject']
        message = self.get_input('message') or self.params['message']
        attachments = self.get_input('attachments') or self.params['attachments']

        self.send_mail(
            send_from=self.params['sender'](),
            send_to=recipients(),
            files=attachments(),
            subject=subject(),
            message=message(),
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

        self.outputs = {'items': None}
        self.inputs = {'items': []}

    def compute(self):
        if self.get_input('items'):
            self.params['items'].value = [item() for item in self.get_input('items')]

        super().compute()


class Switch(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.outputs = {'output': None}
        self.inputs = {}

    def compute(self):
        if self.get_input('items'):
            self.params['items'].value = [item() for item in self.get_input('items')]

        super().compute()


class ForEach(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.outputs = {
            'item': None,
            'index': Value(0),
            'limit': Value(0),
        }
        self.inputs = {'items': []}

    def get_input(self, input_):
        if not self.inputs[input_]:
            return []

        return [node_obj.get_output(output) for node_obj, output in self.inputs[input_]]

        # node_obj, output = self.inputs[input_]
        # return node_obj.get_output(output)

    def compute(self):
        count = len(self.get_input('items'))
        for index, item in enumerate(self.get_input('items')):
            self.outputs['item'] = item
            self.outputs['index'].value = index
            self.outputs['index'].value = count
            print(index)
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
    e.set_param('password', '')
    e.set_param('use_tls', True)
    e.inputs['attachments'] = i.get_output('items')

    z.connect_from(d.computed)
    c.connect_from(z.computed)
    e.connect_from(z.computed)
    e.connect_from(i.computed)
    i.connect_from(z.computed)

    d.compute()
