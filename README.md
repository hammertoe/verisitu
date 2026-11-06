# VeriSitu

Framework-free, static single-page website. No installation, JavaScript, analytics, cookies or build required.

## Preview

From this directory:

```sh
python3 -m http.server 8080
```

Open http://localhost:8080. Deploy `index.html`, `styles.css` and `assets/` to any static host. Tests and this README need not be published.

## Before publishing

- **Confirm the contact email.** `hello@verisitu.com` is a proposed default, not a verified mailbox. Edit the `mailto:` URL and visible label together in the contact section of `index.html` (search for `CONTACT CONFIGURATION`). No JavaScript is needed.
- Canonical and Open Graph URLs use `https://hammertoe.github.io/verisitu/`. Update them when connecting a custom domain.
- Product images are real homepage captures from https://pulsebarbados.com and https://yuhgettintru.com, taken on 6 November 2026. Refresh them when the applications change. Screenshot contents belong to their respective products, not VeriSitu traction claims.
- The diagram is conceptual, not a depiction of an already-shared technical platform. API delivery is described as a development direction, not a published API offer.

## Checks

```sh
python3 -m unittest discover -s tests -v
```

The site intentionally uses the requested light palette, system fonts, local images and CSS-only interaction feedback. Product screenshots load lazily and have explicit dimensions. Navigation works without scripts, including on mobile.
