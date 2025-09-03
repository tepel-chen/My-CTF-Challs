import pyshark

pcap_file = "./dist/dump.pcap"
target_ip = "34.84.101.79"
target_port = 443


def add_interval(intervals, start, end):
    if end <= start:
        return 0
    new_intervals = []
    added = end - start

    i = 0
    s, e = start, end
    while i < len(intervals) and intervals[i][1] < s:
        new_intervals.append(intervals[i])
        i += 1
    while i < len(intervals) and intervals[i][0] <= e:
        overlap_s = max(s, intervals[i][0])
        overlap_e = min(e, intervals[i][1])
        if overlap_e > overlap_s:
            added -= overlap_e - overlap_s
        s = min(s, intervals[i][0])
        e = max(e, intervals[i][1])
        i += 1
    new_intervals.append((s, e))
    while i < len(intervals):
        new_intervals.append(intervals[i])
        i += 1
    merged = []
    for a, b in sorted(new_intervals):
        if not merged or merged[-1][1] < a:
            merged.append((a, b))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
    intervals[:] = merged
    return max(0, added)


streams = {}

display = f"tcp.port == {target_port} && ip.addr == {target_ip}"
cap = pyshark.FileCapture(pcap_file, display_filter=display, keep_packets=False)

try:
    for pkt in cap:
        try:
            tcp = pkt.tcp
            stream_id = int(tcp.stream)

            seg_len = int(getattr(tcp, "len", "0") or 0)
            if seg_len <= 0:
                continue

            st = streams.setdefault(stream_id, {"intervals": [], "unique_bytes": 0})

            added = add_interval(st["intervals"], int(tcp.seq), int(tcp.nxtseq))
            st["unique_bytes"] += added

        except AttributeError:
            continue
finally:
    cap.close()

i = 1


def check_condition():
    global i
    res = streams[i]["unique_bytes"] == 5071
    i += 1
    return res


result = ""
for pos in range(1, 32 + 1):
    low = 32
    high = 126
    found = False
    while low <= high:
        mid = (low + high) // 2
        if check_condition():
            low = mid + 1
            char_guess = chr(mid)
        else:
            high = mid - 1
    if low == 32:
        break
    result += char_guess
    print(f"Password so far: {result}")

print("Leaked admin password:", result)