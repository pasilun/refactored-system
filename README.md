# Gmail Unsubscriber

A command-line tool that reads your Gmail inbox and finds unsubscribe links. It presents a table showing:
- Unsubscribe links found in your emails
- Number of emails from each sender (with the same unsubscribe link)
- Last date an email was received from each sender

## Features

- 🔍 Scans emails from the last 30 days
- 📧 Extracts unsubscribe links from email headers and body
- 📊 Displays results in a clean, formatted table
- 🔒 Secure OAuth2 authentication with Gmail API
- 📈 Aggregates data by unsubscribe link to show frequency

## Requirements

- Python 3.7 or higher
- Gmail account
- Google Cloud Project with Gmail API enabled

## Installation

1. Clone this repository:
```bash
git clone https://github.com/pasilun/refactored-system.git
cd refactored-system
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Setup

### 1. Enable Gmail API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Create OAuth Credentials

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Give it a name (e.g., "Gmail Unsubscriber")
5. Click "Create"
6. Download the credentials file
7. Save it as `credentials.json` in the project directory

For detailed instructions, see the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)

## Usage

Run the tool:
```bash
python gmail_unsubscriber.py
```

Or, if you made it executable:
```bash
./gmail_unsubscriber.py
```

On first run:
1. The tool will open your browser for OAuth authentication
2. Sign in with your Gmail account
3. Grant the requested permissions (read-only access to Gmail)
4. The tool will save your credentials in `token.json` for future use

The tool will then:
1. Fetch emails from the last 30 days
2. Extract unsubscribe links from each email
3. Display a table with:
   - Unsubscribe link
   - Number of emails with that link
   - Last date an email was received

### Example Output

```
============================================================
Gmail Unsubscriber - Find Unsubscribe Links
============================================================

✓ Successfully authenticated with Gmail API

Fetching emails from the last 30 days...
  Total messages found: 245

Processing 245 emails to find unsubscribe links...
  Processed 50/245 emails...
  Processed 100/245 emails...
  Processed 150/245 emails...
  Processed 200/245 emails...
  Completed processing all emails.

====================================================================================================
UNSUBSCRIBE LINKS FOUND IN THE LAST 30 DAYS
====================================================================================================
+--------------------------------------------------------+-------+------------------+
| Unsubscribe Link                                       | Count | Last Date        |
+========================================================+=======+==================+
| https://example.com/unsubscribe?id=12345               |    15 | 2026-01-20 14:30 |
+--------------------------------------------------------+-------+------------------+
| https://newsletter.com/unsub/abc123                    |     8 | 2026-01-19 09:15 |
+--------------------------------------------------------+-------+------------------+
| https://marketing.site/remove?email=user@example.com   |     5 | 2026-01-18 16:45 |
+--------------------------------------------------------+-------+------------------+

Total unique unsubscribe links: 3
Total emails with unsubscribe links: 28
```

## Security & Privacy

- This tool uses OAuth2 for secure authentication
- It only requests **read-only** access to your Gmail (`gmail.readonly` scope)
- No emails or data are sent to external servers
- All processing happens locally on your machine
- Your credentials are stored locally in `token.json` (excluded from git)

## Permissions

The tool requires the following Gmail API scope:
- `https://www.googleapis.com/auth/gmail.readonly` - Read-only access to Gmail

## Troubleshooting

### "credentials.json not found" Error

Make sure you've downloaded the OAuth credentials from Google Cloud Console and saved them as `credentials.json` in the project directory.

### Authentication Issues

If you encounter authentication problems:
1. Delete `token.json`
2. Run the script again to re-authenticate

### No Emails Found

- Check that your Gmail account has emails from the last 30 days
- Verify that the tool has been granted the necessary permissions

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
