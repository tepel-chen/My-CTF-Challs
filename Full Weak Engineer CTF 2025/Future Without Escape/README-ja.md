# Future Without Escape

## 問題文

There will be no exit

## Writeup

[このUAF](https://github.com/python/cpython/issues/126405)を利用する。

UAFが発生した段階で、長さ15バイトのbyteオブジェクトを作成すると、UAFされた箇所にそのバイトが書き込まれる。UAFが発生した箇所には次のような`PyObject`構造体が期待されている。([参考](https://github.com/python/cpython/blob/c22cc8fccdd299fa923f04e253a3f7c59ce88bfe/Include/object.h#L125))

```c
typedef struct _object {  
    Py_ssize_t ob_refcnt;
    struct _typeobject *ob_type;
} PyObject;
```

そして、UAFが発生した後に、[`do_richcompare`](https://github.com/python/cpython/blob/ab2a3dda1d3b6668162a847bf5b6aca2855a3416/Objects/object.c#L1044)にて`Py_TYPE(w)->tp_richcompare`が実行される。都合が良いことに、この時の第一引数(=rdi)はオブジェクト自身となるため、`tp_richcompare`が`plt.system`に、rdiが`/bin/sh\0`の文字列への参照になるように`PyObject`と`PyTypeObject`を偽装することで、`system("/bin/sh")`が実行され、RCEとなる。

このpythonのバージョンはPIEが有効なため、`plt.system`のアドレスを固定的に知ることはできない。小さいint型の値が起動時に[`.data`に確保される](https://github.com/python/cpython/blob/3cfab449ab1e3c1472d2a33dc3fae3dc06c39f7b/Include/internal/pycore_runtime_structs.h#L121)するため`id(1)`が`.data`上の固定の場所をあらわすことを利用し、libpythonのベースアドレスを計算することで、`plt.system`のアドレスを計算することができる。

## 謝辞

pwnではない解法がないように、プレイテストをしてくださったoh_wordさんに感謝いたします。

## Flag

`fwectf{7h3_fu7ur3_574r75_70d4y_n07_70m0rr0w}`

