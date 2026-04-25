#!/usr/bin/env bash
# ============================================================
# ai-journal-sync · build-time smoke test
# 在 git push 之前跑這個（pre-push hook 或 CI）
# 任何一篇 daily 雙倍渲染 / 缺欄位 / 假連結都會 fail，阻擋 push
# ============================================================
set -euo pipefail

POSTS_DIR="${1:-posts}"
fail=0

echo "Running smoke tests on $POSTS_DIR/*.html ..."

for f in "$POSTS_DIR"/*.html; do
  bn="$(basename "$f")"
  # 跳過 template / index 本身
  case "$bn" in
    _template.html|index.html) continue ;;
  esac

  # 1. keypoints ≤ 1（daily 通常 1 個 / 發刊詞 0 個都 OK 但不能 2）
  count=$(grep -c '<aside class="keypoints"' "$f" || true)
  if [ "$count" -gt 1 ]; then
    echo "❌ $f: aside.keypoints=$count (want ≤ 1) — 雙倍渲染信號"
    fail=1
  fi

  # 2. figure ≤ 10
  fig=$(grep -c '<figure' "$f" || true)
  if [ "$fig" -gt 10 ]; then
    echo "❌ $f: figure=$fig (want ≤ 10) — 雙倍渲染信號"
    fail=1
  fi

  # 3. article.post 恰好 1 個
  art=$(grep -c '<article class="post"' "$f" || true)
  if [ "$art" -ne 1 ]; then
    echo "❌ $f: article.post=$art (want 1)"
    fail=1
  fi

  # 4. DOCTYPE 之後直接 <html>（中間最多空白；用 tr 把換行壓掉跨行 match）
  head_chunk=$(head -c 200 "$f" | tr -d '\n')
  if ! printf '%s' "$head_chunk" | grep -qE '<!DOCTYPE[^>]*>[[:space:]]*<html'; then
    echo "❌ $f: DOCTYPE 與 <html> 之間有東西（可能是 v2.0 註解 bug）"
    fail=1
  fi

  # 5. 沒有未替換的 {{PLACEHOLDER}}
  if grep -qE '\{\{[A-Z_]+\}\}' "$f"; then
    bad=$(grep -oE '\{\{[A-Z_]+\}\}' "$f" | sort -u | tr '\n' ' ')
    echo "❌ $f: 殘留未替換 placeholder: $bad"
    fail=1
  fi

  # 6. HN item ID 必須是純數字
  bad_hn=$(grep -oE 'news\.ycombinator\.com/item\?id=[^"&]+' "$f" | grep -vE '\?id=[0-9]+$' || true)
  if [ -n "$bad_hn" ]; then
    echo "❌ $f: 假 HN item id（必須純數字）: $bad_hn"
    fail=1
  fi
done

if [ "$fail" -eq 1 ]; then
  echo ""
  echo "smoke test FAILED — 不要 push"
  exit 1
fi

echo "✓ smoke test passed for all posts"
