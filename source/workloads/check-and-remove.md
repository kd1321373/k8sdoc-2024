# リソースの確認と削除

ここでは、先程作っている `pod/hello-world` について、確認や削除などを行ってみます。

## リソースの確認

マニフェストで指示したリソースができているかについては、`kubectl get` コマンドで確認できます。

```bash
$ kubectl get pod/hello-world
```

````{note}
前述の通り、リソースの種別とリソース名を引数で分ける記述も可能です。好きな方を使って下さい。

```bash
$ kubectl get pods hello-world
```
````

この操作により、リソースの名前と状態などが出力されます。

```bash
$ kubectl get pod/hello-world
NAME          READY   STATUS      RESTARTS   AGE
hello-world   0/1     Completed   0          6s
```

しかし、状況によっては以下のようにあまり良くない感じにでることがあります。

```{code-block}
:emphasize-lines: 3
:language: bash

$ kubectl get pod/hello-world
NAME          READY   STATUS             RESTARTS      AGE
hello-world   0/1     CrashLoopBackOff   1 (12s ago)   24s
```

`CrashLoopBackOff` は本来、コンテナが異常終了を繰り返してしまい、安全のためコンテナの起動を一時的に停止している状態です。
しかし、今回使っているコンテナはいわゆるHello Worldのため、出力をするとコンテナが終了してしまいます。
Kubernetesでは(特別な指定をしない場合)コンテナは『起動しっぱなし』を正常とみなすため、以上と判断して再起動を繰り返す挙動になっています。いわば **正しく異常な挙動をしている** となります。

## リソースの削除

リソースを削除するのは、2つの方法があります。

### `kubectl delete` コマンド

リソースを指定して削除するために使うのが、`kubectl delete` コマンドです。

```bash
$ kubectl delete pod/hello-world
$ kubectl get pods  # ポッドの状態を取得
```

### マニフェストファイルを使う

マニフェストファイルを`kubectl apply -f`同様に行うと、記載されているリソースの削除を試みます。
前節で削除をした場合は、再度適用しておきましょう。

```bash
$ kubectl apply -f pod-hw.yml
```

改めて削除してみます。

```bash
$ kubectl delete -f pod-hw.yml
$ kubectl get pods  # ポッドの状態を取得
```

こちらでも削除できます。

```{note}
リソース削除の際、削除が実際に完了するまで待たされることがあります。
これは、Dockerの標準的な挙動において、10秒程度コンテナが終了するのに時間を要することがあるためです。
```
