# Tar Uploader

[日本語はこちら](./README-ja.md)

## Description

Give it to me in tar.

### Beginner Hint: Common pitfalls (AI-translated)

- Depending on your Python version, you may see behavior that differs from the server. Test with Python 3.13.
- The `nobody` user is not allowed to write to most directories and files. Because of that, getting RCE by overwriting executables or dependency files is difficult.

## Writeup

The goal of this challenge is to read `/flag.txt`. The server extracts uploaded tar files with `archive.extractall`.

A tar archive can contain symbolic links. In Python 3.13, `archive.extractall` allows those links to point to files or directories outside the extraction directory.

You can create an archive like this and upload it to the server. Then you can access the file at `http://<DOMAIN>/static/<UUID>/flag.txt`.

```bash
ln -s /flag.txt flag.txt
tar cvf test.tar flag.txt
```

You can also create a tar file in Python. See [solve.py](./solution/solve.py) for more details.

## Flag

`Alpaca{t4r_syml1nk_at7ack_1s_mit1g4ted_in_3.14}`
