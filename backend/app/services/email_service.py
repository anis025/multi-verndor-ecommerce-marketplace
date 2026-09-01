import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from app.core.config import settings


def validate_email_config() -> None:
    """Raise if email is required but not configured. Call at startup.

    In development a missing configuration only logs/skips. In PRODUCTION
    it fails loud so a misconfiguration (e.g. missing EMAIL_FROM) is caught
    immediately instead of silently dropping verification/notification emails.
    """
    if settings.APP_ENV != "production":
        return
    missing = []
    if not settings.SMTP_USERNAME:
        missing.append("SMTP_USERNAME")
    if not settings.SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    if not settings.EMAIL_FROM:
        missing.append("EMAIL_FROM")
    if missing:
        raise RuntimeError(
            "Email is not configured for production. Missing: "
            + ", ".join(missing)
            + ". Set these in the environment / .env before starting."
        )


class EmailService:
    """Thin SMTP wrapper. Safe in dev: if SMTP credentials are not
    configured it logs and skips instead of raising, so callers (e.g.
    checkout) never fail because of email.

    In PRODUCTION, missing email configuration fails loud (raises) so a
    misconfiguration is caught immediately instead of silently dropping
    verification/notification emails."""

    def send_verification_email(self, to: str, otp: str) -> bool:
        subject = "Verify your email - Hatify"
        text = (
            f"Welcome to Hatify!\n\n"
            f"Your email verification code is: {otp}\n\n"
            f"This code expires in 10 minutes. If you did not create a Hatify "
            f"account, you can safely ignore this email."
        )
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto">
          <h2>Welcome to Hatify</h2>
          <p>Thanks for signing up. Use the code below to verify your email address:</p>
          <p style="font-size:32px;font-weight:bold;letter-spacing:6px;
                    background:#f4f4f5;padding:16px;text-align:center;border-radius:8px">
            {otp}
          </p>
          <p>This code expires in 10 minutes. If you did not create a Hatify account,
             you can safely ignore this email.</p>
        </div>
        """
        return self.send_email(to, subject, html, text)

    def send_email(self, to: str, subject: str, html: str, text: str = None, images: dict = None) -> bool:
        if not to:
            return False
        has_creds = bool(settings.SMTP_USERNAME and settings.SMTP_PASSWORD)
        if not has_creds:
            if settings.APP_ENV == "production":
                raise RuntimeError(
                    "Email not configured: SMTP_USERNAME and SMTP_PASSWORD are required in production."
                )
            print(f"[email:dev] no SMTP credentials - attempting passwordless send "
                  f"(use a local relay like Mailpit for development).")
        if not settings.EMAIL_FROM and settings.APP_ENV == "production":
            raise RuntimeError("Email not configured: EMAIL_FROM is required in production.")
        try:
            msg = MIMEMultipart("related")
            alt = MIMEMultipart("alternative")
            if text:
                alt.attach(MIMEText(text, "plain"))
            alt.attach(MIMEText(html, "html"))
            msg.attach(alt)

            if images:
                for cid, path in images.items():
                    try:
                        with open(path, "rb") as f:
                            img = MIMEImage(f.read())
                        img.add_header("Content-ID", f"<{cid}>")
                        img.add_header("Content-Disposition", "inline", filename=os.path.basename(path))
                        msg.attach(img)
                    except Exception as e:
                        print(f"[email:warn] could not embed image {path}: {e}")

            msg["Subject"] = subject
            msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME or "no-reply@hatify.local"
            msg["To"] = to
            if settings.SMTP_USE_SSL or settings.SMTP_PORT == 465:
                with smtplib.SMTP_SSL(
                    settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT
                ) as server:
                    if has_creds:
                        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(
                    settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT
                ) as server:
                    server.starttls()
                    if has_creds:
                        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            print(f"[email:sent] to={to} subject='{subject}'")
            return True
        except Exception as e:
            print(f"[email:error] failed to send to {to}: {type(e).__name__}: {e}")
            return False

    # ----------------------------- Order emails -----------------------------

    def _format_address(self, addr: dict) -> str:
        if not addr:
            return ""
        parts = [addr.get("name", ""), addr.get("address", ""), f"Phone: {addr.get('phone', '')}" if addr.get("phone") else ""]
        return ", ".join(p for p in parts if p)

    def send_order_confirmation_email(self, to: str, order: dict, customer_name: str) -> bool:
        if not settings.EMAIL_ENABLED:
            return False
        logo_cid = "hatify-logo"
        html = self._order_confirmation_html(order, customer_name, logo_cid)
        text = self._order_confirmation_text(order, customer_name)
        subject = f"Order Confirmation - Order #{str(order.get('id', ''))[:8]}"
        return self.send_email(to, subject, html, text, images={logo_cid: settings.BRAND_LOGO_PATH})

    def send_seller_order_notification(self, to: str, seller_name: str, order: dict, items: list) -> bool:
        if not settings.EMAIL_ENABLED:
            return False
        logo_cid = "hatify-logo"
        html = self._seller_order_html(order, seller_name, items, logo_cid)
        text = self._seller_order_text(order, seller_name, items)
        subject = f"New Order Received - Order #{str(order.get('id', ''))[:8]}"
        return self.send_email(to, subject, html, text, images={logo_cid: settings.BRAND_LOGO_PATH})

    def send_admin_login_otp(self, to: str, otp: str) -> bool:
        if not settings.EMAIL_ENABLED:
            return False
        logo_cid = "hatify-logo"
        subject = "Admin sign-in code - Hatify"
        text = (
            f"Your Hatify admin sign-in code is: {otp}\n\n"
            f"This code expires in 10 minutes. If you did not request it, "
            f"please secure your account immediately."
        )
        html = f"""
        <body style="margin:0;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif">
          <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;overflow:hidden">
            <div style="background:#111;padding:20px;text-align:center">
              <img src="cid:{logo_cid}" alt="{settings.BRAND_NAME}" style="height:48px" />
            </div>
            <div style="padding:24px">
              <h2 style="margin:0 0 8px">Admin sign-in</h2>
              <p style="color:#555">Use the code below to sign in to the Hatify admin console:</p>
              <p style="font-size:32px;font-weight:bold;letter-spacing:6px;
                        background:#f4f4f5;padding:16px;text-align:center;border-radius:8px;
                        font-family:ui-monospace,Menlo,monospace">
                {otp}
              </p>
              <p style="color:#555;font-size:13px">
                This code expires in <strong>10 minutes</strong>. If you did not request
                this code, please secure your account immediately.
              </p>
            </div>
            <div style="background:#111;color:#bbb;padding:20px;font-size:13px;text-align:center">
              {settings.BRAND_NAME} &middot;
              <a href="mailto:{settings.SUPPORT_EMAIL}" style="color:#fff">{settings.SUPPORT_EMAIL}</a><br/>
              &copy; {settings.BRAND_NAME}. All rights reserved.
            </div>
          </div>
        </body>
        """
        return self.send_email(to, subject, html, text, images={logo_cid: settings.BRAND_LOGO_PATH})

    def _order_confirmation_html(self, order, customer_name, logo_cid):
        rows = "\n".join(
            f"<tr><td style='padding:10px;border-top:1px solid #eee'>{i.get('product_name','')}</td>"
            f"<td align='center' style='padding:10px'>{i.get('quantity',0)}</td>"
            f"<td align='right' style='padding:10px'>${float(i.get('subtotal',0)):.2f}</td></tr>"
            for i in order.get("items", [])
        )
        return f"""
        <body style="margin:0;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif">
          <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;overflow:hidden">
            <div style="background:#111;padding:20px;text-align:center">
              <img src="cid:{logo_cid}" alt="{settings.BRAND_NAME}" style="height:48px" />
            </div>
            <div style="padding:24px">
              <h2 style="margin:0 0 8px">Thank you, {customer_name}! 🎉</h2>
              <p style="color:#555">We've received your order
                 <strong>#{str(order.get('id',''))[:8]}</strong> and it's being processed.</p>
              <table style="width:100%;border-collapse:collapse;margin:16px 0">
                <tr style="background:#fafafa">
                  <th align="left" style="padding:10px">Item</th>
                  <th align="center" style="padding:10px">Qty</th>
                  <th align="right" style="padding:10px">Price</th>
                </tr>
                {rows}
              </table>
              <p style="text-align:right;font-size:18px"><strong>Total: ${float(order.get('total_amount',0)):.2f}</strong></p>
              <p style="color:#555"><strong>Ship to:</strong> {self._format_address(order.get('shipping_address'))}</p>
            </div>
            <div style="background:#111;color:#bbb;padding:20px;font-size:13px;text-align:center">
              {settings.BRAND_NAME} &middot;
              <a href="{settings.BRAND_WEBSITE}" style="color:#fff">Visit us</a> &middot;
              <a href="mailto:{settings.SUPPORT_EMAIL}" style="color:#fff">{settings.SUPPORT_EMAIL}</a><br/>
              &copy; {settings.BRAND_NAME}. All rights reserved.
            </div>
          </div>
        </body>
        """

    def _order_confirmation_text(self, order, customer_name):
        lines = [f"Hi {customer_name},", f"Thanks for your order #{str(order.get('id',''))[:8]}."]
        for i in order.get("items", []):
            lines.append(f"- {i.get('product_name','')} x{i.get('quantity',0)} = ${float(i.get('subtotal',0)):.2f}")
        lines.append(f"Total: ${float(order.get('total_amount',0)):.2f}")
        lines.append(f"Ship to: {self._format_address(order.get('shipping_address'))}")
        lines.append(f"\n{settings.BRAND_NAME} | {settings.SUPPORT_EMAIL}")
        return "\n".join(lines)

    def _seller_order_html(self, order, seller_name, items, logo_cid):
        rows = "\n".join(
            f"<tr><td style='padding:10px;border-top:1px solid #eee'>{i.get('product_name','')}</td>"
            f"<td align='center' style='padding:10px'>{i.get('quantity',0)}</td>"
            f"<td align='right' style='padding:10px'>${float(i.get('subtotal',0)):.2f}</td></tr>"
            for i in items
        )
        return f"""
        <body style="margin:0;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif">
          <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;overflow:hidden">
            <div style="background:#111;padding:20px;text-align:center">
              <img src="cid:{logo_cid}" alt="{settings.BRAND_NAME}" style="height:48px" />
            </div>
            <div style="padding:24px">
              <h2 style="margin:0 0 8px">New order for {seller_name} 🛒</h2>
              <p style="color:#555">Order <strong>#{str(order.get('id',''))[:8]}</strong> includes your items:</p>
              <table style="width:100%;border-collapse:collapse;margin:16px 0">
                <tr style="background:#fafafa">
                  <th align="left" style="padding:10px">Item</th>
                  <th align="center" style="padding:10px">Qty</th>
                  <th align="right" style="padding:10px">Subtotal</th>
                </tr>
                {rows}
              </table>
              <p style="color:#555"><strong>Customer shipping:</strong> {self._format_address(order.get('shipping_address'))}</p>
            </div>
            <div style="background:#111;color:#bbb;padding:20px;font-size:13px;text-align:center">
              {settings.BRAND_NAME} &middot;
              <a href="{settings.BRAND_WEBSITE}" style="color:#fff">Visit us</a> &middot;
              <a href="mailto:{settings.SUPPORT_EMAIL}" style="color:#fff">{settings.SUPPORT_EMAIL}</a>
            </div>
          </div>
        </body>
        """

    def _seller_order_text(self, order, seller_name, items):
        lines = [f"New order for {seller_name} (#{str(order.get('id',''))[:8]}):"]
        for i in items:
            lines.append(f"- {i.get('product_name','')} x{i.get('quantity',0)} = ${float(i.get('subtotal',0)):.2f}")
        lines.append(f"Customer shipping: {self._format_address(order.get('shipping_address'))}")
        return "\n".join(lines)
