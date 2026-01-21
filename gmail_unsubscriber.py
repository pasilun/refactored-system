#!/usr/bin/env python3
"""
Gmail Unsubscriber - Find unsubscribe links in Gmail
"""

import os
import re
import base64
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from tabulate import tabulate

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailUnsubscriber:
    def __init__(self):
        self.service = None
        self.unsubscribe_data = defaultdict(lambda: {"count": 0, "last_date": None, "emails": []})

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("\nERROR: credentials.json not found!")
                    print("\nTo use this tool, you need to:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a new project or select an existing one")
                    print("3. Enable the Gmail API")
                    print("4. Create OAuth 2.0 credentials (Desktop app)")
                    print("5. Download the credentials and save as 'credentials.json' in this directory")
                    print("\nFor detailed instructions, visit:")
                    print("https://developers.google.com/gmail/api/quickstart/python")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def get_emails_from_last_month(self) -> List[Dict]:
        """Fetch emails from the last month"""
        if not self.service:
            return []
        
        # Calculate date one month ago
        one_month_ago = datetime.now() - timedelta(days=30)
        query = f'after:{one_month_ago.strftime("%Y/%m/%d")}'
        
        print(f"\nFetching emails from the last 30 days...")
        
        try:
            messages = []
            page_token = None
            
            while True:
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token,
                    maxResults=500
                ).execute()
                
                if 'messages' in results:
                    messages.extend(results['messages'])
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                
                print(f"  Fetched {len(messages)} messages so far...")
            
            print(f"  Total messages found: {len(messages)}")
            return messages
        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def extract_unsubscribe_links(self, message_id: str) -> Tuple[List[str], str]:
        """Extract unsubscribe links from an email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Get the date
            headers = message.get('payload', {}).get('headers', [])
            date_str = None
            for header in headers:
                if header['name'].lower() == 'date':
                    date_str = header['value']
                    break
            
            # Check for List-Unsubscribe header
            unsubscribe_links = []
            for header in headers:
                if header['name'].lower() == 'list-unsubscribe':
                    # Extract URLs from the header (format: <url1>, <url2>)
                    urls = re.findall(r'<(https?://[^>]+)>', header['value'])
                    unsubscribe_links.extend(urls)
            
            # Also check email body for unsubscribe links
            body = self._get_email_body(message)
            if body:
                # Look for common unsubscribe link patterns
                body_links = re.findall(
                    r'<a[^>]*href=["\']([^"\']*unsubscribe[^"\']*)["\'][^>]*>',
                    body,
                    re.IGNORECASE
                )
                unsubscribe_links.extend(body_links)
                
                # Also look for plain URLs with "unsubscribe" in them
                plain_links = re.findall(
                    r'https?://[^\s<>"\']+unsubscribe[^\s<>"\']*',
                    body,
                    re.IGNORECASE
                )
                unsubscribe_links.extend(plain_links)
            
            # Remove duplicates and clean links
            unsubscribe_links = list(set([link.strip() for link in unsubscribe_links if link.strip()]))
            
            return unsubscribe_links, date_str
        
        except Exception as e:
            print(f"  Error processing message {message_id}: {e}")
            return [], None

    def _get_email_body(self, message: Dict) -> str:
        """Extract email body from message"""
        try:
            payload = message.get('payload', {})
            
            # Try to get HTML body
            body = None
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/html':
                        body = part.get('body', {}).get('data')
                        break
                    elif part.get('mimeType') == 'multipart/alternative' and 'parts' in part:
                        for subpart in part['parts']:
                            if subpart.get('mimeType') == 'text/html':
                                body = subpart.get('body', {}).get('data')
                                break
            else:
                body = payload.get('body', {}).get('data')
            
            if body:
                # Decode base64
                decoded = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
                return decoded
        
        except Exception as e:
            pass
        
        return ""

    def process_emails(self):
        """Process all emails and extract unsubscribe information"""
        messages = self.get_emails_from_last_month()
        
        if not messages:
            print("\nNo emails found in the last month.")
            return
        
        print(f"\nProcessing {len(messages)} emails to find unsubscribe links...")
        processed = 0
        
        for msg in messages:
            msg_id = msg['id']
            links, date_str = self.extract_unsubscribe_links(msg_id)
            
            for link in links:
                # Normalize the link (remove tracking parameters for better grouping)
                normalized_link = self._normalize_link(link)
                
                self.unsubscribe_data[normalized_link]["count"] += 1
                self.unsubscribe_data[normalized_link]["emails"].append(msg_id)
                
                # Parse and update last date
                if date_str:
                    try:
                        # Parse email date
                        email_date = self._parse_email_date(date_str)
                        if email_date:
                            if (self.unsubscribe_data[normalized_link]["last_date"] is None or
                                email_date > self.unsubscribe_data[normalized_link]["last_date"]):
                                self.unsubscribe_data[normalized_link]["last_date"] = email_date
                    except:
                        pass
            
            processed += 1
            if processed % 50 == 0:
                print(f"  Processed {processed}/{len(messages)} emails...")
        
        print(f"  Completed processing all emails.")

    def _normalize_link(self, link: str) -> str:
        """Normalize unsubscribe link by removing some tracking parameters"""
        # Keep the full link but clean up some common variations
        # Remove trailing slashes
        link = link.rstrip('/')
        
        # For very similar links, we'll keep them as-is
        # You could add more sophisticated normalization here
        return link

    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        from email.utils import parsedate_to_datetime
        try:
            return parsedate_to_datetime(date_str)
        except:
            return None

    def display_results(self):
        """Display results in a table"""
        if not self.unsubscribe_data:
            print("\nNo unsubscribe links found.")
            return
        
        # Prepare table data
        table_data = []
        for link, data in sorted(self.unsubscribe_data.items(), key=lambda x: x[1]["count"], reverse=True):
            last_date = data["last_date"].strftime("%Y-%m-%d %H:%M") if data["last_date"] else "Unknown"
            count = data["count"]
            
            # Truncate long links for display
            display_link = link if len(link) <= 80 else link[:77] + "..."
            
            table_data.append([display_link, count, last_date])
        
        # Display table
        print("\n" + "="*100)
        print("UNSUBSCRIBE LINKS FOUND IN THE LAST 30 DAYS")
        print("="*100)
        print(tabulate(
            table_data,
            headers=["Unsubscribe Link", "Count", "Last Date"],
            tablefmt="grid"
        ))
        print(f"\nTotal unique unsubscribe links: {len(self.unsubscribe_data)}")
        print(f"Total emails with unsubscribe links: {sum(data['count'] for data in self.unsubscribe_data.values())}")

    def run(self):
        """Main entry point"""
        print("="*60)
        print("Gmail Unsubscriber - Find Unsubscribe Links")
        print("="*60)
        
        if not self.authenticate():
            return
        
        print("\n✓ Successfully authenticated with Gmail API")
        
        self.process_emails()
        self.display_results()


def main():
    """Main function"""
    unsubscriber = GmailUnsubscriber()
    unsubscriber.run()


if __name__ == '__main__':
    main()
