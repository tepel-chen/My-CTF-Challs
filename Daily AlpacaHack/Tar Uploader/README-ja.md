# Tar Uploader

[English](./README.md)

## 問題文

Tarでくれ (麻呂AA省略)

### 初心者向けヒント: つまりやすいポイント

- pythonのバージョンによっては、サーバーと異なる挙動をすることがあります。3.13で実験してください。
- nobodyユーザーはほとんどのディレクトリやファイルへの書き込みを制限されます。したがって、実行ファイルや依存ファイルの上書きによるRCEは難しくなっています。

## Writeup

この問題の目標は `/flag.txt` を読むことです。サーバーは、アップロードされた tar ファイルを `archive.extractall` で展開します。

tar アーカイブにはシンボリックリンクを含めることができます。Python 3.13 の `archive.extractall` では、そのリンクを展開先ディレクトリの外にあるファイルやディレクトリへ向けることができます。

次のようにアーカイブを作成してサーバーにアップロードすると、`http://<DOMAIN>/static/<UUID>/flag.txt` でそのファイルにアクセスできます。

```bash
ln -s /flag.txt flag.txt
tar cvf test.tar flag.txt
```

Python で tar ファイルを作ることもできます。詳しくは [solve.py](./solution/solve.py) を参照してください。

## フラグ

`Alpaca{t4r_syml1nk_at7ack_1s_mit1g4ted_in_3.14}`
