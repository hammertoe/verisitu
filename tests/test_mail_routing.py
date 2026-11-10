"""Verify the robyn mail server routes hello@verisitu.com to matt's mailbox.

Run against the live host:
    python3 -m unittest discover -s tests -v

The checks are read-only apart from the delivery probe, which sends one
message through the local SMTP listener and then deletes the delivered copy.
"""
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROBOT = os.environ.get('ROBOT', 'robyn')

# A probe subject unique enough to identify the delivered copy.
# Dovecot's subject search matches a single word, so keep it to one word.
PROBE_SUBJECT = 'verisituprobe'

# The probe's Message-Id. Used to confirm the delivered copy is the probe
# before removing it.
PROBE_MESSAGE_ID = 'verisitu-probe@example.org'


def ssh(*args, check=True):
    """Run a command on the mail host and return its stdout."""
    result = subprocess.run(
        ['ssh', ROBOT, *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f'ssh {" ".join(args)} failed ({result.returncode}):\n{result.stderr}'
        )
    return result.stdout


class RoutingConfigTests(unittest.TestCase):
    """Configuration on robyn must know about verisitu.com and hello@."""

    def setUp(self):
        self.smtpd_conf = ssh('cat', '/etc/mail/smtpd.conf')

    def test_verisitu_is_an_alias_domain(self):
        self.assertIn('"verisitu.com"', self.smtpd_conf)

    def test_verisitu_has_an_alias_table(self):
        self.assertIn('table alias_verisitu', self.smtpd_conf)

    def test_verisitu_has_a_local_delivery_action(self):
        self.assertIn('action "local_lmtp_alias_verisitu"', self.smtpd_conf)

    def test_verisitu_has_an_inbound_match_rule(self):
        self.assertIn(
            'for domain "verisitu.com" action "local_lmtp_alias_verisitu"',
            self.smtpd_conf,
        )

    def test_verisitu_is_accepted_by_the_subaddress_filter(self):
        # The rspamd subaddr filter rewrites rcpt-to and must not drop
        # verisitu.com recipients before the alias table is consulted.
        self.assertIn(r'verisitu\.com', self.smtpd_conf)

    def test_alias_file_maps_hello_to_matt(self):
        aliases = ssh('cat', '/etc/mail/aliases/verisitu.com')
        self.assertRegex(aliases, r'(?m)^hello\s+matt\s*$')


class DeliveryTests(unittest.TestCase):
    """A message addressed to hello@verisitu.com must land in matt's mailbox."""

    def setUp(self):
        # The probe helper lives beside this file; copy it to the mail host.
        probe = Path(__file__).resolve().parent / 'smtp_probe.py'
        subprocess.run(
            ['scp', str(probe), f'{ROBOT}:/tmp/smtp_probe.py'],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

    def tearDown(self):
        self._remove_probe()

    def test_recipient_is_accepted(self):
        """smtpd must accept the address rather than reject it."""
        result = self._send_probe()
        self.assertIn('Recipient ok', result.stdout)
        self.assertIn('Message accepted for delivery', result.stdout)

    def test_message_to_hello_is_delivered_to_matt(self):
        self._send_probe()

        uids = self._search()
        self.assertTrue(
            uids,
            'message to hello@verisitu.com did not reach matt\'s INBOX',
        )

        header = ssh(
            'doas -n doveadm fetch -u matt hdr.Delivered-To '
            f'mailbox INBOX subject "{PROBE_SUBJECT}"'
        )
        self.assertIn('matt', header)
        self.assertIn('hello@verisitu.com', header)

    def _send_probe(self):
        """Send a message to hello@verisitu.com through the local listener."""
        return subprocess.run(
            [
                'ssh',
                ROBOT,
                'doas -n python3 /tmp/smtp_probe.py ' + PROBE_SUBJECT,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

    def _search(self):
        """Find probe message uids in matt's INBOX."""
        out = ssh(
            'doas -n doveadm search -u matt mailbox INBOX '
            f'subject "{PROBE_SUBJECT}"'
        )
        return [line.split()[0] for line in out.splitlines() if line.strip()]

    def _remove_probe(self):
        """Delete the probe copy so the mailbox is left as it was found.

        The probe carries a unique Message-Id, so only that exact message
        is removed. Nothing else in the mailbox can be caught by it.
        """
        uids = self._search()
        if not uids:
            return
        headers = ssh(
            'doas -n doveadm fetch -u matt hdr.Message-Id '
            f'mailbox INBOX subject "{PROBE_SUBJECT}"'
        )
        if PROBE_MESSAGE_ID not in headers:
            return
        ssh(
            'doas -n doveadm expunge -u matt mailbox INBOX subject '
            f'"{PROBE_SUBJECT}"',
            check=False,
        )


class DnsTests(unittest.TestCase):
    """Public DNS must route verisitu.com mail to the mail server."""

    def _mx(self):
        dig = shutil.which('dig') or '/usr/bin/dig'
        result = subprocess.run(
            [dig, '+short', 'MX', 'verisitu.com', '@1.1.1.1'],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout

    def test_mx_record_exists(self):
        self.assertTrue(
            self._mx().strip(),
            'verisitu.com has no MX record; mail would bounce',
        )

    def test_mx_points_at_the_mail_server(self):
        records = self._mx().lower()
        self.assertTrue(
            'mail.dharach.com' in records or '142.132.160.36' in records,
            f'no MX pointing at the mail server: {records!r}',
        )


if __name__ == '__main__':
    unittest.main()
