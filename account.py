"""
account.py
Project Mercury
Yovel Key-Cohen
"""

import random
import time
import encrypt

class Infinity:
    def __int__(self):
        return 2**64
    def __float__(self):
        return 2.0**64
    def __gt__(self, *args):
        return True
    def __ge__(self, *args):
        return True
    def __lt__(self, *args):
        return False
    def __le__(self, *args):
        return False
    def __add__(self, other):
        return 2 ** 64
    def __sub__(self, other):
        return 2 ** 64
    def __mul__(self, other):
        return 2**64
    def __str__(self):
        return '∞'


class Message:
    def __init__(self, subject, msg, sender, recipient):
        self.msg = msg
        self.formal_date = time.strftime('%m/%d/%y<br>%I:%M %p')
        self.sort_date = str(time.time())
        self.id = '%08d' % random.randint(10**8, 10**9-1)
        self.sender = sender
        self.recipient = recipient
        self.subject = subject.replace('+', ' ')

        self.file = open("data/messages/"+self.id+".msg", 'w')
        h = '# ' + self.sender.id + ' -> ' + self.recipient.id + ' | ' + self.formal_date + '\n'
        self.file.write(h + self.msg.replace('+', ' '))
        self.file.close()


class Account:
    def __init__(self, firstname, lastname, username, password, email, id):
        self.id = id
        self._balance = 0
        self.username = username
        self._password = encrypt.encrypt(password, 'c')
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.coalition = 'none'
        self.session_id = 'none'
        self.transaction_history = []
        self.messages = []
        self.sent_messages = []
        self.shell = False
        self.validator = self.get_new_validator()
        self.total_hunts = 0
        self.active_hunts = 0
        self.last_activity = 'Unused'
        self.date_of_creation = time.strftime('%c')
        self.admin = False
        self.blacklisted = False
        self.ip_addresses = set()
        self.settings = {}

    @property
    def password(self):
        return encrypt.decrypt(self._password, 'c')

    @password.setter
    def password(self, val):
        self._password = encrypt.encrypt(val, 'c')


    @property
    def balance(self):
        return self._balance if self.id != '1377' else Infinity()

    @balance.setter
    def balance(self, val):
        self._balance = val

    def pay(self, amt, account):
        if amt <= self.balance:
            account.balance += amt
            if self.id != '1377':
                self.balance -= amt
            account.balance = float('%.2f' % account.balance)
            self.balance = float('%.2f' % self.balance)
            return 0
        else:
            return 1

    @staticmethod
    def get_new_validator():
        s = '%64d' % random.randint(10 ** 64, 10 ** 65 - 1)  # 512-bit validator
        return s

    def get_name(self):
        return self.firstname + ' ' + self.lastname

    def send_message(self, subject, msg, recpt):
        m = Message(subject, msg, self, recpt)
        self.sent_messages.append(m)
        recpt.messages.append(m)

    # Can be used for SID some time
    def compose_validator_string(self):
        return ''.join(list(map(lambda x: str(hex(ord(x) % 16)[2:]), encrypt.encrypt(self.validator, self.last_activity))))


class ShellAccount:
    def __init__(self):
        self.id = None
        self.balance = 0
        self.username = None
        self.password = None
        self.firstname = None
        self.lastname = None
        self.coalition = 'none'
        self.session_id = 'none'
        self.transaction_history = []
        self.shell = True
        self.total_hunts = 0
        self.active_hunts = 0
        self.date_of_creation = 'none'
        self.admin = False
        self.email = 'none'
        self.blacklisted = False
        self.messages = []
        self.ip_addresses = set()
        self.settings = {}
        self.validator = None
