"""sendmail email backend class."""

import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from subprocess import Popen,PIPE

class EmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self._lock = threading.RLock()

    def open(self):
        return True

    def close(self):
        pass

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        self._lock.acquire()
        try:
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
        finally:
            self._lock.release()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        try:
            ps = Popen(["sendmail"]+list(email_message.recipients()), \
                       stdin=PIPE)
            ps.stdin.write(email_message.message().as_string())
            ps.stdin.flush()
            ps.stdin.close()
            return not ps.wait()
        except:
            if not self.fail_silently:
                raise
            return False
        return True
