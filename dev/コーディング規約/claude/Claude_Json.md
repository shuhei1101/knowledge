# Claude Code Jsonファイル作成時のルール

## コメントの書き方
- Jsonはコメントを書けないが、以下方法でコメントを記載すること
- オブジェクト自体のコメントは不要（以下例の `permissions` にコメントがないように）
- 各キーは一行の間を空けること
  - ただし、最上部のキーやコメントがないキーは除く。つまり、コメントがないキーどうしが並ぶ場合は空行不要
```json
{
  "permissions": {
    "_defaultMode": "権限モードの初期値。bypassPermissionsで毎回の確認をスキップ",
    "defaultMode": "bypassPermissions"
  },

  "_effortLevel": "推論にかける労力のレベル。highで高品質寄り",
  "effortLevel": "high",
  
  "_autoUpdatesChannel": "自動アップデートの取得チャンネル。latestで最新版を追従",
  "autoUpdatesChannel": "latest",
  
  "_autoMemoryEnabled": "自動メモリ機能の有効/無効。falseで無効",
  "autoMemoryEnabled": false
}
```

### フックコメント
- フックのみ特殊でフック内のキーに`_description`を設置し、そこに説明を載せる

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Read",
        "hooks": [
          {
            "type": "command",
            "_description": "本フックの説明を記載する",
            "command": "python",
            "args": [
              "${CLAUDE_PROJECT_DIR}/hooks/sample.py"
            ]
          }
        ]
      }
    ]
  }
}
```
