#!/usr/bin/env python3
"""
Bluesky Post Reporter - Web Frontend

A Flask web application that allows users to view Bluesky posts by entering a handle.
"""

from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
from typing import List, Dict, Any

app = Flask(__name__)

class BlueskyService:
    """Service for interacting with Bluesky API."""

    def __init__(self):
        self.api_base = "https://public.api.bsky.app/xrpc"

    def resolve_handle(self, handle: str) -> Dict[str, Any]:
        """
        Resolve a Bluesky handle to get user information.

        Args:
            handle: The Bluesky handle (e.g., username.bsky.social)

        Returns:
            Dictionary with user information including DID
        """
        # Clean up handle
        handle = handle.strip()
        if handle.startswith("@"):
            handle = handle[1:]
        if "." not in handle:
            handle = f"{handle}.bsky.social"

        try:
            response = requests.get(
                f"{self.api_base}/app.bsky.actor.getProfile",
                params={"actor": handle},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                "success": True,
                "did": data.get("did", ""),
                "handle": data.get("handle", ""),
                "displayName": data.get("displayName", ""),
                "followersCount": data.get("followersCount", 0),
                "followsCount": data.get("followsCount", 0),
                "postsCount": data.get("postsCount", 0),
                "avatar": data.get("avatar", "")
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

    def fetch_user_posts(self, did: str, limit: int = 50) -> List[Dict[str, Any]]:
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

            except requests.exceptions.RequestException:
                break

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

        # Extract post text
        text = record.get("text", "")
        first_line = text.split('\n')[0] if text else ""

        # Extract metadata
        created_at = record.get("createdAt", "")

        # Parse date for better formatting
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            relative_date = self._get_relative_time(dt)
        except:
            formatted_date = created_at
            relative_date = created_at

        # Build post URL
        uri = post.get("uri", "")
        post_id = uri.split('/')[-1] if uri else ""
        post_url = f"https://bsky.app/profile/{handle}/post/{post_id}" if post_id and handle else ""

        # Extract engagement metrics
        like_count = post.get("likeCount", 0)
        repost_count = post.get("repostCount", 0)
        reply_count = post.get("replyCount", 0)
        quote_count = post.get("quoteCount", 0)

        return {
            "handle": handle,
            "post_date": formatted_date,
            "relative_date": relative_date,
            "post_url": post_url,
            "text": text,
            "first_line": first_line,
            "likes": like_count,
            "reposts": repost_count,
            "replies": reply_count,
            "quotes": quote_count,
            "uri": uri
        }

    def _get_relative_time(self, dt: datetime) -> str:
        """Get relative time string (e.g., '2 hours ago')."""
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago" if minutes > 1 else "1m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago" if hours > 1 else "1h ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}d ago" if days > 1 else "1d ago"
        else:
            return dt.strftime("%b %d, %Y")

    def get_user_report(self, handle: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get a complete report for a user by their handle.

        Args:
            handle: The Bluesky handle
            limit: Maximum number of posts to fetch

        Returns:
            Dictionary with user info and posts
        """
        # Resolve handle to get user info
        user_info = self.resolve_handle(handle)

        if not user_info["success"]:
            return user_info

        # Fetch posts
        did = user_info["did"]
        handle = user_info["handle"]
        posts = self.fetch_user_posts(did, limit)

        # Extract summaries
        summaries = [self.extract_post_summary(post, handle) for post in posts]

        return {
            "success": True,
            "user": user_info,
            "posts": summaries,
            "post_count": len(summaries)
        }


# Initialize service
bluesky_service = BlueskyService()


@app.route('/')
def index():
    """Render the home page with search form."""
    return render_template('index.html')


@app.route('/report', methods=['POST'])
def report():
    """Handle report request and display results."""
    handle = request.form.get('handle', '').strip()
    limit = int(request.form.get('limit', 50))

    if not handle:
        return render_template('index.html', error="Please enter a Bluesky handle")

    # Get report
    result = bluesky_service.get_user_report(handle, limit)

    if not result["success"]:
        return render_template('index.html', error=f"Error: {result.get('error', 'Unknown error')}")

    return render_template('report.html', result=result)


@app.route('/api/report/<handle>')
def api_report(handle: str):
    """API endpoint to get report as JSON."""
    limit = request.args.get('limit', 50, type=int)
    result = bluesky_service.get_user_report(handle, limit)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
