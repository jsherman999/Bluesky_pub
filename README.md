# Bluesky_pub

# Bluesky Post Summary Reporter

A tool for fetching recent posts from Bluesky users with both a **web interface** and command-line scripts. View posts with engagement metrics in an easy-to-read format with clickable URLs.

## Web Interface (Recommended)

The easiest way to use this tool is through the web interface. Simply enter a Bluesky handle and view posts in a beautiful, easy-to-read format.

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web server
python app.py
```

Then open your browser to: http://localhost:5000

### Features
- 🎨 Beautiful, responsive web interface
- 🔍 Search by handle (username.bsky.social or @username)
- 📊 View engagement metrics (likes, reposts, replies, quotes)
- 🔗 Clickable URLs that take you directly to Bluesky posts
- 👤 User profile information with stats
- 📱 Mobile-friendly design

## Command Line Scripts

A Python script that fetches recent posts from a Bluesky user and generates a summary report in JSON or CSV format.

## Features

- Fetches posts from any Bluesky user using their DID (Decentralized Identifier)
- Outputs in JSON or CSV format
- Includes:
  - User handle
  - Post date and time
  - Post URL
  - First line of post text
  - Engagement metrics (likes, reposts, replies, quotes)
  - Post URI

### API Endpoint

The web interface also provides a JSON API endpoint:

```bash
# Get JSON data for a user
curl http://localhost:5000/api/report/bsky.app?limit=50
```

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- `Flask` - Web framework for the web interface
- `requests` - HTTP library for API calls

Or manually install:

```bash
pip install Flask requests
```

## Usage

### Basic Usage

```bash
# JSON output (default)
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur

# CSV output
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur --format csv

# Save to file
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur --format csv --output report.csv
```

### Advanced Options

```bash
# Limit the number of posts
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur --limit 50

# Combine options
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur -f csv -l 25 -o recent_posts.csv
```

## Finding a User’s DID

To find a Bluesky user’s DID, you can:

1. Use the Bluesky public API to resolve a handle:
   
   ```bash
   curl "https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor=HANDLE.bsky.social"
   ```
1. Look at the user’s profile page source or use browser developer tools
1. Use online tools that resolve Bluesky handles to DIDs

## Command Line Arguments

- `did` (required): The DID of the Bluesky user
- `-f, --format`: Output format, either `json` or `csv` (default: json)
- `-l, --limit`: Maximum number of posts to fetch (default: 100)
- `-o, --output`: Output file path (default: stdout)

## Output Format

### JSON Output

```json
{
  "did": "did:plc:z72i7hdynmk6r22z27h6tvur",
  "handle": "username.bsky.social",
  "post_count": 100,
  "generated_at": "2025-11-02 15:30:00 UTC",
  "posts": [
    {
      "handle": "username.bsky.social",
      "post_date": "2025-11-02 14:25:33 UTC",
      "post_url": "https://bsky.app/profile/username.bsky.social/post/abc123",
      "first_line": "This is the first line of the post",
      "likes": 42,
      "reposts": 5,
      "replies": 3,
      "quotes": 1,
      "uri": "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/abc123"
    }
  ]
}
```

### CSV Output

```csv
handle,post_date,post_url,first_line,likes,reposts,replies,quotes,uri
username.bsky.social,2025-11-02 14:25:33 UTC,https://bsky.app/profile/username.bsky.social/post/abc123,This is the first line of the post,42,5,3,1,at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/abc123
```

## Examples

### Example 1: Get JSON report of 50 most recent posts

```bash
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur --limit 50
```

### Example 2: Create CSV report and save to file

```bash
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur --format csv --output my_posts.csv
```

### Example 3: Pipe JSON output to another tool

```bash
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur | jq '.posts[] | select(.likes > 10)'
```

## Error Handling

The script handles various error conditions:

- Invalid DID format
- Network errors
- API rate limits
- Missing or invalid data

Error messages are written to stderr, while the report is written to stdout (or the specified output file).

## Notes

- The script uses the public Bluesky API, which doesn’t require authentication
- The API may have rate limits, so be mindful when fetching large amounts of data
- The “first line” of a post is determined by splitting on newline characters
- Post URLs are constructed from the handle and post ID

## License

This script is provided as-is for educational and personal use.