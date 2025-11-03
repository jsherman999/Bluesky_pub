#!/usr/bin/env python3
“””
Bluesky Post Summary Reporter

Fetches recent posts from a Bluesky user via their DID and generates a summary report
in JSON or CSV format.

Usage:
python bluesky_report.py <DID> [–format json|csv] [–limit N] [–output FILE]

Example:
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur –format json
python bluesky_report.py did:plc:z72i7hdynmk6r22z27h6tvur –format csv –output report.csv
“””

import argparse
import json
import csv
import sys
from datetime import datetime
from typing import List, Dict, Any
import requests

class BlueskyReporter:
“”“Handles fetching and reporting on Bluesky posts.”””

```
def __init__(self):
    self.api_base = "https://public.api.bsky.app/xrpc"
    
def resolve_handle(self, did: str) -> str:
    """
    Resolve a DID to get the user's handle.
    
    Args:
        did: The DID (Decentralized Identifier) of the user
        
    Returns:
        The user's handle
    """
    try:
        response = requests.get(
            f"{self.api_base}/app.bsky.actor.getProfile",
            params={"actor": did},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("handle", "Unknown")
    except Exception as e:
        print(f"Warning: Could not resolve handle: {e}", file=sys.stderr)
        return "Unknown"

def fetch_user_posts(self, did: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch recent posts from a Bluesky user.
    
    Args:
        did: The DID of the user
        limit: Maximum number of posts to fetch
        
    Returns:
        List of post data dictionaries
    """
    posts = []
    cursor = None
    
    print(f"Fetching posts for DID: {did}...", file=sys.stderr)
    
    while len(posts) < limit:
        params = {
            "actor": did,
            "limit": min(100, limit - len(posts))
        }
        if cursor:
            params["cursor"] = cursor
            
        try:
            response = requests.get(
                f"{self.api_base}/app.bsky.feed.getAuthorFeed",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            feed = data.get("feed", [])
            if not feed:
                break
                
            posts.extend(feed)
            cursor = data.get("cursor")
            
            if not cursor:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching posts: {e}", file=sys.stderr)
            break
    
    print(f"Fetched {len(posts)} posts", file=sys.stderr)
    return posts

def extract_post_summary(self, post_data: Dict[str, Any], handle: str) -> Dict[str, Any]:
    """
    Extract summary information from a post.
    
    Args:
        post_data: Raw post data from API
        handle: User's handle
        
    Returns:
        Dictionary with summary information
    """
    post = post_data.get("post", {})
    record = post.get("record", {})
    
    # Extract post text (first line)
    text = record.get("text", "")
    first_line = text.split('\n')[0] if text else ""
    
    # Extract metadata
    created_at = record.get("createdAt", "")
    
    # Parse date for better formatting
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        formatted_date = created_at
    
    # Build post URL
    uri = post.get("uri", "")
    # URI format: at://did:plc:xxx/app.bsky.feed.post/xxxxx
    post_id = uri.split('/')[-1] if uri else ""
    post_url = f"https://bsky.app/profile/{handle}/post/{post_id}" if post_id and handle != "Unknown" else ""
    
    # Extract engagement metrics
    like_count = post.get("likeCount", 0)
    repost_count = post.get("repostCount", 0)
    reply_count = post.get("replyCount", 0)
    quote_count = post.get("quoteCount", 0)
    
    return {
        "handle": handle,
        "post_date": formatted_date,
        "post_url": post_url,
        "first_line": first_line,
        "likes": like_count,
        "reposts": repost_count,
        "replies": reply_count,
        "quotes": quote_count,
        "uri": uri
    }

def generate_report(self, did: str, output_format: str = "json", limit: int = 100) -> str:
    """
    Generate a summary report for a user's posts.
    
    Args:
        did: The DID of the user
        output_format: Output format ('json' or 'csv')
        limit: Maximum number of posts to include
        
    Returns:
        Formatted report as string
    """
    # Get user handle
    handle = self.resolve_handle(did)
    
    # Fetch posts
    posts = self.fetch_user_posts(did, limit)
    
    # Extract summaries
    summaries = [self.extract_post_summary(post, handle) for post in posts]
    
    # Generate output
    if output_format.lower() == "json":
        return json.dumps({
            "did": did,
            "handle": handle,
            "post_count": len(summaries),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "posts": summaries
        }, indent=2)
    elif output_format.lower() == "csv":
        return self._generate_csv(summaries)
    else:
        raise ValueError(f"Unsupported format: {output_format}")

def _generate_csv(self, summaries: List[Dict[str, Any]]) -> str:
    """Generate CSV output from post summaries."""
    if not summaries:
        return ""
    
    # Use StringIO for CSV writing
    from io import StringIO
    string_buffer = StringIO()
    
    fieldnames = ["handle", "post_date", "post_url", "first_line", "likes", "reposts", "replies", "quotes", "uri"]
    writer = csv.DictWriter(string_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(summaries)
    
    return string_buffer.getvalue()
```

def main():
parser = argparse.ArgumentParser(
description=“Generate a summary report of Bluesky posts for a user”,
formatter_class=argparse.RawDescriptionHelpFormatter,
epilog=”””
Examples:
%(prog)s did:plc:z72i7hdynmk6r22z27h6tvur –format json
%(prog)s did:plc:z72i7hdynmk6r22z27h6tvur –format csv –limit 50 –output report.csv
%(prog)s did:plc:z72i7hdynmk6r22z27h6tvur -f json -l 25
“””
)

```
parser.add_argument(
    "did",
    help="The DID (Decentralized Identifier) of the Bluesky user (e.g., did:plc:...)"
)

parser.add_argument(
    "-f", "--format",
    choices=["json", "csv"],
    default="json",
    help="Output format (default: json)"
)

parser.add_argument(
    "-l", "--limit",
    type=int,
    default=100,
    help="Maximum number of posts to fetch (default: 100)"
)

parser.add_argument(
    "-o", "--output",
    help="Output file path (default: stdout)"
)

args = parser.parse_args()

# Validate DID format
if not args.did.startswith("did:"):
    print("Error: DID must start with 'did:' (e.g., did:plc:...)", file=sys.stderr)
    print("\nTip: You can find a user's DID by looking at their profile API response", file=sys.stderr)
    sys.exit(1)

try:
    reporter = BlueskyReporter()
    report = reporter.generate_report(args.did, args.format, args.limit)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(report)
        
except KeyboardInterrupt:
    print("\nOperation cancelled by user", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

if **name** == “**main**”:
main()