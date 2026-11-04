// 文中の太字（strong）を違反にする。インラインコードの中の ** は strong にならないため対象外
export default {
  names: ["KN001", "no-inline-strong"],
  description: "太字を使わない（Markdown 編集規約 emphasis-01）",
  tags: ["emphasis"],
  parser: "micromark",
  function: (params, onError) => {
    for (const token of params.parsers.micromark.tokens) {
      walk(token, onError);
    }
  },
};

function walk(token, onError) {
  if (token.type === "strong") {
    onError({ lineNumber: token.startLine, detail: token.text });
  }
  for (const child of token.children) {
    walk(child, onError);
  }
}
