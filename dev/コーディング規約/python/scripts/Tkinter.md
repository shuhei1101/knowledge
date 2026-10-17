# tkinter — GUI スクリプト規約

スクリプトに小さい操作画面を付ける程度なら tkinter で十分（本格 GUI は Electron / Tauri 等）。

## 設計指針

- UI と処理を分離: handler は引数を集めるだけ、実処理は `_do_work()` に委譲（テスト可能に）
- テーマは `ttk.Style(root).theme_use("clam")` 固定（OS 間の見た目を統一）
- アクセントカラーは青で統一（`#2563eb` 基準、hover `#1d4ed8`）。`Accent.TButton` スタイルを定義
- エラーは握りつぶさず `messagebox.showerror` でユーザーに見せる
- `tk.Tk()` は 1 つだけ。モーダルは `tk.Toplevel` 派生 + `transient(master)` + `grab_set()`、結果は `result` プロパティで返し `root.wait_window(dialog)` で受ける
- ファイル / フォルダ選択は `filedialog.askdirectory` / `askopenfilename(filetypes=...)` / `asksaveasfilename`
- 骨格（docstring / main / sys.exit）は `scripts/Pythonスクリプト.md` と同じ

## 長い処理

GUI スレッドをブロックしない:
- `threading.Thread(daemon=True)` で worker を回し、結果は `Queue` へ
- `root.after(100, poll)` のポーリングで tk イベントループ上で回収して messagebox 表示
