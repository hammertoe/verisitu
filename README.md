# VeriSitu

Framework-free, static single-page website. No installation, JavaScript, analytics, cookies or build required.

## Preview

From this directory:

```sh
python3 -m http.server 8080
```

Open http://localhost:8080. Deploy `index.html`, `styles.css` and `assets/` to any static host. Tests and this README need not be published.

## Before publishing

- **Confirm the contact email.** `hello@verisitu.com` is a live mailbox. It is hosted on `robyn.dharach.com` (OpenSMTPD + Dovecot) and forwards to `matt@dharach.com` via the alias in `/etc/mail/aliases/verisitu.com`. If the address changes, edit the `mailto:` URL and visible label together in the contact section of `index.html` (search for `CONTACT CONFIGURATION`) and update the alias on the mail server. No JavaScript is needed.
- Canonical and Open Graph URLs use `https://hammertoe.github.io/verisitu/`. Update them when connecting a custom domain.
- Product images are real homepage captures from https://pulsebarbados.com and https://yuhgettintru.com, taken on 6 November 2026. Refresh them when the applications change. Screenshot contents belong to their respective products, not VeriSitu traction claims.
- The diagram is conceptual, not a depiction of an already-shared technical platform. API delivery is described as a development direction, not a published API offer.

## Mail routing

`hello@verisitu.com` forwards to `matt@dharach.com`.

- DNS: `verisitu.com` MX `10 mail.dharach.com` (A `142.132.160.36`).
- On robyn, `/etc/mail/smtpd.conf` lists `verisitu.com` in `alias_domains`, loads `table alias_verisitu` from `/etc/mail/aliases/verisitu.com`, adds `action "local_lmtp_alias_verisitu"` (LMTP to the local Dovecot on `127.0.0.1:24`) and matches `for domain "verisitu.com"`. The domain is also added to the `subaddr` filter regex so tagged addresses are not dropped.
- `/etc/mail/aliases/verisitu.com` maps `hello` to `matt`, which delivers into the `matt` Maildir.
- The domain is receive-and-forward only. There is no DKIM key and no SPF record for it, so robyn does not send mail as `@verisitu.com`.

## Checks

```sh
python3 -m unittest discover -s tests -v
```

`tests/test_site.py` covers the page. `tests/test_mail_routing.py` covers the mail server: it checks the smtpd configuration, the alias file, the public MX record, and delivers a probe message to `hello@verisitu.com` through the local SMTP listener, asserting it reaches matt's INBOX. The probe is identified by its Message-Id and removed afterwards, so the mailbox is left unchanged. The suite requires `ssh` access to the mail host as the `ROBOT` user (override with the `ROBOT` environment variable).

The site intentionally uses the requested light palette, system fonts, local images and CSS-only interaction feedback. Product screenshots load lazily and have explicit dimensions. Navigation works without scripts, including on mobile.
