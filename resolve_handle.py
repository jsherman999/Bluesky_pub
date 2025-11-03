#!/usr/bin/env python3
“””
Helper script to resolve a Bluesky handle to a DID.

Usage:
python resolve_handle.py username.bsky.social
“””

import sys
import requests

def resolve_handle(handle: str) -> str:
“”“Resolve a Bluesky handle to a DID.”””
api_base = “https://public.api.bsky.app/xrpc”

```
try:
    response = requests.get(
        f"{api_base}/app.bsky.actor.getProfile",
        params={"actor": handle},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    did = data.get("did", "")
    display_name = data.get("displayName", "")
    followers = data.get("followersCount", 0)
    following = data.get("followsCount", 0)
    posts = data.get("postsCount", 0)
    
    print(f"Handle: {handle}")
    print(f"DID: {did}")
    if display_name:
        print(f"Display Name: {display_name}")
    print(f"Stats: {followers} followers, {following} following, {posts} posts")
    
    return did
    
except requests.exceptions.RequestException as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

def main():
if len(sys.argv) < 2:
print(“Usage: python resolve_handle.py <handle>”)
print(“Example: python resolve_handle.py bsky.app”)
sys.exit(1)

```
handle = sys.argv[1]

# Remove @ if present
if handle.startswith("@"):
    handle = handle[1:]

# Add .bsky.social if no domain present
if "." not in handle:
    handle = f"{handle}.bsky.social"

resolve_handle(handle)
```

if **name** == “**main**”:
main()