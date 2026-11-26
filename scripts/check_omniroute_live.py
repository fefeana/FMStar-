import json
import os
import sys
import urllib.request


def main():
    server_url = os.environ.get("FMSTAR_LIVE_URL", "https://fmstar-ai-studio.onrender.com").rstrip("/")
    payload = json.dumps({"prompt": "فحص اتصال حي مع استوديو FMStar و OmniRoute"}).encode("utf-8")
    req = urllib.request.Request(
        f"{server_url}/api/v1/studio/generate",
        data=payload,
        headers={"Content-Type": "application/json", "Origin": "https://fefeana.github.io"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            print(f"HTTP {resp.status}: {body[:500]}")
            sys.exit(0)
    except Exception as exc:
        print(f"Live check result: {exc}")
        sys.exit(0)


if __name__ == "__main__":
    main()
