# Podの持つIPアドレスと接続実験

たとえば、MySQLのサーバーに対するPodを構築したとしましょう。
ストレージの話のところで、StatefulSet/mysqlを作っていますので、こちらを使ってみましょう。

```{literalinclude} ../storage/src/ss-mysql.yml
:language: yaml
:name: ss-mysql.yml
```

ここで、このMySQLのPodでは、IPアドレスがいくつになっているのでしょうか。
マニフェストを適用し、Podに接続してから`/etc/hosts`ファイルで確認してみましょう。

```bash
$ kubectl apply -f ss-mysql.yml
$ kubectl exec statefulset/mysql -- cat /etc/hosts
```
すると、次のような結果が返ってきます。

```
# Kubernetes-managed hosts file.
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
fe00::0 ip6-mcastprefix
fe00::1 ip6-allnodes
fe00::2 ip6-allrouters
10.1.0.10       mysql-0.mysql.default.svc.cluster.local mysql-0```
```

このように、PodのIPアドレスは`/etc/hosts`ファイルに記載されています。
今回の環境では、10.1.0.10となっていましたが、このIPアドレスは、Podが削除されると変わってしまいます。

では、対となるクライアントを考えてみましょう。
今回はphpMyAdminを使って接続することを考えてみます。リソース名は`deploy/pma`とします。

```{literalinclude} sources/deploy-pma.yml
:language: yaml
:name: deploy-pma.yml
```

```{note}
リモートのMySQLサーバに繋ぐため、オービトラリーモードに設定しています(環境変数`PMA_ARBITRARY`)
```

ここでは、以下の値を設定してみてください。

* ホスト名: `mysql`
* ユーザー名: `myuser`
* パスワード: `mypassword`


```{figure} images/pma-login-invalid-hostname.png

とりあえず接続を試行
```

```{figure} images/pma-login-error-hostname.png

当然のように失敗する
```

接続に失敗しています。どうやら「`mysql`という名前のホストが見つからない」ということにようです。
先程調べたIPアドレスを使って接続してみたらどうでしょうか。先程見つけておいた、**10.1.0.10**というアドレス(自分の環境で調べたものに置き換えてくださいね)を使ってみましょう。

```{figure} images/pma-login-using-pod-ip.png

控えておいたIPでは?
```

こちらなら無事にログインできます。

```{figure} images/pma-login-with-pod-ip.png

こちらはうまくいく
```


今度は接続できました。このように、Pod同士の接続は**Podの持つIPアドレス**を使って行います。
しかし、このPodの持つIPアドレスは固定とはなりません。Podが再生成されるようなことがあると、番号が変わってしまいます。
たとえば、MySQLのPodを一度削除して、オートヒーリングの力で再生成させてみましょう。


```bash
$ kubectl get pods # mysqlのPodの名前を確認
NAME                      READY   STATUS    RESTARTS        AGE
mysql-0                   1/1     Running   1 (8m31s ago)   18m
pma-59fc478f7b-gcndn   1/1     Running   1 (8m31s ago)   11m
$ kubectl delete pod mysql-0 # 該当するPodを削除
pod "mysql-0" deleted
$ kubectl get pods # mysqlのPodが再生成されていることを確認
NAME                      READY   STATUS    RESTARTS        AGE
pma-59fc478f7b-gcndn   1/1     Running   1 (9m14s ago)   12m
mysql-0                   1/1     Running   0               4s
$ kubectl exec -it statefulset/mysql -- cat /etc/hosts # IPアドレスを確認(再び)
# Kubernetes-managed hosts file.
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
fe00::0 ip6-mcastprefix
fe00::1 ip6-allnodes
fe00::2 ip6-allrouters
10.1.0.16       mysql-0.mysql.default.svc.cluster.local mysql-0
```

と、今度は10.1.0.16という風に変わってしまいました。
つまり**Pod間での接続に直接相手のIPアドレスを使うことは現実的とは言えません**。
この問題、どうしたら解決できるでしょうか。

