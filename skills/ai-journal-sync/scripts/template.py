"""
ai-journal-sync · template renderer

關鍵函式：
- render(template, vars) — 安全替換 placeholder
- strip_pre_html_comments(html) — P0 防呆 step 4a
- smoke_test(html, slug) — P0 防呆 step 4b
"""

import re


PLACEHOLDER_RE = re.compile(r'\{\{([A-Z_]+)\}\}')


def render(template: str, vars: dict) -> str:
    """
    用 {{NAME}} placeholder 替換 vars。
    缺值的 placeholder 替換成空字串（不留 {{X}} 在輸出）。
    """
    def sub(m):
        return str(vars.get(m.group(1), ''))
    return PLACEHOLDER_RE.sub(sub, template)


def strip_pre_html_comments(html: str) -> str:
    """
    砍掉 <!DOCTYPE> 與 <html> 之間的所有 HTML 註解。
    P0 防呆：避免 v2.0 範本那種把 placeholder 寫在註解裡的設計再次踩雷。
    """
    return re.sub(
        r'(<!DOCTYPE[^>]*>)\s*(?:<!--.*?-->\s*)+(?=<html\b)',
        r'\1\n',
        html,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


class BuildError(Exception):
    pass


def smoke_test(html: str, slug: str) -> None:
    """
    渲染後 assert：
    - keypoints / article.post 都恰好 1 個
    - DOCTYPE 後直接 <html>（中間最多空白）
    - 沒有未替換的 {{PLACEHOLDER}}
    - figure 不能 > 10 (防雙倍渲染的副作用)
    """
    checks = [
        (html.count('<aside class="keypoints"'), 1, 'aside.keypoints 必須恰好 1 個'),
        (html.lower().count('<article class="post"'), 1, 'article.post 必須恰好 1 個'),
        (
            bool(re.search(r'<!DOCTYPE[^>]*>\s*<html\b', html, re.IGNORECASE)),
            True,
            'DOCTYPE 與 <html> 之間不能有任何內容（v2.0 P0 bug 重現訊號）',
        ),
        (
            bool(re.search(r'\{\{[A-Z_]+\}\}', html)),
            False,
            '不能有未替換的 {{PLACEHOLDER}}',
        ),
        (html.count('<figure'), 'le10', 'figure 不能超過 10（雙倍渲染症狀）'),
    ]
    failures = []
    for actual, want, msg in checks:
        if want == 'le10':
            if actual > 10:
                failures.append((actual, '<= 10', msg))
        elif actual != want:
            failures.append((actual, want, msg))

    if failures:
        details = '\n'.join(f'  - {msg} (got {a}, want {w})' for a, w, msg in failures)
        raise BuildError(f'[{slug}] smoke test failed:\n{details}')


# ============================================================
# 範例用法（unit test 用）
# ============================================================
if __name__ == '__main__':
    # 故意製造 v2.0 bug 重現：body 內含 HTML 註解
    body_with_comment = (
        '<!-- 今日重點方向 -->\n'
        '<aside class="keypoints"><div class="kp-label">key</div></aside>\n'
        '<article class="post"><div>內容</div></article>'
    )

    # 用乾淨的 v2.1 模板（DOCTYPE 後直接 <html>）
    template_v21 = (
        '<!DOCTYPE html>\n'
        '<html lang="zh-Hant"><head><title>{{TITLE}}</title></head>\n'
        '<body>{{BODY_HTML}}</body></html>'
    )
    rendered = render(template_v21, {'TITLE': 'Test', 'BODY_HTML': body_with_comment})
    rendered = strip_pre_html_comments(rendered)
    smoke_test(rendered, 'test-v21')
    print('✓ v2.1 模板 + body 內含註解 → smoke test 通過')

    # 模擬 v2.0 bug：模板自己有 DOCTYPE 註解
    template_v20_bug = (
        '<!DOCTYPE html>\n'
        '<!--\n'
        '  Placeholder: {{BODY_HTML}} 文章主體\n'
        '-->\n'
        '<html><body>{{BODY_HTML}}</body></html>'
    )
    rendered2 = render(template_v20_bug, {'BODY_HTML': body_with_comment})
    rendered2 = strip_pre_html_comments(rendered2)  # ← 這條會砍掉 DOCTYPE 註解
    try:
        smoke_test(rendered2, 'test-v20-with-strip')
        print('✓ v2.0 模板 + strip → smoke test 通過（strip 救回來了）')
    except BuildError as e:
        print(f'✗ v2.0 + strip 還是炸: {e}')
