# ライブネスプローブ

ライブネスプローブは、いわゆるハートビートとも呼ばれる死活監視を提供する機能として認識していればOKです。

- 一定時間ごとに確認操作を行う
- 成功していれば特に問題無し
- 失敗した場合、そのコンテナを破棄して再起動します
  - 一発で再起動することもありますし、一定回数失敗で再起動することもあります

この機能により、コンテナが停止している状態を検知し、自動で復旧することが可能です。

## 下ごしらえ: そんなWebサーバーを用意する

実際に動いているアプリケーションに頻繁に壊れられても困るので、ここでは簡単なWebサーバーを用意します。
PythonでFlaskを用いたサーバーコードです。

```{literalinclude} src/failweb/web/server.py
:language: Python
:name: server.py
```

このコードは、`/`にアクセスすると`Hello, World!`と返すだけのシンプルなWebサーバーです。
ただし、ハートビートとして `/healthz` にアクセスすると、以下の挙動が発生します。

1. カウンターを内部で用意し、`/healthz`にアクセスするたびに増えていきます
2. カウンターの値をパーセンテージとみなし、確率により成功と失敗が発生します
3. 成功した場合はステータスコード200(OK)を、失敗した場合はステータスコード500(Internal Server Error)を返します

このコードを組み込んだDockerイメージとして、 densukest/failweb:v1 イメージをDocker Hubに用意したので、こちらを使って検証してみましょう。

```bash
$ docker run --name failweb --rm -p 8080:80 densukest/failweb:v1
```

待機状態になるので別の端末で`curl`で検証してみます。

```bash
$ curl 127.0.0.1:8080       # / -> Hello, World!
Hello, World!

$ curl 127.0.0.1:8080/healthz  # ハートビート起動
OK 2
$ curl 127.0.0.1:8080/healthz
OK 4
...
$ curl 127.0.0.1:8080/healthz
Server Error 6                  # 失敗(6%を引いたのは悪くない)
```

呼び出しを繰り返すほどに失敗の確率が上がっていきます。
ここまで露骨に上がることは現実にはないと思いますが、サーバーの中で状態を持つようなアプリケーションの場合、当初の想定と徐々に挙動が異なっていくことがあるために似たようなことは起こりえます。それを雑に模倣したのが今回のコードになっています。

## デプロイメントとサービスを用意する

では、このイメージを利用するデプロイメントおよびアクセス用にサービスを用意してみましょう。

```{literalinclude} src/failweb/deploy-failweb.yml
:language: yaml
```

そして、ノードポートを使ってアクセスできるようにサービスを用意します。

```{literalinclude} src/failweb/service-failweb.yml
:language: yaml
```

両マニフェストを適用し、アクセスポートを確認してみましょう。

```bash
$ kubectl apply -f deploy-failweb.yml -f service-failweb.yml
$ kubectl get svc failweb
NAME      TYPE       CLUSTER-IP        EXTERNAL-IP   PORT(S)        AGE
failweb   NodePort   192.168.194.199   <none>        80:31062/TCP   58s
```

今回は31062に割り当てられたようなので、実際にアクセスして確認してみましょう。

```bash
$ curl localhost:31062  # まずは通常
Hello, World!
```

では、ハートビートチェックをしてみましょう。繰り返さないとエラーが出ないので運試しです。
```bash
$ curl localhost:31062/healthz
OK 2%
$ curl localhost:31062/healthz
OK 4%
...
$ curl localhost:31062/healthz
Server Error 44%
```

なんと今回は20回ほど試行する必要がありました、運が向上した?!

このように、アクセスしているうちにおかしくなっていくような気がするサービスができました。

## ライブネスプローブの導入

ではプローブを導入してみましょう。Webサービス(?)なので、ここでは`httpdGet`を使ってみましょう。

```{literalinclude} src/failweb/deploy-failweb-lp.yml
:diff: src/failweb/deploy-failweb.yml
:language: yaml
```

※ 全体を見たい方は、[ソース](src/failweb/deploy-failweb-lp.yml)を確認してください。

リーディネスプローブと大きな違いはありませんが、`httpGet`を使っている点が異なります。

- `httpGet`: Webページへのアクセスにてテストする宣言
  - `port`: アクセスするポート番号(省略すれば80/tcp)
  - `path`: アクセスするパス(省略すれば`/`)
    - 今回は `/healthz` へアクセスしています
- failureThreshold: 失敗回数の許容値
  - 今回は3回失敗したら再起動するように設定しています

このマニフェストが適用されると、最初の街時間以降、1秒ごとにハートビートへリクエストを送り続けます。
そのうち失敗確率が上がり、3回失敗した時点でコンテナが破棄されてポッド内での再起動が確認されます。
この様子は、`kubectl get pods`もしくは`kubectl events -w`で確認できます。

```bash
$ kubectl events -w
...
13s         Normal    Started             pod/failweb-6c7496cd6f-94xkd    Started container failweb
3s          Warning   Unhealthy           pod/failweb-6c7496cd6f-94xkd    Liveness probe failed: HTTP probe failed with statuscode: 500
0s          Warning   Unhealthy           pod/failweb-6c7496cd6f-94xkd    Liveness probe failed: HTTP probe failed with statuscode: 500
...
```

そのうち再起動が発生するので、適宜止めて、ポッド状態も確認してみましょう。

```
$ kubectl get pods
NAME                       READY   STATUS    RESTARTS      AGE
failweb-6c7496cd6f-94xkd   1/1     Running   5 (37s ago)   5m7s
```

見ての通りで、再起動回数がいつの間にか5回となっていました。

```{note}
なお、今回の設定ではKubernetesにおける「短時間で再起動回数が多すぎる」というしきい値に引っかかることがあります。
引っかかった場合、CrashLoopBackOff状態となり、一定時間起動が待機させられてしまいます。
なったらなったで諦めて少し待ちましょう(30〜1分程度)
```

## まとめ

ライブネスプローブ(ハートビート)は、コンテナの死活監視を行います。
サーバーが起動しっぱなしにより、当初想定してた安定状態ではなくなっていくこともありますので
このような方法で監視を行い、自動で再起動を行わせることは重要です。

サービスとしてハートビートも提供し、裏で自己チェックを行う仕組みを作ることも重要です。

- サービス提供時間(レスポンス提供までのトリップタイム)をモニターしておいて、一定水準を超えていないかを常時確認しておく
- メモリ状態が想定外の変化になっていないかを確認しておく
- ディスク容量や使用メモリ量が本番稼働前に測定していたしきい値を超えていないかをチェックする
  - 過剰なキャッシュなどが原因かもしれないので、キャッシュ破棄コマンドを組み込むのも有効かもしれません

もちろんハートビート以前にも、勝手にクラッシュする可能性だってありますよね。

- メモリを使い過ぎて制限値を超えた(メモリ確保ができなくなったアプリケーションは大抵クラッシュします)
- ストレージを使い果たした(ログファイルなども関わるかもしれません)
- 数学的なミス(0除算など)

いずれにしても、クラッシュすることはある程度織り込み済みにして、その兆候を早く捉えて対処することが必要です。

```{note}
今回Python版の『徐々にエラーになるサンプル』を出しましたが、本当はRustで書きたかった(一応動くが問題があった)ので、
泣く泣くPythonにした次第です…
```

```{note}
なお、バックオフは初回の発生時は10秒、その後2倍で増加していきます。
実際のサービスでこんな頻繁に落ちてはおかしいでしょうから、とりあえずしのいでくれてるこの間に原因特定して更新できるようにしましょう。
```

