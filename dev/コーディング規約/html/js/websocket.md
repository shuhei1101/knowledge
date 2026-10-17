# WebSocket

- `class WsClient extends EventTarget` で実装し、購読側は `addEventListener` で受ける。
- 再接続は指数バックオフ。URL は `createWsUrl()` 経由（ハードコードしない）。
