import re
import smtplib
import logging
import socket
import dns.resolver

# try:
#     raw_input
# except NameError:
#     def raw_input(prompt=''):
#         return input(prompt)
from components.utils import ApiLogging


def get_mx_ip(hostname):
    MX_DNS_CACHE = {}
    if hostname not in MX_DNS_CACHE:
        try:

            records = dns.resolver.query(str(hostname), 'MX')
            MX_DNS_CACHE[hostname] = str(records[0].exchange)
            # mxRecord = str(mxRecord)


        except:
            # if e.rcode == 3:  # NXDOMAIN (Non-Existent Domain)
            MX_DNS_CACHE[hostname] = None
            # else:
            #    raise

    return MX_DNS_CACHE


def validate_email(email, check_mx=False, verify=False, debug=False, smtp_timeout=10, sending_email=''):
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
    # Syntax check
    match = re.match(regex, email)
    if match == None:
        ApiLogging.warning('Bad Syntax')
        return False

    if check_mx:

        hostname = email[email.find('@') + 1:]

        mx_hosts = get_mx_ip(hostname)

        if mx_hosts is None:
            return False
        for key in mx_hosts:
            try:
                server = smtplib.SMTP()
                server.set_debuglevel(0)

                # SMTP Conversation
                if mx_hosts[key] is None:
                    return False
                server.connect(mx_hosts[key])

                server.helo(server.local_hostname)
                server.mail(sending_email)
                code, message = server.rcpt(email)
                server.quit()
                if code == 250:

                    return True
                else:

                    return False
            except:
                return False


