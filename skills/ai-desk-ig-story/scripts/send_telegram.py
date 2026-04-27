"""
ai-desk-ig-story · Telegram 推送

把產出的 story.png + caption.txt 推到 Telegram bot 的私聊。

跑法：
  python3 send_telegram.py <story.png> <caption.txt>

需要環境變數（找不到時會 fallback 讀 ~/.config/ai-desk/telegram.env）：
  TELEGRAM_BOT_TOKEN  bot 的 token
  TELEGRAM_CHAT_ID    收訊息的 chat id (private user / group / channel)
"""
import os
import re
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path


def load_env():
    """先看 process env，再 fallback 讀 ~/.config/ai-desk/telegram.env。"""
    env_file = Path.home() / '.config' / 'ai-desk' / 'telegram.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            m = re.match(r'(?:export\s+)?(\w+)\s*=\s*[\'"]?([^\'"\n]+)[\'"]?\s*$', line)
            if m:
                os.environ.setdefault(m.group(1), m.group(2))


def send_message(token: str, chat_id: str, text: str, parse_mode: str = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    if parse_mode:
        data['parse_mode'] = parse_mode
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method='POST')
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def send_photo(token: str, chat_id: str, photo_path: Path, caption: str = '') -> dict:
    """multipart/form-data upload."""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    boundary = '----IGStoryUpload' + os.urandom(8).hex()

    parts = []
    # chat_id
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n')
    # caption (optional, max 1024 chars for Telegram photo caption)
    if caption:
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n')
    # photo file
    photo_data = photo_path.read_bytes()
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="{photo_path.name}"\r\nContent-Type: image/png\r\n\r\n')

    body = b''.join([p.encode('utf-8') if isinstance(p, str) else p for p in parts])
    body += photo_data
    body += f'\r\n--{boundary}--\r\n'.encode()

    req = urllib.request.Request(
        url, data=body, method='POST',
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def push_story(story_path: Path, caption_path: Path) -> bool:
    load_env()
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("❌ Telegram 環境變數沒設")
        print("   請設 TELEGRAM_BOT_TOKEN 跟 TELEGRAM_CHAT_ID")
        print("   或跑 setup-telegram.sh 一次設好")
        return False

    if not story_path.exists():
        print(f"❌ story 不存在: {story_path}")
        return False
    if not caption_path.exists():
        print(f"❌ caption 不存在: {caption_path}")
        return False

    caption_text = caption_path.read_text(encoding='utf-8').strip()
    # 從 caption 抽 title (第一行) + edition row (第三行) 當 header
    lines = caption_text.split('\n')
    title = lines[0] if lines else 'AI DESK'
    edition_row = lines[2] if len(lines) > 2 else ''

    try:
        # 1. header
        header = (
            "📸 *AI DESK · IG Story 素材*\n\n"
            f"{edition_row}\n"
            "✓ 1080×1920 PNG 已產出\n"
            "✓ Caption + hashtag 已產出\n\n"
            "存圖到相簿 → 開 IG → 加限動 → 30 秒"
        )
        r1 = send_message(token, chat_id, header, parse_mode='Markdown')
        if not r1.get('ok'):
            print(f"❌ header send failed: {r1}")
            return False

        # 2. photo (no caption — caption 太長 Telegram 限 1024 chars)
        r2 = send_photo(token, chat_id, story_path)
        if not r2.get('ok'):
            print(f"❌ photo send failed: {r2}")
            return False

        # 3. caption as a separate message
        # Telegram message limit 4096 chars
        caption_for_tg = caption_text[:4000]
        r3 = send_message(token, chat_id, caption_for_tg)
        if not r3.get('ok'):
            print(f"❌ caption send failed: {r3}")
            return False

        print("✓ Telegram 推送成功（3 則訊息）")
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 send_telegram.py <story.png> <caption.txt>")
        sys.exit(1)

    story = Path(sys.argv[1]).expanduser().resolve()
    caption = Path(sys.argv[2]).expanduser().resolve()
    success = push_story(story, caption)
    sys.exit(0 if success else 1)
