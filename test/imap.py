import base64
import datetime
import os
import shutil

from imapclient import IMAPClient
import email

from imapclient.util import to_unicode
from six import iteritems
import mailparser


class CustomImap(IMAPClient):

    def __init__(self, host, ssl=True):
        super().__init__(host, ssl=ssl)

    def fetch_email_messages(self, messages, _class=None):
        """Retrieve messages as Python email Messages.
        *messages* is a list of message IDs to retrieve.
        The optional *_class* is passed to the `email.parser.Parser` that
        generates the Message.
        A dictionary is returned, indexed by message number. Values are
        instances of `email.message.Message` or `email.message.EmailMessage`
        depending on the *_class* used and the version of Python.
        """
        rv = dict()
        i = self.fetch(messages, 'RFC822')
        # print('i: ', i)
        for message_id, content in iteritems(i):
            # print('content: ', content)
            try:
                email_message = email.message_from_bytes(
                    content[b'RFC822'], _class
                )
            except AttributeError:
                # For Python 2.7
                if _class is None:
                    from email.message import Message
                    _class = Message
                email_message = email.message_from_string(
                    to_unicode(content[b'RFC822']), _class
                )
            rv[message_id] = email_message
        return rv


# context manager ensures the session is cleaned up
with CustomImap(host="mail.panizgroup.ir", ssl=False) as client:
    client.login('info@panizgroup.ir', '305400')
    # print(client.list_folders()[0][-1])
    client.select_folder('INBOX')

    # search criteria are passed in a straightforward way
    # (nesting is supported)
    messages = client.search(['ALL'])

    # response = client.fetch(messages, ['RFC822'])
    # import mailparser
    # print(response)
    # mail = mailparser.parse_from_bytes(response)
    # print('mail: ', mail)
    # mail = mailparser.parse_from_file(f)
    # mail = mailparser.parse_from_file_msg(outlook_mail)
    # mail = mailparser.parse_from_file_obj(fp)
    # mail = mailparser.parse_from_string(raw_mail)
    # fetch selectors are passed as a simple list of strings.
    responses = client.fetch_email_messages(messages)
    # print("response: ", response)
    for message_id, data in responses.items():
        message_data = data  # type: email.message.Message
        mail = mailparser.parse_from_string(message_data.as_string())
        # print(mail,mail.text_plain[-1], mail.date_json)
        # filename, payload
        # print(message_data.is_multipart(), message_data.get_payload())
        # if message_data.is_multipart():
        #     print('new message multipart')
        #     for payload in message_data.get_payload():
        # if payload.is_multipart(): ...
        # print(payload.get_payload())
        # else:
        #     print('new message')
        #     print(message_data.get_payload())
    # `response` is keyed by message id and contains parsed,
    # converted response items.
    # for message_id, data in response.items():
    #     print('{id}: {size} bytes, flags={flags}'.format(
    #         id=message_id,
    #         size=data[b'RFC822.SIZE'],
    #         flags=data[b'FLAGS']))
    #     print("item: ", data[b'BODYSTRUCTURE'])


class MailAPI(object):
    DELETED = b'\Deleted'
    SEEN = b'\Seen'
    ANSWERED = b'\Answered'
    FLAGGED = b'\Flagged'
    DRAFT = b'\Draft'
    RECENT = b'\Recent'

    def __init__(self, host, username, password, folder):
        self.client = CustomImap(host=host, ssl=False)
        self.client.login(username, password)
        self.client.select_folder(folder)

    def logout(self):
        self.client.expunge()
        self.client.logout()

    def get(self):
        # production UNSEEN development ALL
        result_emails = []
        messages = self.client.search(['ALL'])
        responses = self.client.fetch_email_messages(messages)
        for message_id, data in responses.items():
            mail = mailparser.parse_from_string(data.as_string())
            path_list = self.save_attachments(mail.attachments)
            result = {
                'subject': mail.subject,
                'message': mail.text_plain[-1],
                'attachments': path_list,
                'date': mail.date
            }

    def save_attachments(self, attachments):
        path_list = []
        for attachment in attachments:
            path = 'attachments/' + str(datetime.datetime.now().microsecond)
            os.makedirs(path, exist_ok=True)
            data = base64.b64decode(attachment['payload'])
            full_path = path + '/' + attachment['filename']
            f = open(full_path, 'wb')
            f.write(data)
            f.close()
            path_list.append(full_path)
        return path_list

    def delete(self, message_ids=list()):
        self.client.set_flags(message_ids, [b'\Deleted'])

    def get_folders(self):
        folders = self.client.list_folders()
        for folder in folders:
            # print(folder[-1])
            pass

    def __del__(self):
        self.logout()
