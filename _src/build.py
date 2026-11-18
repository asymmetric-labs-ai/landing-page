#!/usr/bin/env python3
"""Builds the asymmetriclabs.ai static pages.

    uv run --with markdown python _src/build.py            # draft: missing details are highlighted
    uv run --with markdown python _src/build.py --release  # fails if any detail is missing

Company details, prices and store links live in _src/site.json. The Terms and Privacy Policy
are rendered from _src/legal/*.md. Pages are written to the repository root, which GitHub Pages
serves as is. Do not edit the generated .html files by hand.
"""
import html
import json
import re
import sys
from pathlib import Path

import markdown

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
SITE = json.loads((SRC / "site.json").read_text())
HELA_LOGO = (SRC / "hela-logo.svg").read_text().strip()
BASE = "https://asymmetriclabs.ai"
MISSING: list[str] = []

LEGAL = SITE["legal_name"]
BRAND = SITE["brand"]
SUPPORT = SITE["support_email"]
LEGAL_EMAIL = SITE["legal_email"]
EFFECTIVE = SITE["effective_date"]
HELA_URL = SITE["hela"]["url"]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def todo(label: str) -> str:
    """Placeholder for a detail site.json does not have yet."""
    if label not in MISSING:
        MISSING.append(label)
    return f'<mark class="todo">Add {esc(label)}</mark>'


def need(value: str, label: str) -> str:
    return esc(value) if value else todo(label)


def mailto(address: str) -> str:
    return f'<a href="mailto:{esc(address)}">{esc(address)}</a>'


def address_lines() -> str:
    lines = SITE["registered_office"]
    return "<br>".join(esc(line) for line in lines) if lines else todo("registered office address")


def address_inline() -> str:
    lines = SITE["registered_office"]
    return esc(", ".join(lines)) if lines else todo("registered office address")


def company_rows(extra: str = "") -> str:
    rows = [
        ("Legal name", esc(LEGAL)),
        ("Trading name", esc(BRAND)),
        ("CIN", need(SITE["cin"], "CIN")),
        ("GSTIN", need(SITE["gstin"], "GSTIN")),
        ("Jurisdiction", "India"),
        ("Website", '<a href="/">asymmetriclabs.ai</a>'),
    ]
    return "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + extra


def asym_store_buttons() -> str:
    asym = SITE["asym"]
    buttons = []
    if asym["play_url"]:
        buttons.append(f'<a class="btn primary" href="{esc(asym["play_url"])}" rel="noopener">Get Asym on Google Play</a>')
    if asym["appstore_url"]:
        buttons.append(f'<a class="btn primary" href="{esc(asym["appstore_url"])}" rel="noopener">Get Asym on the App Store</a>')
    if not buttons:
        buttons.append(todo("Asym Google Play and App Store links"))
    return "\n".join(buttons)


NAV = [("/asym/", "Asym"), ("/hela/", "Hela"), ("/pricing/", "Pricing"), ("/about/", "About"), ("/contact/", "Contact")]
FOOT = [
    ("/asym/", "Asym"),
    ("/hela/", "Hela"),
    ("/pricing/", "Pricing"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
    ("/terms/", "Terms"),
    ("/privacy/", "Privacy"),
    ("/refunds/", "Cancellation and refunds"),
    ("/delivery/", "Delivery"),
    ("/apply-for-editor/", "Work with us"),
]
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' "
    "fill='%231a1814'/%3E%3Ctext x='32' y='44' text-anchor='middle' font-family='Georgia,serif' font-style='italic' "
    "font-size='36' fill='%23f1ece2'%3Ea.%3C/text%3E%3C/svg%3E"
)


def page(path: str, title: str, description: str, body: str) -> None:
    current = ' aria-current="page"'
    nav = "".join(f'<a href="{href}"{current if href == path else ""}>{label}</a>' for href, label in NAV)
    foot = "".join(f'<a href="{href}">{label}</a>' for href, label in FOOT)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{BASE}{path}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{BASE}{path}">
  <meta property="og:type" content="website">
  <link rel="icon" href="{FAVICON}">
  <link rel="stylesheet" href="/assets/site.css">
</head>
<body>
  <header>
    <div class="wrap">
      <a class="mark" href="/" aria-label="{esc(BRAND)} home">Asymmetric Labs<b>.</b></a>
      <nav aria-label="Primary">{nav}</nav>
    </div>
  </header>

  <main>
{body}
  </main>

  <footer>
    <div class="wrap">
      <p class="legal">© 2026 {esc(LEGAL)}. Asym is a product of {esc(LEGAL)}. Asymmetric Labs is the sole distributor of Hela in India.</p>
      <nav aria-label="Footer">{foot}</nav>
    </div>
  </footer>
</body>
</html>
"""
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)


def hero(eyebrow: str, heading: str, text: str, small: bool = True) -> str:
    return f"""    <div class="hero{' small' if small else ''}">
      <div class="wrap">
        <p class="eyebrow">{eyebrow}</p>
        <h1>{heading}<b>.</b></h1>
        <p>{text}</p>
      </div>
    </div>"""


def build_home() -> None:
    body = f"""{hero(esc(LEGAL), "Aiding human intelligence with AI", f"{esc(BRAND)} is the trading name of {esc(LEGAL)}, an Indian education technology company. We build Asym, a learning platform for UPSC aspirants. We are also the sole distributor of Hela in India.", small=False)}

    <section id="what-we-do">
      <div class="wrap">
        <p class="eyebrow">What we do</p>
        <h2>One product of our own, one we distribute, and the services behind both.</h2>
        <div class="cols three">
          <div class="card">
            <h3>Our product</h3>
            <h4>Asym</h4>
            <p>A learning platform for UPSC Civil Services aspirants: study notes, previous year questions with explanations, tests and current affairs, on Android, iOS and the web.</p>
            <div class="btns"><a class="btn" href="/asym/">About Asym</a></div>
          </div>
          <div class="card">
            <h3>Distribution in India</h3>
            <h4>Hela</h4>
            <p>Asymmetric Labs is the sole distributor of Hela in India.</p>
            <div class="btns"><a class="btn" href="/hela/">Hela in India</a></div>
          </div>
          <div class="card">
            <h3>Services</h3>
            <h4>Technology and content</h4>
            <p>We provide software development, content production and user support services for Hela, alongside the work on our own product.</p>
            <div class="btns"><a class="btn" href="/about/">About the company</a></div>
          </div>
        </div>
      </div>
    </section>

    <section id="asym">
      <div class="wrap">
        <p class="eyebrow">Our product</p>
        <h2>Asym, for UPSC aspirants.</h2>
        <p class="lede">Asym brings the syllabus, the previous year questions and the practice into one place, so that what you read and what you are tested on stay connected.</p>
        <div class="product">
          <div>
            <p class="wordmark">Asym<b>.</b></p>
            <h3>Study notes, previous year questions and tests for the UPSC Civil Services Examination.</h3>
            <p>Asym is free to use at the moment. Available as an Android app, an iOS app and on the web.</p>
            <div class="btns">
              <a class="btn primary" href="/asym/">See what Asym includes</a>
              <a class="btn" href="/pricing/">Pricing</a>
            </div>
          </div>
          <ul class="facts">
            <li><strong>What it is</strong>A learning platform for the UPSC Civil Services Examination, free to use at the moment.</li>
            <li><strong>What you get</strong>Study notes, previous year questions with explanations, custom tests and current affairs.</li>
            <li><strong>Who it is for</strong>UPSC aspirants in India, aged 16 and over.</li>
          </ul>
        </div>
      </div>
    </section>

    <section id="hela">
      <div class="wrap">
        <p class="eyebrow">Distributed in India</p>
        <h2>Hela, for medical students and clinicians.</h2>
        <p class="lede">Asymmetric Labs is the sole distributor of Hela in India.</p>
        <div class="product">
          <div>
            {HELA_LOGO}
            <h3>Clinical knowledge, kept current, with the evidence attached.</h3>
            <p>A medical knowledge platform for medical students and clinicians. Everything about Hela, including plans and prices, is on hela.org.</p>
            <div class="btns">
              <a class="btn primary" href="{esc(HELA_URL)}" rel="noopener">Visit hela.org</a>
            </div>
          </div>
          <ul class="facts">
            <li><strong>Our role</strong>Sole distributor of Hela in India.</li>
            <li><strong>Who it is for</strong>Medical students and clinicians.</li>
            <li><strong>Plans and prices</strong>See <a href="{esc(HELA_URL)}" rel="noopener">hela.org</a>.</li>
          </ul>
        </div>
      </div>
    </section>

    <section id="company">
      <div class="wrap">
        <p class="eyebrow">Company</p>
        <h2>Business details.</h2>
        <p class="lede">{esc(LEGAL)} is a private limited company incorporated in India under the Companies Act, 2013. It trades as {esc(BRAND)}.</p>
        <div class="cols">
          <div class="card">
            <h3>Registered office</h3>
            <address>
              <span class="big">{esc(LEGAL)}</span><br>
              {address_lines()}
            </address>
          </div>
          <div class="card">
            <h3>Company details</h3>
            <dl>{company_rows()}</dl>
          </div>
        </div>
      </div>
    </section>

    <section id="contact">
      <div class="wrap">
        <p class="eyebrow">Contact</p>
        <h2>Need help? Write to us.</h2>
        <p class="lede">For questions about Asym, or about a payment or refund for a Hela subscription bought in India, write to {mailto(SUPPORT)} from the email address on your account.</p>
        <div class="btns">
          <a class="btn primary" href="/contact/">Contact us</a>
          <a class="btn" href="/refunds/">Cancellation and refunds</a>
        </div>
      </div>
    </section>"""
    page(
        "/",
        "Asymmetric Labs — Makers of Asym, sole distributor of Hela in India",
        f"{LEGAL} (Asymmetric Labs) builds Asym, a learning platform for UPSC aspirants, and is the sole distributor of Hela in India.",
        body,
    )


def build_asym() -> None:
    features = [
        ("Study notes", "Notes organised by subject and topic across the Prelims syllabus, written and reviewed by subject experts."),
        ("Previous year questions", "Questions from past UPSC Prelims papers, each with an explained answer and a link back to the notes it draws on."),
        ("Tests", "Practice by topic or build a custom test from the subjects and years you choose, then review every answer."),
        ("Current affairs", "Current affairs material tied to the syllabus topics it belongs to."),
        ("Your progress", "Bookmarks for notes and questions, and statistics on what you have attempted and how you scored."),
        ("Discussion", "Comment on notes and questions, and report anything that looks wrong so it gets corrected."),
    ]
    cards = "\n".join(f'<div class="card"><h4>{t}</h4><p>{d}</p></div>' for t, d in features)
    body = f"""{hero("Our product", "Asym", "Asym is a learning platform for UPSC Civil Services aspirants. It keeps study notes, previous year questions and practice tests in one place, on Android, iOS and the web.")}

    <section>
      <div class="wrap">
        <p class="eyebrow">What Asym includes</p>
        <h2>Read, practise, and see where you stand.</h2>
        <div class="cols three">
{cards}
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Plans</p>
        <h2>Free at the moment.</h2>
        <p class="lede">Asym is free to use at the moment: you create an account and get access without paying. If we introduce paid plans, the plan, its price and its duration will be shown on this site and in Asym before anyone is charged.</p>
        <div class="btns">
          <a class="btn primary" href="/pricing/">Pricing</a>
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Get Asym</p>
        <h2>On your phone and on the web.</h2>
        <p class="lede">Asym is for users aged 16 and over. Users aged 16 or 17 need the consent of a parent or guardian, as our <a href="/terms/">Terms</a> explain.</p>
        <div class="btns">
          {asym_store_buttons()}
        </div>
      </div>
    </section>"""
    page(
        "/asym/",
        "Asym — Learning platform for UPSC aspirants",
        "Asym is a learning platform for UPSC Civil Services aspirants: study notes, previous year questions with explanations, tests and current affairs.",
        body,
    )


def build_hela() -> None:
    body = f"""{hero("Distributed in India", "Hela in India", "Asymmetric Labs is the sole distributor of Hela in India.")}

    <section>
      <div class="wrap">
        <p class="eyebrow">The product</p>
        <h2>A medical knowledge platform.</h2>
        <p class="lede">Hela is a medical knowledge platform for medical students and clinicians. Everything about the product, including its plans and current prices, is on <a href="{esc(HELA_URL)}" rel="noopener">hela.org</a>.</p>
        <p class="lede">As the sole distributor in India, {esc(LEGAL)} sells and bills Hela subscriptions bought in India. Billing, cancellation and refunds are covered by our <a href="/refunds/">Cancellation and Refund Policy</a>.</p>
        <div class="btns">
          <a class="btn primary" href="{esc(HELA_URL)}" rel="noopener">Visit hela.org</a>
          <a class="btn" href="/contact/">Billing support</a>
        </div>
      </div>
    </section>"""
    page(
        "/hela/",
        "Hela in India — Asymmetric Labs",
        "Asymmetric Labs is the sole distributor of Hela in India.",
        body,
    )


def build_pricing() -> None:
    body = f"""{hero("Pricing", "Pricing", "Asym, our own product, is free to use at the moment. We are the sole distributor of Hela in India; its plans and prices are on hela.org.")}

    <section>
      <div class="wrap">
        <p class="eyebrow">Our product</p>
        <h2>Asym.</h2>
        <div class="cols">
          <div class="card plan">
            <h3>Asym</h3>
            <h4>Free access</h4>
            <p class="price">₹0</p>
            <p class="period">Free at the moment</p>
            <p>Create an account and use Asym without paying. If we introduce paid plans, the plan, its price and its duration will be shown here and in Asym before anyone is charged.</p>
          </div>
          <div class="card">
            <h3>Included</h3>
            <ul>
              <li>Study notes across the Prelims syllabus</li>
              <li>Previous year questions with explained answers</li>
              <li>Topic tests and custom tests</li>
              <li>Current affairs material</li>
              <li>Bookmarks and progress statistics</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Distributed in India</p>
        <h2>Hela.</h2>
        <p class="lede">Asymmetric Labs is the sole distributor of Hela in India. Subscriptions are sold in Indian Rupees with GST included. Plans and current prices are shown on hela.org, where you subscribe.</p>
        <div class="btns">
          <a class="btn primary" href="{esc(HELA_URL)}" rel="noopener">Visit hela.org</a>
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Paying</p>
        <h2>Payment, cancellation and refunds.</h2>
        <p class="lede">Payments are processed by Razorpay. We do not store your card, UPI or bank details. You can cancel a renewing subscription at any time and keep access to the end of the period you have paid for.</p>
        <div class="btns">
          <a class="btn primary" href="/refunds/">Cancellation and refunds</a>
          <a class="btn" href="/delivery/">Delivery</a>
          <a class="btn" href="/terms/">Terms</a>
        </div>
      </div>
    </section>"""
    page(
        "/pricing/",
        "Pricing — Asymmetric Labs",
        "Asym is free to use at the moment. Hela subscriptions sold in India are priced on hela.org.",
        body,
    )


def build_about() -> None:
    body = f"""{hero("About us", "About Asymmetric Labs", f"{esc(BRAND)} is the trading name of {esc(LEGAL)}, an education technology company in India. We build learning software for people preparing for demanding examinations.")}

    <section>
      <div class="wrap">
        <p class="eyebrow">Our business</p>
        <h2>Three lines of work.</h2>
        <div class="cols three">
          <div class="card">
            <h3>1. Asym</h3>
            <p>Our own product: a learning platform for UPSC Civil Services aspirants. It is free to use at the moment.</p>
          </div>
          <div class="card">
            <h3>2. Hela distribution</h3>
            <p>Asymmetric Labs is the sole distributor of Hela in India. We sell Hela subscriptions to users in India and collect payment in Indian Rupees.</p>
          </div>
          <div class="card">
            <h3>3. Services</h3>
            <p>We provide software development, content production and user support services for Hela.</p>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Customers</p>
        <h2>Who we sell to.</h2>
        <p class="lede">Our customers are individual learners in India: UPSC aspirants for Asym, and medical students and clinicians for Hela. What we sell is a digital subscription, bought online with access given immediately. We do not sell physical goods.</p>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Company</p>
        <h2>Business details.</h2>
        <div class="cols">
          <div class="card">
            <h3>Registered office</h3>
            <address>
              <span class="big">{esc(LEGAL)}</span><br>
              {address_lines()}
            </address>
          </div>
          <div class="card">
            <h3>Company details</h3>
            <dl>{company_rows(f"<dt>Support</dt><dd>{mailto(SUPPORT)}</dd>")}</dl>
          </div>
        </div>
      </div>
    </section>"""
    page(
        "/about/",
        "About — Asymmetric Labs",
        f"About {LEGAL} (Asymmetric Labs): maker of Asym and sole distributor of Hela in India.",
        body,
    )


def build_contact() -> None:
    phone = SITE["phone"]
    phone_card = (
        f'''<div class="card">
            <h3>Phone</h3>
            <p class="big"><a href="tel:{esc(phone.replace(" ", ""))}">{esc(phone)}</a></p>
          </div>'''
        if phone
        else ""
    )
    body = f"""{hero("Contact", "Contact us", "Write to us about Asym, a Hela subscription bought in India, a payment, a refund or your personal data.")}

    <section>
      <div class="wrap">
        <div class="cols" style="margin-top:0">
          <div class="card">
            <h3>Support and billing</h3>
            <p class="big">{mailto(SUPPORT)}</p>
            <p>Write from the email address on your account. For a payment or refund question, include the order or payment ID from your receipt.</p>
          </div>
          {phone_card}
          <div class="card">
            <h3>Grievance Officer</h3>
            <p class="big">{esc(SITE["grievance_officer"])}</p>
            <p>{mailto(LEGAL_EMAIL)}</p>
            <p>For complaints, legal notices and personal data requests. We acknowledge a complaint within 24 hours and resolve it within 15 days.</p>
          </div>
          <div class="card">
            <h3>Registered office</h3>
            <address>
              <span class="big">{esc(LEGAL)}</span><br>
              {address_lines()}
            </address>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="wrap">
        <p class="eyebrow">Hela</p>
        <h2>Questions about Hela itself.</h2>
        <p class="lede">For help using Hela, its content or your Hela account, use <a href="https://hela.org/support" rel="noopener">hela.org/support</a>. For anything about a payment made in India, write to us at {mailto(SUPPORT)}.</p>
      </div>
    </section>"""
    page("/contact/", "Contact — Asymmetric Labs", f"Contact {LEGAL}: support, billing, grievance officer and registered office.", body)


def build_refunds() -> None:
    body = f"""{hero("Policy", "Cancellation and refunds", f"This policy covers every subscription sold by {esc(LEGAL)}. Today that means Hela subscriptions bought in India; Asym is free to use at the moment. Effective {esc(EFFECTIVE)}.")}

    <section>
      <div class="wrap prose">
        <h2 style="margin-top:0">1. What you buy</h2>
        <p>We sell digital subscriptions. A subscription gives access to the product's paid content and features for the period you buy. Prices are shown in Indian Rupees, inclusive of GST, before you pay. Payments are processed by Razorpay.</p>

        <h2>2. Renewal</h2>
        <p><strong>Hela.</strong> A Hela subscription renews automatically at the end of each billing period, at the price shown when you subscribed, until you cancel.</p>
        <p><strong>Asym.</strong> Asym is free at the moment, so there is nothing to renew or cancel. If we introduce paid plans, a plan will run for the duration bought and will not renew automatically unless that is stated at purchase.</p>

        <h2>3. Cancelling</h2>
        <p>You can cancel a renewing subscription at any time before the next renewal date, from your account on <a href="https://hela.org" rel="noopener">hela.org</a> or by writing to {mailto(SUPPORT)}. Cancellation stops future charges. Your access continues to the end of the period you have already paid for; the current period is not refunded on cancellation.</p>

        <h2>4. Refunds</h2>
        <p>In line with the Consumer Protection Act, 2019 and the Consumer Protection (E-Commerce) Rules, 2020:</p>
        <ul>
          <li><strong>Charged but not activated, or charged twice.</strong> If you are charged and the subscription is not activated, or you are charged more than once for the same order, we refund the failed or extra charge in full.</li>
          <li><strong>Service fault.</strong> If a technical fault on our side stops you from using the core paid features of your subscription for a continuous 72 hours or more after you report it, you may ask for a pro-rata refund for the affected period.</li>
          <li><strong>Change of mind.</strong> Because a subscription gives immediate access to digital content, we do not offer change-of-mind refunds once paid content has been accessed, except where the law requires it.</li>
        </ul>

        <h2>5. How to ask for a refund</h2>
        <p>Write to {mailto(SUPPORT)} from the email address on your account, with the order or payment ID and the reason. Approved refunds go back to the original payment method, typically within 5 to 7 business days after Razorpay confirms the refund. Your bank may take longer to show it.</p>

        <h2>6. Purchases through an app store</h2>
        <p>If you bought a subscription through the Apple App Store or Google Play billing, cancellation and refunds are handled by that store under its own policies.</p>

        <h2>7. Contact</h2>
        <p>{esc(LEGAL)}, {address_inline()}. Support and Grievance Officer ({esc(SITE["grievance_officer"])}): {mailto(SUPPORT)}.</p>
      </div>
    </section>"""
    page(
        "/refunds/",
        "Cancellation and Refund Policy — Asymmetric Labs",
        f"How to cancel a subscription sold by {LEGAL}, and when refunds are given.",
        body,
    )


def build_delivery() -> None:
    body = f"""{hero("Policy", "Delivery", f"{esc(LEGAL)} sells digital subscriptions only. Nothing is shipped. Effective {esc(EFFECTIVE)}.")}

    <section>
      <div class="wrap prose">
        <h2 style="margin-top:0">1. How access is delivered</h2>
        <p>Everything we sell is delivered online. When your payment is confirmed, the subscription is activated on the account you paid from and you can use it straight away in the app or on the web.</p>

        <h2>2. No physical delivery</h2>
        <p>We do not sell or ship physical goods, so there are no shipping charges, delivery addresses or delivery times.</p>

        <h2>3. If access does not start</h2>
        <p>If you have been charged and your subscription is not active, sign out and back in first. If it is still not active, write to {mailto(SUPPORT)} from the email address on your account with the order or payment ID. We will activate the subscription or refund the charge, as our <a href="/refunds/">Cancellation and Refund Policy</a> sets out.</p>

        <h2>4. Where we sell</h2>
        <p>Subscriptions are sold to users in India and charged in Indian Rupees.</p>
      </div>
    </section>"""
    page("/delivery/", "Delivery Policy — Asymmetric Labs", f"{LEGAL} sells digital subscriptions delivered online; nothing is shipped.", body)


def render_legal(source: str) -> str:
    text = (SRC / "legal" / source).read_text()
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = text.replace("Asym AI Labs Pvt Ltd", LEGAL)
    text = text.replace("\n**Last updated:**", "  \n**Last updated:**")
    text = re.sub(r"\[EFFECTIVE DATE[^\]]*\]|\[LAST UPDATED[^\]]*\]", EFFECTIVE, text)
    text = text.replace("https://asymmetriclabs.ai/privacy", "/privacy/").replace("https://asymmetriclabs.ai/terms", "/terms/")
    out = markdown.markdown(text, extensions=["tables", "sane_lists"])
    out = re.sub(r"\[REGISTERED OFFICE ADDRESS[^\]]*\]", lambda _: address_inline(), out)
    return out.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")


def build_legal() -> None:
    note = f"""<blockquote><p><strong>Scope.</strong> These Terms cover Asym. Hela is governed by Hela's own <a href="https://hela.org/terms" rel="noopener">Terms of Use</a>; billing for Hela subscriptions bought in India is covered by our <a href="/refunds/">Cancellation and Refund Policy</a>.</p></blockquote>"""
    terms = f"""{hero("Legal", "Terms and Conditions", "The terms that govern your use of Asym.")}

    <section>
      <div class="wrap prose">
        {note}
        {render_legal("terms.md")}
      </div>
    </section>"""
    page("/terms/", "Terms and Conditions — Asymmetric Labs", f"Terms governing the use of Asym, operated by {LEGAL}.", terms)
    privacy = f"""{hero("Legal", "Privacy Policy", "What personal data we collect, why, and the rights you have.")}

    <section>
      <div class="wrap prose">
        {render_legal("privacy.md")}
      </div>
    </section>"""
    page("/privacy/", "Privacy Policy — Asymmetric Labs", f"How {LEGAL} processes personal data for Asym.", privacy)


def build_sitemap() -> None:
    paths = ["/", "/asym/", "/hela/", "/pricing/", "/about/", "/contact/", "/terms/", "/privacy/", "/refunds/", "/delivery/", "/apply-for-editor/"]
    urls = "".join(f"<url><loc>{BASE}{p}</loc></url>" for p in paths)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")


def main() -> int:
    build_home()
    build_asym()
    build_hela()
    build_pricing()
    build_about()
    build_contact()
    build_refunds()
    build_delivery()
    build_legal()
    build_sitemap()
    if MISSING:
        print("Missing from _src/site.json:")
        for label in MISSING:
            print(f"  - {label}")
        if "--release" in sys.argv:
            print("Release build refused: fill these in first.")
            return 1
    print("Built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
