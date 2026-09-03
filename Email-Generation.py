# Email-Generation
import requests
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

class MohmalDirect:
    def __init__(self):
        self.base_url = "https://www.mohmal.com"
        self.inboxes = []

    def create_email(self) -> Optional[Dict]:
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            })

            session.get(self.base_url, timeout=10)

            create_url = f"{self.base_url}/ar/create/random"

            response = session.get(create_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            email = None

            email_elements = soup.find_all(['input', 'span', 'div', 'h1', 'p'],
                                           attrs={'class': re.compile(r'email|mail|address|inbox', re.I)})

            for elem in email_elements:
                text = elem.get('value', '') or elem.text.strip()
                if '@' in text and '.' in text.split('@')[-1] and len(text) > 10:
                    email = text
                    break

            if not email:
                page_text = response.text
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                matches = re.findall(email_pattern, page_text)
                if matches:
                    for match in matches:
                        if match not in [inbox['email'] for inbox in self.inboxes]:
                            email = match
                            break
                    if not email:
                        email = matches[0] if matches else None

            if not email:
                print("❌ Email address not found")
                return None

            email_info = {
                'email': email,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(minutes=45),
                'session_cookies': session.cookies.get_dict(),
                'session': session,
                'processed_msg_ids': set(),
                'last_badge_value': 0
            }

            print(f"✅ Email created: {email}")
            return email_info

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Connection error: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            return None

    def refresh_page(self, email_info: Dict) -> BeautifulSoup:
        try:
            session = email_info.get('session')
            if not session:
                session = requests.Session()
                if email_info.get('session_cookies'):
                    session.cookies.update(email_info['session_cookies'])

            refresh_url = f"{self.base_url}/ar/refresh"
            response = session.get(refresh_url, timeout=10)
            response.raise_for_status()

            return BeautifulSoup(response.text, 'html.parser')

        except Exception as e:
            return None

    def get_badge_value(self, soup: BeautifulSoup) -> int:
        try:
            badge = soup.find('span', class_='badge')
            if badge:
                text = badge.text.strip()
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
            return 0
        except Exception as e:
            return 0

    def get_all_messages_from_rows(self, soup: BeautifulSoup) -> List[Dict]:
        try:
            messages = []

            tr_elements = soup.find_all('tr', {'data-msg-id': True})

            for tr in tr_elements:
                msg_id = tr.get('data-msg-id')
                if not msg_id:
                    continue

                cells = tr.find_all('td')
                if len(cells) >= 3:
                    sender = cells[0].text.strip()
                    subject = cells[1].text.strip()
                    time_received = cells[2].text.strip()

                    messages.append({
                        'msg_id': msg_id,
                        'sender': sender,
                        'subject': subject,
                        'time': time_received
                    })

            return messages

        except Exception as e:
            return []

    def open_message_by_id(self, email_info: Dict, msg_id: str) -> Optional[str]:
        try:
            if not msg_id:
                return None

            session = email_info.get('session')
            if not session:
                session = requests.Session()
                if email_info.get('session_cookies'):
                    session.cookies.update(email_info['session_cookies'])

            message_url = f"{self.base_url}/ar/message/{msg_id}"

            print(f"   🖱️ Opening message with ID: {msg_id}")

            response = session.get(message_url, timeout=10)
            response.raise_for_status()

            print(f"   ⏳ Waiting 5 seconds for page to load...")
            time.sleep(5)

            soup = BeautifulSoup(response.text, 'html.parser')

            full_content = ""

            content_selectors = [
                '.message-body',
                '.email-body',
                '.content',
                '.message-content',
                '.body',
                '.text',
                '.details',
                'div[class*="message"]',
                'div[class*="body"]',
                'div[class*="content"]',
                'div[class*="text"]',
                'div[class*="detail"]',
                '.inbox-message',
                '.email-content',
                'pre',
                '.message-text',
                '.message-details',
                'div[role="main"]',
                '.main-content'
            ]

            for selector in content_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.text.strip()
                    if len(text) > 10:
                        full_content += " " + text

            if not full_content:
                for unwanted in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    unwanted.decompose()
                full_content = soup.body.text.strip() if soup.body else ""

            full_content = ' '.join(full_content.split())

            return full_content if full_content else None

        except Exception as e:
            print(f"   ❌ Error opening message: {e}")
            return None

    def extract_otp(self, text: str) -> Optional[str]:
        if not text:
            return None

        patterns = [
            r'OTP[:\s]*(\d{4,6})',
            r'كود[:\s]*(\d{4,6})',
            r'رمز[:\s]*(\d{4,6})',
            r'رمز التحقق[:\s]*(\d{4,6})',
            r'كود التحقق[:\s]*(\d{4,6})',
            r'رقم التحقق[:\s]*(\d{4,6})',
            r'verification[:\s]*(\d{4,6})',
            r'code[:\s]*(\d{4,6})',
            r'pin[:\s]*(\d{4,6})',
            r'token[:\s]*(\d{4,6})',
            r'[Cc]ode[:\s]*(\d{4,6})',
            r'[Vv]erification[:\s]*(\d{4,6})',
            r'[Aa]ctivate[:\s]*(\d{4,6})',
            r'(\d{6})\s*$',
            r'^(\d{6})',
            r'[\[\(](\d{4,6})[\]\)]',
            r'\b(\d{6})\b',
            r'\b(\d{5})\b',
            r'\b(\d{4})\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                code = match.group(1) if match.lastindex else match.group(0)
                if code and len(code) >= 4:
                    return code

        six_digit = re.findall(r'\b(\d{6})\b', text)
        if six_digit:
            return six_digit[0]

        return None

    def monitor_emails(self, duration_minutes: int = 60):
        print(f"\n🔍 Starting monitoring for {duration_minutes} minutes...")
        print("🔄 Refreshing every 3 seconds to check for new messages\n")

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        refresh_count = 0

        while time.time() < end_time:
            for email_info in self.inboxes:
                if datetime.now() > email_info['expires_at']:
                    continue

                try:
                    refresh_count += 1
                    soup = self.refresh_page(email_info)

                    if not soup:
                        continue

                    badge_value = self.get_badge_value(soup)

                    if refresh_count % 5 == 0:
                        print(f"   📊 [{email_info['email']}] Badge: {badge_value}")

                    if badge_value > 0:
                        all_messages = self.get_all_messages_from_rows(soup)

                        if all_messages:
                            new_messages = [
                                msg for msg in all_messages
                                if msg['msg_id'] not in email_info.get('processed_msg_ids', set())
                            ]

                            if new_messages:
                                print(f"\n🔔 Detected {len(new_messages)} new message(s)! (Badge = {badge_value})")

                                for idx, msg in enumerate(new_messages, 1):
                                    msg_id = msg.get('msg_id')

                                    if 'processed_msg_ids' not in email_info:
                                        email_info['processed_msg_ids'] = set()
                                    email_info['processed_msg_ids'].add(msg_id)

                                    print(f"\n{'=' * 60}")
                                    print(f"📩 Message {idx} of {len(new_messages)}")
                                    print(f"📩 Email: {email_info['email']}")
                                    print(f"🆔 Message ID: {msg_id}")
                                    print(f"   📤 From: {msg.get('sender', 'Unknown')}")
                                    print(f"   📌 Subject: {msg.get('subject', 'No subject')}")
                                    print(f"   ⏰ Time: {msg.get('time', 'Unknown')}")

                                    full_content = self.open_message_by_id(email_info, msg_id)

                                    if full_content:
                                        print(f"\n   📝 Full message content:")
                                        print(f"   {'-' * 50}")
                                        print(f"   {full_content}")
                                        print(f"   {'-' * 50}")

                                        otp = self.extract_otp(full_content)
                                        if otp:
                                            print(f"\n   ✅ 🔑 OTP Code: {otp}")
                                        else:
                                            print(f"\n   ℹ️ No clear OTP code found")
                                    else:
                                        print(f"   ❌ Failed to open message")
                                    print(f"{'=' * 60}")

                                    if idx < len(new_messages):
                                        time.sleep(2)

                                print(f"   🔄 Updating page...")
                                time.sleep(2)
                            else:
                                if refresh_count % 10 == 0:
                                    print(f"   ℹ️ All known messages processed (Badge: {badge_value})")
                        else:
                            if refresh_count % 10 == 0:
                                print(f"   ⚠️ No messages found on page")

                except Exception as e:
                    pass

            time.sleep(3)

            elapsed = time.time() - start_time
            if int(elapsed) % 30 == 0 and elapsed > 0:
                remaining = int((end_time - time.time()) / 60)
                if remaining > 0:
                    print(f"⏳ {remaining} minutes remaining...")

        print("\n⏰ Monitoring finished (60 minutes).")

    def run(self):
        print("=" * 59)
        print("        ███████╗ ███╗   ███╗  █████╗  ██╗ ██╗")
        print("        ██╔════╝ ████╗ ████║ ██╔══██╗ ██║ ██║")
        print("        █████╗   ██╔████╔██║ ███████║ ██║ ██║")
        print("        ██╔══╝   ██║╚██╔╝██║ ██╔══██║ ██║ ██║")
        print("        ███████╗ ██║ ╚═╝ ██║ ██║  ██║ ██║ ███████╗")
        print("        ╚══════╝ ╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚═╝ ╚══════╝")
        print("=" * 59)

        while True:
            try:
                count = input("\n🔢 How many emails do you want to create :")
                if count.lower() == 'q':
                    print("👋 Exiting.")
                    return

                count = int(count)
                if count <= 0:
                    print("⚠️ Please enter a positive number.")
                    continue
                break
            except ValueError:
                print("⚠️ Please enter a valid number.")

        print(f"\n🔄 Creating {count} email(s)...")
        print("⏳ This may take a few seconds per email...\n")

        for i in range(count):
            print(f"📧 Creating email {i + 1}:")
            email_info = self.create_email()

            if email_info:
                self.inboxes.append(email_info)
                print(f"   ✅ {email_info['email']}")
            else:
                print(f"   ❌ Failed to create email {i + 1}")

            if i < count - 1:
                print("   ⏳ Waiting 3 seconds before next email...")
                time.sleep(3)

        if not self.inboxes:
            print("\n❌ No emails were created. Check your internet connection.")
            return

        print("\n" + "=" * 60)
        print("📨 Created emails:")
        for idx, inbox in enumerate(self.inboxes, 1):
            print(f"   {idx}. {inbox['email']}")
        print("=" * 60)

        self.monitor_emails(duration_minutes=60)


if __name__ == "__main__":
    try:
        app = MohmalDirect()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Program stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")