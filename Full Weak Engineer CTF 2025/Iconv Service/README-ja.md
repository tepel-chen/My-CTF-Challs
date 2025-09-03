# Iconv Service

## 問題文

"Chaining iconv filters in pwn… but not in PHP?” - anonymous web CTF player

## Writeup


脆弱性は以下の箇所にある。

```c
    int src, dst;
    char from[32], to[32];
    printf("Source index (0-2) > ");
    scanf("%d", &src);
    printf("Destination index (0-2) > ");
    scanf("%d", &dst);
    printf("From encoding > ");
    scanf("%31s", from);
    printf("To encoding > ");
    scanf("%31s", to);
```

srcとdstのインデックスのチェックが無いため、範囲外のデータを変換したり、範囲外にデータを送ることが可能である。ただし、inputやoutputコマンドではインデックスのチェックが行われているため、範囲外のデータを出力するには、一度範囲内にコピーする必要がある。

ただし、`buf[3]`から`buf[0]`にコピーしようとすると、`buf[3].left`の値が大きすぎるため、次のようなエラーになる。

```
1: input | 2: output | 3: convert | 4: exit
> 3
Source index (0-2) > 3
Destination index (0-2) > 0
From encoding > LATIN1
To encoding > LATIN1
iconv: Argument list too long
```

これを回避するため、次の箇所の実装エラーを利用する。

```c
    char *outptr = bufs[dst].buf;
    bufs[dst].left = BUFF_SIZE;

    size_t res = iconv(cd, &inptr, &(bufs[src].left), &outptr, &(bufs[dst].left));
    if (res == (size_t)-1) {
        perror("iconv");
    } else {
        bufs[dst].left = BUFF_SIZE - bufs[dst].left;
    }
```

`bufs[dst].left = BUFF_SIZE`のように初期化するが、iconvに失敗した場合、`bufs[dst].left`がリセットされずに残る。したがって、最初のバイトでエンコーディングに失敗した場合、`bufs[dst].left`は`BUFF_SIZE`のままである。これを発生させるためには、例えば、エンコーディングをUTF-8に設定し、`bufs[src].buf`にUTF-8として不正なバイトを入力すればよい。

また、iconvを利用した変換について、`LATIN1`のようにどのようなバイトでもエラーにならないエンコーディングを利用することにより、範囲外のメモリをそのまま範囲内にコピーすることができる。

以上を利用して、以下のステップで任意コード実行を行う。
* `bufs[3].left`を正常な値にする。
* `bufs[3].buf`を`bufs[0].buf`に`LATIN1`を利用してコピーする。
* `bufs[3].buf`にはスタックカナリアの値が含まれている。スタックカナリアの直前までを非ヌルのバイトで埋めることにより、`printf`で`buf[0].buf`を出力すると、スタックカナリアの値がリークする。
* 同様に`bufs[3].buf`にはlibc上のアドレスも含まれているので、それもリークする。
* `bufs[0].buf`にROPのペイロードとスタックカナリアを書き込み、`buf[3].buf`にコピーする。
* ROPによりRCEが可能になる


## Flag

`fwectf{C0nv_75uyu_h4_y4m454}`

