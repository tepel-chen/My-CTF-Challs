# Julia ni Jailbreak

## 問題文

https://youtu.be/vdPIPVsx0B0

## Writeup

[このバグ](https://github.com/JuliaLang/julia/issues/54328)を利用する。これは多次元配列を作成する際に、整数オーバーフローを起こすことにより、配列がメモリ上で配置可能かのチェックをバイパスし、メモリ全域アクセス可能な配列を生成できてしまうバグである。これを利用することで、任意アドレス読み込み・書き込みが可能となる。

これ以降のアプローチはROPなど複数考えられるが、一番簡単な方法は、スクリプトが実行した後に[REPLに移行するかどうかのフラグがスタック上にある](https://github.com/JuliaLang/julia/blob/99663f5828517f31f7b50ab17ca1e2d59ae4f2e3/base/client.jl#L241)ので、これを書き換えることにより、REPLを起動することである。具体的には:
* PIEは無効のため、juliaの`.data`上にあるlibc上のアドレスからlibcのベースアドレスをリークする。
* libc上の.data上にあるld.so上のアドレスから、ld.soのベースアドレスをリークする。
* ld.so上にあるenvironのアドレスから、スタックのアドレスをリークする。
* スタック上のREPLに移行するかどうかのフラグを書き換え、REPLに移行する
* ``run(`cat flag.txt`)``でフラグを入手
    * ``run(`/bin/sh`)``では、起動可能なプロセス数の最大値(5)を超えてしまうので、実行不可



## Flag

`fwectf{Kaerouze_ano_machikado_he_Jailbreak_ol_my_my_my_my_Julia!!!!!!!}`

