from lib.bootstrapper import *
from lib.boilerplate import *
from lib.server.server import *
from lib.server.log import *
from lib.server.response import *
from lib.account import *
import lib.bootstrapper
import console
import random
import datetime
from threading import Thread
CB = get_account_by_id('1377')

# Base class
class RequestHandler:
    def __init__(self, server, conn, addr, request, response):
        self.conn = conn
        self.addr = addr
        self.request = request
        self.response = response
        self.server = server

    def throwError(self, code, letter):
        self.response.error = self.server.throwError(code, letter, self.request.get_last_page(), self.conn, response=self.response)
        self.server.log.log(self.addr[0], '- Client requested a non-coalition coalition page (like Group() instance)',
                            lvl=Log.ERROR)


    @staticmethod
    def handler(f):
        def wrapper(*args):
            f(*args)
            return args[0].response
        return wrapper

"""
def Part(string):
    return lambda s: s[:len(string)] == string
def Full(string):
    return lambda s: s == string
"""

# Handlers
class HandlerBlank(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.set_status_code(307, location='/home.html')


class HandlerHome(RequestHandler):
    @RequestHandler.handler
    def call(self):
        if self.request.client.id == 'none':
            self.response.attach_file('home.html')
        else:
            self.response.set_status_code(307, location='/news.html')

class HandlerNews(RequestHandler):
    @RequestHandler.handler
    def call(self):
        news = []
        lines = open('conf/news.cfg').read().split('\n')
        c = 0
        for l in lines:
            if l[0] == '-':
                c += 1
                title, img = l[1:].split('/')
                n = """<a href="n-{3}"><div class="story{2}">
                            <div class="dark-overlay"></div>
                            <span class="title">{0}</span>
                            </div></a>""".format(title, img, '-1' if c is 1 else '', title.replace(' ', '-'))
                news.append(n)
        self.response.attach_file('news.html', nb_page='home.html', stories='\n'.join(news))

class HandlerNewsItem(RequestHandler):
    @RequestHandler.handler
    def call(self):
        name = self.request.address[0][2:].replace('-', ' ').lower()
        lines = open('conf/news.cfg').read().split('\n')
        here = False
        title = ''
        text = []
        for l in lines:
            if l[0] == '-':
                t = l[1:].split('/')[0].lower()
                here = t == name
                if here:
                    title = t.title()
            elif here:
                text.append(l)
        text = '\n'.join(list(map(lambda x: '<p>' + x + '</p>', text)))
        self.response.attach_file('story.html', tl=title, tx=text, nb_page='home.html')

class HandlerFAQ(RequestHandler):
    @RequestHandler.handler
    def call(self):
        faq = open("conf/faq_content.cfg", 'r').read().split('\n')
        questions = {}
        q = ''
        for line in faq:
            if line != '':
                if line[0] == '-':
                    l = line[1:].split('/')
                    q = '<h6 id="' + l[1].strip() + '">' + l[0].strip() + "</h6>"
                    questions[q] = ''
                else:
                    questions[q] += '<p>' + line + '</p>'

        faqs = []
        for q in questions:
            faqs.append(q + questions[q])

        self.response.attach_file('faq.html', nb_page='account.html', questions='<br>'.join(faqs))

class HandlerTreaty(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.set_status_code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs')

class HandlerAccount(RequestHandler):
    @RequestHandler.handler
    def call(self):
        account = get_account_by_id(self.request.client.id)
        if not account.shell:
            prog = open('conf/progress.cfg', 'r').read().replace(r'%m%', str(len(accounts) - 3)).split('\n')
            progress = []
            for i in range(len(prog)):
                if (prog[i].strip() + ' ')[0] not in ('#', ' '):
                    progress.append(
                        'disabled' if (not (eval(prog[i].split(':')[1].strip()) >= 1)) and (not self.request.client.admin) else '')
            self.response.attach_file('account.html',
                                 d1=progress[0], d2=progress[1],
                                 d3=progress[2], d4=progress[3],
                                 d5=progress[4])
        else:
            self.response.set_status_code(307, location='/login.html')

class HandlerLogin(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.attach_file('login.html', nb_page="account.html")

class HandlerSignup(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.attach_file('signup.html', nb_page="account.html")

class HandlerPay(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.attach_file('pay.html', nb_page="account.html")

class HandlerTransactionHistory(RequestHandler):
    @RequestHandler.handler
    def call(self):
        cid = self.request.client.id
        acnt = get_account_by_id(cid)
        hist = []
        for item in acnt.transaction_history:
            item = item.split('|')
            #.format(amount, taxed, tid, time.strftime('%X - %x')))
            hist.append('<tr>'+''.join(tuple(map(td_wrap, item)))+'\n</tr>')
        self.response.attach_file('transaction_history.html', nb_page='account.html', history='\n'.join(hist))

class HandlerRegistry(RequestHandler):
    @RequestHandler.handler
    def call(self):
        acnts = []
        for a in sorted(accounts, key=lambda u: u.lastname if not u.admin else u.id):
            acnts.append(
                '<tr>' + td_wrap(a.firstname + ' ' + a.lastname) + td_wrap(a.id) + td_wrap(a.coalition.name) + td_wrap(
                    a.last_activity) + td_wrap(a.date_of_creation) + '\n</tr>')
        self.response.attach_file('registry.html', nb_page='account.html', accounts='\n'.join(acnts))

class HandlerMessages(RequestHandler):
    @RequestHandler.handler
    def call(self):
        messages = []
        for msg in sorted(self.request.client.messages, key=lambda m: -float(m.sort_date)):
            m = '<div onmouseleave="mouseLeave(this)" onmouseover="updateMessage(\'{0}\', this)" class="preview" id="{0}">\n<span class="sender">{1}</span><br>\n<span class="subject">{2}</span>\n<span class="date">{3}</span>\n</div>'.format(
                msg.id,
                msg.sender.get_name(),
                msg.subject.title() if msg.subject else 'No Subject',
                msg.formal_date
            )
            messages.append(m)
        if not messages:
            messages.append('<span class="no-message">Inbox empty...</span>')
        self.response.attach_file('messages.html', nb_page='account.html', messages='\n'.join(messages))

class HandlerProgress(RequestHandler):
    @RequestHandler.handler
    def call(self):
        f = open('conf/progress.cfg', 'r').readlines()
        for l in range(len(f)):
            f[l] = f[l].replace('%m%', str(len(list(filter(lambda a: not a.admin, accounts)))))

        lines = []
        compose = []
        for line in f:
            if line[0].strip() not in ('#', ''):
                lines.append(tuple(map(lambda x: x.strip(), line.split(':'))))

        for line in lines:
            compose.append('<h3>' + line[0] + '</h3>' + '<div class="prog-bar"><div class="{2}" style="width: 0%" id="{3}"><script>move(document.getElementById("{3}"), {0});</script><span class="prog-bar-int-text">{1}</span></div></div><br>'.format(
                str(100*eval(line[1])),
                (line[1] if len(line) == 2 else line[2]) if eval(line[1]) < 1 else "Complete",
                "prog-bar-int" if eval(line[1]) < 1 else "prog-bar-int-comp",
                lines.index(line) + 100
                ))

        self.response.attach_file('progress.html', bars='\n'.join(compose))

class HandlerSettings(RequestHandler):
    @RequestHandler.handler
    def call(self):
        settings = open('conf/client_settings.cfg', 'r').read()
        fields = []
        for line in settings.split('\n'):
            if line != '' and line[0] != '#' and line[:4] != '<br>' and line[:2] != 'h.':
                opts = line.split('|')
                field = "<span class=\"desc-text\">{2}</span><input type=\"{0}\" name=\"{1}\" {3}>".format(*opts)
                fields.append(field)
            elif line[:2] == 'h.':
                fields.append("<h4>{}</h4>".format(line[2:]))
            elif line[:4] == '<br>':
                fields.append('<br>' * int(line[4:]))

        self.response.attach_file('settings.html', settings='<br>\n'.join(fields), nb_page="account.html")

class HandlerCoalitionRedirect(RequestHandler):
    @RequestHandler.handler
    def call(self):
        if not self.request.client.coalition.default:
            self.response.set_status_code(303, location='coalition.html')
        else:
            self.response.set_status_code(303, location='coalition_list.html')

class HandlerCoalitionList(RequestHandler):
    @RequestHandler.handler
    def call(self):
        coalitions = []
        for group in groups:
            if not group.exists:
                continue
            coalitions.append("""<a href="/c/{0}.{7}">
                            <div class="c-listing">
                                <img src="{1}">
                                <div class="white-back"></div>
                                <h4>{2}</h4><br>
                                <p>
                                    Members: {3}<br>
                                    Type: {4}<br>
                                    Created: {5}<br>
                                    Owner: {6}<br>
                                    Coalit. ID: {0}
                                </p>
                            </div>
                        </a>""".format(
                group.cid,
                group.img,
                group.name,
                str(len(group.members)),
                "Guild" if isinstance(group, Guild) else "Coalition",
                group.creation_date,
                group.founder.get_name(),
                'gld' if isinstance(group, Guild) else 'clt' if isinstance(group, Coalition) else 'std'
            ))
        self.response.attach_file('coalition_list.html', groups='\n'.join(coalitions), nb_page='account.html')

class HandlerCoalition(RequestHandler):
    @RequestHandler.handler
    def call(self):
        c = 'clt' if isinstance(self.request.client.coalition, Coalition) else 'gld' if isinstance(self.request.client.coalition, Guild) else 'std'
        self.response.set_status_code(303, location='/c/' + self.request.client.coalition.cid + '.' + c)

class HandlerCreateCoalition(RequestHandler):
    @RequestHandler.handler
    def call(self):
        img_opts = open('conf/clt_img.cfg').read().split('\n')
        opts = ['<option value="{}">{}</option>'.format(*line.split('|')) for line in img_opts]
        self.response.attach_file('create_coalition.html', nb_page='account.html', img_opts='\n'.join(list(opts)))


class HandlerTransferCoalition(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.attach_file('clt_transfer_ownership.html', nb_page='account.html')

class HandlerPayCoalitionMember(RequestHandler):
    @RequestHandler.handler
    def call(self):
        mems = ['<option value="{}">{}</option>'.format(m.id, m.get_name()) for m in self.request.client.coalition.members]
        self.response.attach_file('pay_member.html', nb_page='account.html', clt_balance=self.request.client.coalition.budget,
                             members='\n'.join(mems))

class Handler(RequestHandler):
    @RequestHandler.handler
    def call(self):
        mems = ['<li><input name="kick-mem" value="{}" type="checkbox" style="box-shadow: initial;">{}</li>'.format(m.id, m.get_name()) for m in self.request.client.coalition.members if m is not self.request.client.coalition.owner]
        img_opts = open('conf/clt_img.cfg').read().split('\n')
        opts = ['<option value="{}">{}</option>'.format(*line.split('|')) for line in img_opts]
        self.response.attach_file('edit_coalition.html', nb_page='account.html',
                             i_members='\n'.join(mems),
                             c_name=self.request.client.coalition.name,
                             c_desc=self.request.client.coalition.description,
                             img_opts='\n'.join(list(opts)))

class HandlerCoalitionPool(RequestHandler):
    @RequestHandler.handler
    def call(self):
        c = self.request.client.coalition
        self.response.attach_file('clt_pooladd.html', nb_page='account.html', cpool='%.2f' % c.pool,
                             blc=('%.2f' % ground((self.request.client.balance - (self.request.client.coal_pct_loaned * c.max_pool)), 0)))

class HandlerCoalitionLoan(RequestHandler):
    @RequestHandler.handler
    def call(self):
        c = self.request.client.coalition
        self.response.attach_file('loan.html', nb_page='account.html', ceiling=cap(c.max_pool * c.get_loan_size(), c.pool))

class HandlerCoalitionLoanJS(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.attach_file('loan_view.js', loan_ceiling=self.request.client.coalition.max_pool)

class HandlerHuntList(RequestHandler):
    @RequestHandler.handler
    def call(self):
        l = []
        time_add = lambda start, add: (datetime.datetime.strptime(start, '%x') + datetime.timedelta(days=add)).strftime(
            '%x')
        for h in hunts:
            if not h.complete and not (len(h.participants) / h.max_contributors >= 1):
                l.append("""<a href="h-{4}"><div class="hunt">
                            <img class="hunt-img" src="google_doc.png">
                            <div class="dark-overlay"></div>
                            <div class="dark-bar {5}"></div>
                            <div class="dark-bar dark-bar-2">
                                <span class="title">{0}</span>
                                <span class="title author">Due {3}<br>{1}<br>Participants: {2}</span>
                            </div>
                        </div></a>""".format(
                    h.title,
                    h.creator.get_name(),
                    '{}/{}'.format(len(h.participants + h.completers), h.max_contributors) if not (
                            len(h.participants + h.completers) / h.max_contributors >= 1) else 'FULL',
                    h.due_date,
                    h.id,
                    'red' if (time.strftime('%x') in [time_add(h.due_date, -1), time_add(h.due_date, 0)]) else '',
                ))
        if len(l) == 0:
            t = '<span style="color:#D7D7D7; font-size: 36px">There aren\'t any hunts available!</span>'
        else:
            t = '\n'.join(l)
        self.response.attach_file('hunts.html', hunts=t)

class HandlerHuntCompleteDenied(RequestHandler):
    @RequestHandler.handler
    def call(self):
        n, hid, tid = self.request.address[0].split('-')
        del n
        try:
            hunt = next(h for h in hunts if h.id == hid)
        except StopIteration:
            self.throwError(1, 'd')
            return

        acnt = hunt.participant_ids[tid]
        hunt.completers.remove(acnt)
        hunt.participants.append(acnt)
        self.response.set_status_code(303, location='h-{}'.format(hid))

class HandlerHuntCompleteAccepted(RequestHandler):
    @RequestHandler.handler
    def call(self):
        n, hid, tid = self.request.address[0].split('-')
        del n
        try:
            hunt = next(h for h in hunts if h.id == hid)
        except StopIteration:
            self.throwError(1, 'e')
            return

        acnt = hunt.participant_ids[tid]
        if acnt not in hunt.paid:
            acnt.total_hunts += 1
            hunt.paid.append(acnt)
            tax = hunt.reward * (
            hunt.creator.coalition.tax if not hunt.creator.coalition == acnt.coalition else hunt.creator.coalition.internal_tax)
            amt = hunt.reward - tax
            tid = '22' + str(random.randint(1000000, 10000000))

            record_transaction(self, hunt.creator.id, self.request.client.id, tid, amt, tax)
            CB.pay(amt, acnt)
            acnt.transaction_history.append(hunt.title + ' - reward of &#8354;{0}|&#8354;{1}|{2}|{3}'.format(
                '%.2f' % amt, '%.2f' % tax if tax != 0 else 'EXEMPT', tid, time.strftime('%X - %x')
            ))
            self.request.client.transaction_history.append('(Hunt) &#8354;{0} rewarded to {1}|&#8354;{2}|3{3}|{4}'.format(
                '%.2f' % amt, acnt.get_name(), '%.2f' % tax if tax != 0 else 'EXEMPT', tid, time.strftime('%X - %x')
            ))
            get_account_by_id('0099').transaction_history.append(
                'Tax income of &#8354;{0} from {1} -> {2}|EXEMPT|7{3}|{4}'.format(round(tax, 2), self.request.client.get_name(),
                                                                                  acnt.get_name(), tid,
                                                                                  time.strftime('%X - %x')))
            CB.pay(tax, get_account_by_id('0099'))
            self.response.set_status_code(303, location='h-{}'.format(hid))
        else:
            self.throwError(17, 'a')
            return

class HandlerEditHunt(RequestHandler):
    @RequestHandler.handler
    def call(self):
        hid = self.request.address[0].split('-')[1]
        try:
            hunt = next(h for h in hunts if h.id == hid)
        except StopIteration:
            self.throwError(1, 'e')
            return
        self.response.attach_file('hunt_edit.html', nb_page='hunts.html', hid=hid, name=hunt.title, link=hunt.link,
                             desc=hunt.desc)

class HandlerHuntSubmit(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.attach_file('hunt_submit.html', nb_page='account.html')

class HandlerMarket(RequestHandler):
    @RequestHandler.handler
    def call(self):
        s = ["""<a href="javascript:purchase({0})"><div class="sale">
                            <img src="{1}">
                            <div class="dark-overlay"></div>
                            <div class="product">{2}</div>
                            <div class="price">&#8354;{3}</div>
                        </div></a>""".format(s.id, s.img, s.name, '%.2f' % s.cost) for s in sales if not s.sold]
        self.response.attach_file('market.html', nb_page='account.html',
                             sales='\n'.join(s) if s else '<span class="empty-msg">It\'s an open market!</span>')

class HandlerPostSale(RequestHandler):
    @RequestHandler.handler
    def call(self):
        img_opts = open('conf/clt_img.cfg').read().split('\n')
        opts = ['<option value="{}">{}</option>'.format(*line.split('|')) for line in img_opts]
        self.response.attach_file('post_sale.html', nb_page='account.html', img_opts='\n'.join(list(opts)))

class HandlerMarketJS(RequestHandler):
    @RequestHandler.handler
    def call(self):
        data = ['"{}":["{}", "{}", "{}"]'.format(s.id, s.name, s.cost, s.seller.get_name()) for s in sales]
        self.response.attach_file('market.js', data='{' + ','.join(data) + '}', bal=int(self.request.client.balance))

class HandlerConsolePage(RequestHandler):
    @RequestHandler.handler
    def call(self):
        consoles[self.addr[0]] = console.Console(accounts)
        self.response.attach_file('console.html')


class HandlerLogoutGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.response.add_cookie('client-id', 'none')
        self.response.add_cookie('validator', 'none')
        self.response.set_status_code(303, location='home.html')

class HandlerShutdownGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.server.log.log('Initiating server shutdown...')
        self.server.close()
        lib.bootstrapper.running = False
        lib.bootstrapper.accounts = accounts
        lib.bootstrapper.groups = groups
        save_users()
        exit()

class HandlerShutdownForceGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        lib.bootstrapper.running = False
        exit()

class HandlerHuntButtonGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        try:
            hunt = next(h for h in hunts if h.id == self.request.address[1])
        except StopIteration:
            self.throwError(2, 'b')
            return
        if self.request.client in hunt.participants:  # Complete
            hunt.finish(self.request.client)
            tid = {v: k for k in hunt.participant_ids.keys() for v in hunt.participant_ids.values()}[self.request.client]
            CB.send_message('Hunt: ' + hunt.title,
                            '{} claims that they\'ve completed the objective of {}. \
                            &#x7B;Click here&#x7C;/hp-'.format(self.request.client.get_name(), hunt.title) + hunt.id + '-' + tid + '&#x7D; \
                            to confirm that this is true and send them their reward. &#x7B;Click here&#x7C;/hd-'.format(
                                self.request.client.get_name(), hunt.title) + hunt.id + '-' + tid + '&#x7D;\
                            to refuse them.',
                            hunt.creator)
            self.response.set_status_code(303, location='/h-' + hunt.id)
        elif self.request.client is hunt.creator:  # End
            hunt.end()
            for acnt in hunt.participants + hunt.completers:
                acnt.active_hunts -= 1
            self.response.set_status_code(303, location='/hunts.html')
        else:  # Join
            self.request.client.active_hunts += 1
            hunt.join(self.request.client)
            self.response.set_status_code(303, location='/h-' + hunt.id)

class HandlerMessageDeleteGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        client = get_account_by_id(self.request.address[2])
        try:
            msg = next(m for m in client.messages if m.id == self.request.address[1])
            client.messages.remove(msg)
        except StopIteration:
            self.server.log.log(self.addr[0], '- Client tried to delete non-existant message.')
        self.response.body = "Success"

class HandlerCoalitionDisbandGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        self.request.client.coalition.dismantle(pm_group)
        self.response.set_status_code(303, location='coalitions.html')

class HandlerCollectSalaryGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        tid = '%19d' % random.randint(1, 2 ** 64)
        c = self.request.client.coalition.credit[self.request.client]
        taxed = c * self.request.client.coalition.internal_tax
        c = c - taxed
        self.request.client.transaction_history.append(
            'Guild salary of &#8354;{0}|&#8354;{1}|9{2}|{3}'.format('%.2f' % c, '%.2f' % taxed, tid,
                                                                    time.strftime('%X - %x')))
        f = open('logs/transactions.log', 'at')
        gl = '{0} -> {1}; Cr{2} [-{3}] ({4}) -- {5}\n'.format(self.request.client.coalition.cid, self.request.client.id, '%.2f' % c,
                                                              '%.2f' % taxed, tid, time.strftime('%X - %x'))
        f.write(gl)
        if log_transactions:
            self.server.log.log(self.addr[0], '- Client collected guild salary of', c)
        self.request.client.coalition.get_credit(self.request.client)

class HandlerRequestGroupJoinGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        try:
            coalition = next(i for i in groups if i.cid == self.request.address[1] and i.exists)
        except StopIteration:
            print(self.request.address[1])
            for c in groups:
                print(c.cid)
            return
        if not self.request.client.requested_coalition:
            rid = str(random.randint(10 ** 5, 10 ** 6))
            self.request.client.requested_coalition = True
            f = open('data/clt_join_reqs.dat', 'w')
            f.write('{}|{}|{}'.format(
                self.request.client.id,
                coalition.cid,
                rid
            ))
            f.close()

            get_account_by_id('1377').send_message('Join Coalition Request',
                                                   'Your request to join coalition {} is pending approval by the owner.'.format(
                                                       coalition.cid), self.request.client)
            get_account_by_id('1377').send_message(
                'Join Coalition Request',
                self.request.client.get_name() + ' (' + self.request.client.id + ') requested to join your coalition!\nYou can accept it by going to &#x7B;this link&#x7C;http://' + host + ':' + str(
                    port) + '/accept_request.act/' + rid + '&#x7D;.',
                coalition.owner
            )

            self.response.set_status_code(303, location="/coalitions.html")

class HandlerAcceptGroupJoinGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        data = open('data/clt_join_reqs.dat', 'r').read().split('\n')
        try:
            r = tuple(filter(lambda x: x.split('|')[2] == self.request.address[1], data))[0].split('|')
        except IndexError:
            print("REALLY BAD ERROR")
            self.server.send('Well that didn\'t work!')
            return

        a = get_account_by_id(r[0])
        if a not in tuple(filter(lambda x: x.cid == r[1], groups))[0].members:
            tuple(filter(lambda x: x.cid == r[1], groups))[0].add_member(a)
            get_account_by_id('1377').send_message('Join Coalition Request',
                                                   'Your request to join the coalition was approved! You can access it with the COALITIONS button in your account.',
                                                   get_account_by_id(r[0]))

class HandlerLeaveCoalitionGA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        client = self.request.client
        client.coalition.remove_member(client, pm_group)
        if isinstance(client.coalition, Guild):
            client.coalition.budget += client.coalition.credit[client]
            client.coalition.credit[client] = 0
        self.response.set_status_code(303, location='coalitions.html')

class HandlerMarketPurchase(RequestHandler):
    @RequestHandler.handler
    def call(self):
        id = self.request.address[0][4:].split('.')[0]
        sale = next(s for s in sales if s.id.strip() == id.strip() and not s.sold)
        seller = sale.seller
        buyer = self.request.client
        guild = sale.guild
        tax = sale.cost * seller.coalition.tax

        if buyer.balance < sale.cost:
            self.throwError(18, 'a')
            return
        elif sale.guild != '':
            sale.guild.budget += sale.cost - tax
            buyer.balance -= sale.cost
        else:
            buyer.pay(sale.cost, seller)

        tid = '4' + str(random.randint(10 ** 10, 10 ** 11 - 1))
        CB.pay(tax, get_account_by_id('0099'))
        get_account_by_id('0099').transaction_history.append(
            'Tax income of &#8354;{0} from {1} -> {2}|EXEMPT|{3}|{4}'.format(round(tax, 2), seller.get_name(),
                                                                             buyer.get_name(), tid,
                                                                             time.strftime('%X - %x')))
        buyer.transaction_history.append(
            '&#8354;{0} payed to {1} for {5}|&#8354;{2}|3{3}|{4}'.format(round(sale.cost, 2), buyer.get_name(),
                                                                         round(tax, 2) if tax != 0 else 'EXEMPT', tid,
                                                                         time.strftime('%X - %x'), sale.name))
        seller.transaction_history.append(
            '{1} payed you &#8354;{0} for {5}|&#8354;{2}|3{3}|{4}'.format(round(sale.cost, 2), seller.get_name(),
                                                                          round(tax, 2) if tax != 0 else 'EXEMPT', tid,
                                                                          time.strftime('%X - %x'), sale.name))

        record_transaction(self, buyer.id, seller.id if not guild else guild.id, tid, sale.cost - tax, tax)
        CB.send_message('Sale of ' + sale.name,
                        '{} has purchased your product {}! You may have to physically give them an item.'.format(
                            buyer.get_name(), sale.name), seller)
        CB.send_message('Sale of ' + sale.name,
                        'Here\'s confirmation of your purchase of {} for Cr{}. You can report dishonesty in a Court Appeal if you do not receive your product in a timely manner.'.format(
                            sale.name, sale.cost), buyer)
        sale.sold = True

        self.response.set_status_code(303, location="market.html")


class HandlerGroupViewer(RequestHandler):
    @RequestHandler.handler
    def call(self):
        client = self.request.client
        try:
            id, type = self.request.address[1].split('.')
            othertype = False
        except ValueError:
            othertype = True
        li = lambda x: '<li>' + x + '</li>'

        if not othertype and type == 'clt':
            try:
                coalition = next(i for i in groups if i.cid == id and i.exists)
            except StopIteration:
                self.throwError(1, 'a')
                return

            owner = coalition.owner is client
            member = client.coalition is coalition
            disabled = lambda condition: 'disabled' if condition else ''
            self.response.attach_file('coalition.html',
                                 members='\n'.join(tuple(map(lambda x: li(x.get_name()), coalition.members))),
                                 c_id=coalition.cid,
                                 c_desc=coalition.description,
                                 c_owner=coalition.owner.get_name(),
                                 coalition_name=coalition.name,
                                 pool='%.2f' % coalition.pool,
                                 max_pool='%.2f' % coalition.max_pool,
                                 pct_loan=100 * coalition.get_loan_size(),
                                 amt_loan='%.2f' % float(coalition.get_loan_size() * coalition.max_pool),
                                 pct_client_loan=('%.1f' % (
                                         client.coal_pct_loaned * 100)) if coalition == client.coalition else 'n/a',
                                 amt_client_loan=('%.2f' % (
                                         client.coal_pct_loaned * coalition.max_pool)) if coalition == client.coalition else 'n/a',

                                 disleave='disband_coalition.act' if owner else 'leave_coalition.act',
                                 disleavet='Disband' if owner else 'Leave',
                                 d1=disabled(member),
                                 d2=disabled(not owner),
                                 d3=disabled(not member),
                                 d4=disabled(not member),
                                 d5=disabled(not owner),
                                 d6=disabled(not member or not client.coal_pct_loaned > 0),
                                 nb_page='account.html')
        elif not othertype and type == 'gld':
            try:
                coalition = next(i for i in groups if i.cid == id and i.exists)
            except StopIteration:
                self.throwError(1, 'b')
                return

            owner = coalition.owner is client
            member = client.coalition is coalition
            disabled = lambda condition: 'disabled' if condition else ''
            if len(self.request.address) > 2:
                if self.request.address[2] == 'budget.html':
                    self.response.attach_file('budget.html', nb_page='account.html',
                                         name=coalition.name,
                                         budget=coalition.budget,
                                         credit=coalition.credit[client]
                                         )
                else:
                    self.response.set_status_code(303, location='/' + self.request.address[2])
            else:
                self.response.attach_file('guild.html',
                                     coalition_name=coalition.name,
                                     members='\n'.join(tuple(map(lambda x: li(x.get_name()), coalition.members))),
                                     c_id=coalition.cid,
                                     c_desc=coalition.description,
                                     c_owner=coalition.owner.get_name(),

                                     disleave='disband_coalition.act' if owner else 'leave_coalition.act',
                                     disleavet='Disband' if owner else 'Leave',
                                     d1=disabled(member),
                                     d2=disabled(not owner),
                                     d3=disabled(not member),
                                     d4=disabled(not member),
                                     d5=disabled(not owner),
                                     d6=disabled(not owner),
                                     d7=disabled(not member),
                                     nb_page='account.html')
        elif othertype or type == 'std':
            self.throwError(15, 'a')
            return
        else:
            self.response.set_status_code(303, location='/' + '/'.join(self.request.address[1:]))

class HandlerMessageFetch(RequestHandler):
    @RequestHandler.handler
    def call(self):
        try:
            # Open message, ignore metadata first line
            d = open('data/messages/' + self.request.address[1] + '.msg', 'r').read()
            head = d.split('\n')[0]
            id = head[head.find('->') + 2:head.find(' |')].strip()
            d = '\n'.join(d.split('\n')[1:])
            # Set message to read for account.html message button rendering
            client = get_account_by_id(id)
            try:
                msg = next(m for m in client.messages if m.id == self.request.address[1])
            except StopIteration:
                print('@', [m.id for m in client.messages])
                print('!', client.id)
                print('$', id)
                print('#', self.request.address[1])
                self.server.log.log(self.addr[0], "- SOMETHING VERY BAD HAPPENED IN MESSAGE FETCH")
                return
            msg.read = True

            d = post_to_html_escape(d)

            self.response.body = d
        except FileNotFoundError:
            self.response.body = "|ERR|"
            self.server.log.log(self.addr[0], '- Client requested non-existent message file.', lvl=Log.ERROR)

class HandlerConsoleCommand(RequestHandler):
    @RequestHandler.handler
    def call(self):
        cons = consoles[self.addr[0]]
        command = self.request.address[1]
        args = self.request.address[2].split('-')

        self.response.set_body(cons.call(command, args))


class HandlerLoginPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        usr = self.request.get_post('user')
        pwd = self.request.get_post('pass')
        u = get_account_by_username(usr)

        if not all(self.request.post_values.values()):
            self.throwError(13, 'a')
            return
        elif u.blacklisted or self.addr[0] in open('data/banned_ip.dat').readlines():
            self.throwError(14, 'a')
            return

        try:
            acnt = list(filter(lambda u: u.username == usr and u.password == pwd, accounts))[0]

            self.response.add_cookie('client-id', acnt.id, 'Max-Age=604800')  # 2 weeks
            self.response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

            self.response.set_status_code(303, location='account.html')
            if log_signin: self.server.log.log('Log in:', u.id)
        except IndexError:
            self.throwError(4, 'a')
            return

class HandlerSignupPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        first = self.request.get_post('first')
        last = self.request.get_post('last')
        mail = self.request.get_post('mail')
        usr = self.request.get_post('user')
        pwd = self.request.get_post('pass')
        cpwd = self.request.get_post('cpass')  # confirm password

        if not all(self.request.post_values.values()):
            self.throwError(13, 'b')
            return

        elif not get_account_by_name(first, last).shell:
            self.throwError(8, 'a')
            return

        elif not get_account_by_username(usr).shell:
            self.throwError(9, 'a')
            return

        elif not first + ' ' + last in whitelist:
            self.throwError(10, 'a')
            return

        elif not get_account_by_email(mail):
            self.throwError(12, 'a')
            return

        elif cpwd != pwd:
            self.throwError(7, 'a')
            return

        id = '0000'
        while id in ('1377',) or id[:2] == '00' or not get_account_by_id(id).shell:  # Saving first 100 accounts for admin purposes
            id = '%04d' % random.randint(0, 9999)
            self.server.log.log("New account created with ID", id, "- first name is", first)
        acnt = Account(first, last, usr, pwd, mail, id)
        pm_group.add_member(acnt)
        acnt.signup_data = self.request.post_values
        accounts.append(acnt)

        self.response.add_cookie('client-id', id, 'Max-Age=604800')  # 2 weeks
        self.response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

        self.response.set_status_code(303, location='account.html')
        if log_signup: self.server.log.log('Sign up:', acnt.get_name(), acnt.id)

class HandlerTransactionPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        if not all(self.request.post_values.values()):
            self.throwError(13, 'c')
            return
        elif get_account_by_id(self.request.get_post('recp')).blacklisted:
            self.throwError(14, 'b')
            return

        recipient_id = self.request.get_post('recp')
        try:
            amount = int(self.request.get_post('amt'))
        except ValueError:
            amount = float(self.request.get_post('amt'))
        recipient_acnt = get_account_by_id(recipient_id)
        if recipient_acnt.shell:
            self.throwError(6, 'a')
            return
        a = self.request.client
        ar = recipient_acnt
        tax = a.coalition.internal_tax if a.coalition == ar.coalition else a.coalition.tax
        taxed = tax * amount
        amount -= taxed

        if not a.pay(amount, recipient_acnt):
            self.response.set_status_code(303, location='account.html')
            tid = '%19d' % random.randint(1, 2 ** 64)
            record_transaction(self, a, ar, tid, amount, taxed, log_transactions)
            a.transaction_history.append(
                '&#8354;{0} sent to {1}|&#8354;{2}|3{3}|{4}'.format('%.2f' % amount, ar.get_name(),
                                                                    '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid,
                                                                    time.strftime('%X - %x')))
            if a.id != '1377':
                ar.transaction_history.append(
                    '{0} sent you &#8354;{1}|&#8354;{2}|2{3}|{4}'.format(a.get_name(), '%.2f' % amount,
                                                                         '%.2f' % taxed if taxed != 0 else 'EXEMPT',
                                                                         tid, time.strftime('%X - %x')))
            else:
                ar.transaction_history.append('CB income of &#8354;{0}|&#8354;{1}|7{2}|{3}'.format('%.2f' % amount,
                                                                                                   '%.2f' % taxed if taxed != 0 else 'EXEMPT',
                                                                                                   tid,
                                                                                                   time.strftime(
                                                                                                       '%X - %x')))
            ar.pay(float(taxed), get_account_by_id('0099'))
            get_account_by_id('0099').transaction_history.append(
                'Tax income of &#8354;{0} from {1} -> {2}|EXEMPT|7{3}|{4}'.format('%.2f' % taxed, a.get_name(),
                                                                                  ar.get_name(), tid,
                                                                                  time.strftime('%X - %x')))
        else:
            self.throwError(3, 'a')
            return

class HandlerMessagePA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        if not all(self.request.post_values.values()):
            self.throwError(13, 'd')
            return

        elif get_account_by_id(self.request.get_post('recp')).blacklisted:
            self.throwError(14, 'c')
            return

        recipient = get_account_by_id(self.request.get_post('recp'))
        if recipient.shell:
            self.throwError(6, 'b')
            return

        msg = self.request.get_post('msg')
        subject = self.request.get_post('subject')
        self.request.client.send_message(subject, msg, recipient)

        self.response.set_status_code(303, location="messages.html")

class HandlerSaveSettingsPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        old_pwd = self.request.get_post('old-pwd')
        new_pwd = self.request.get_post('new-pwd')
        cnew_pwd = self.request.get_post('cnew-pwd')
        new_usr = self.request.get_post('new-usr')

        # This nall() thing is neat - like XOR but for a list
        if not nall(old_pwd, new_pwd, cnew_pwd) or not nall(new_usr, ):
            self.throwError(13, 'e')
            return

        if old_pwd:
            if new_pwd != cnew_pwd:
                self.throwError(7, 'b')
                return
            if old_pwd == self.request.client.password:
                self.request.client.password = new_pwd
            else:
                self.throwError(4, 'b')
                return

        if new_usr:
            self.request.client.username = new_usr

        self.response.set_status_code(303, location='account.html')

class HandlerCreateCoalitionPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        name = self.request.get_post('name')
        type = self.request.get_post('type')
        img = self.request.get_post('img')
        desc = self.request.get_post('desc')

        if not all(self.request.post_values.values()):
            self.throwError(13, 'f')
            return

        client = self.request.client
        client.coalition.remove_member(client, pm_group)
        if client.coalition.owner == client and client.coalition != pm_group:
            client.coalition.dismantle(pm_group)
        if type == 'c':
            new = Coalition(name, img, client, desc)
        else:
            new = Guild(name, img, client, desc)

        groups.append(new)
        self.response.set_status_code(303, location="coalition.html")

class HandlerTransferOwnershipPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        if not all(self.request.post_values.values()):
            self.throwError(13, 'g')
            return

        target = get_account_by_id(self.request.post_values.get('id'))
        if target == 'none':
            self.throwError(6, 'c')
            return

        if target.coalition is self.request.client.coalition or target.coalition is pm_group:
            self.request.client.coalition.change_owner(target)
        else:
            self.throwError(16, 'a')
            return

        self.response.set_status_code(303, location='coalitions.html')

class HandlerPayCoalitionMemberPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        if not all(self.request.post_values.values()):
            self.throwError(13, 'h')
            return

        target = get_account_by_id(self.request.post_values.get('id'))
        if target == 'none':
            self.throwError(6, 'c')
            return

        self.request.client.coalition.pay_member(float(self.request.post_values.get('amt')), target)
        self.response.set_status_code(303, location='coalitions.html')

class HandlerEditCoalitionPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        request = self.request
        c = request.client.coalition
        if request.post_values.get('name'):
            c.name = request.get_post('name')
        if request.post_values.get('desc'):
            c.description = request.get_post('desc')
        if request.post_values.get('img'):
            c.img = request.get_post('img')
        if request.post_values.get('kick-mem'):
            msg = 'The owner of your coalition decided to kick you out. If you think this was done unfairly, please submit an appeal to the Project Mercury Court. Keep in mind that the coalition is their property, not yours, and not ours.'
            km = request.get_post('kick-mem')
            self.server.log.log('Member kicked from a coalition by {}'.format(request.client.id))
            if isinstance(km, list):
                for mem in km:
                    m = get_account_by_id(mem)
                    c.remove_member(m, pm_group)
                    get_account_by_id('1377').send_message('Coalition Kick', msg, m)
            else:
                m = get_account_by_id(km)
                c.remove_member(m, pm_group)
                get_account_by_id('1377').send_message('Coalition Kick', msg, m)
        self.response.set_status_code(303, location='coalitions.html')

class HandlerCoalitionPoolPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        client = self.request.client
        c = client.coalition
        amt = float(request.get_post('amt'))
        client.transaction_history.append('')
        c.add_to_pool(amt, client)
        tid = random.randint(10 ** 5, 10 ** 6)
        client.transaction_history.append(
            '&#8354;{0} donated to {1}|&#8354;{2}|3{3}|{4}'.format('%.2f' % amt, c.name, 'EXEMPT', tid,
                                                                   time.strftime('%X - %x')))
        record_transaction(self, client.id, c.cid, tid, amt, 0, log_transactions)
        self.response.set_status_code(303, location='coalitions.html')

class HandlerCoalitionLoanPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        c = self.request.client.coalition
        amt = float(self.request.get_post('amt'))
        c.loan(amt, self.request.client)
        self.response.set_status_code(303, location="coalitions.html")

class HandlerEditHuntPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        name = self.request.get_post('name')
        link = self.request.get_post('link')
        desc = self.request.get_post('desc')
        hid = self.request.get_post('hid')
        try:
            hunt = next(h for h in hunts if h.id == hid)
        except StopIteration:
            self.throwError(1, 'f')
            return

        hunt.title = name.replace('+', ' ')
        hunt.link = link.replace('+', ' ')
        hunt.desc = desc.replace('+', ' ')

        self.response.set_status_code(303, location='h-' + hid)

class HandlerSubmitHuntPA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        name = self.request.get_post('name')
        link = self.request.get_post('link')
        if link[:4] != 'http':
            link = 'https://' + link
        desc = self.request.get_post('desc')
        due = self.request.get_post('due').split('-')
        due = due[1] + '/' + due[2] + '/' + due[0][2:]
        print(due)
        contributors = self.request.get_post('cntrb')
        reward = self.request.get_post('reward')

        h = Hunt(self.request.client, name, desc, due, int(contributors), float(reward), link)
        self.request.client.my_hunts.append(h)
        hunts.append(h)
        self.response.set_status_code(303, location='h-' + h.id)

class HandlerPostSalePA(RequestHandler):
    @RequestHandler.handler
    def call(self):
        request = self.request
        client = request.client
        name = request.get_post('name')
        price = float(request.get_post('price'))
        img = request.get_post('img')
        guild = request.get_post('guild')

        s = Sale(client, price, name, img)
        s.guild = '' if not guild or not isinstance(client.coalition, Guild) else client.coalition
        client.my_sales.append(s)
        sales.append(s)
        self.response.set_status_code(303, location='market.html')


GET = {
    '': HandlerBlank,
    'home.html': HandlerHome,
}

POST = {

}