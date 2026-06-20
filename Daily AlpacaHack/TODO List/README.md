# TODO List

[日本語版はこちら](./README-ja.md)

## Description
TODO: Check if this website doesn't contain any XSS.

### Beginner Hint1: About the Admin Bot

- In this challenge, you are given not only the web application itself, but also an Admin Bot.
- The Admin Bot has a cookie containing the flag, and it opens a specified path using Headless Chrome.
- Therefore, your goal is to make the Admin Bot trigger your payload and send the cookie value to an external server.
- You can prepare your own server as the destination, or use an existing service that lets you receive and inspect HTTP requests.
- If you are still not familiar with how to use the Admin Bot or how to inspect incoming requests, it may help to solve [Fushigi Crawler](https://alpacahack.com/daily/challenges/fushigi-crawler?month=2026-01) first and read its writeup.

### Beginner Hint2: Overview of the Challenge
  
- This is a simple TODO application. When you first visit it, you get a session ID, and you can create a TODO list associated with that session.
- If you specify `?sessionId=...`, you can also view the list associated with another user's session. In other words, you can make the Admin Bot open your own session.
- Each TODO item accepts HTML input, but it is not rendered as-is. The app sanitizes it with [DOMPurify](https://github.com/cure53/DOMPurify).
- DOMPurify itself is the latest version, so this probably is not a challenge where you exploit an old known vulnerability in DOMPurify directly.

### Beginner Hint3: Approach
  
- A basic rule when using a sanitizer like DOMPurify is that you should not further transform the sanitized string afterward.
- In this application, is the data left untouched after sanitization?

## Writeup

### Overview

WIP

## Flag
`Alpaca{T0do:f1x_th3_XS5}`
