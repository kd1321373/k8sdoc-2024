# Pod内での通信

このセクションは『コンテナ間』の話ですが、ここではPodの中での通信についてです。
Podは必要であれば**複数のコンテナを内包することができる**仕様です、そのため、Pod内のコンテナ間通信も時には必要となります。

Pod内での通信は、Pod内のコンテナ間で行われます。Pod内のコンテナは、同じネットワーク名前空間を共有しているため、localhostを使って通信することができます。
試しに2つのコンテナを内包するPodを作って確認してみましょう。

MySQLのコンテナを用意し、その脇でphpMyAdminを用意してみましょう

```{literalinclude} sources/ss-mysql-with-controller.yml
:languge: yaml
:diff: ../storage/src/ss-mysql.yml
```

````{warning}
このマニフェストを適用する時、既存のStatefulSetが存在しているとエラーになります(StatefulSetにコンテナを追加する行為は**変更としては承認されない仕様**なのです)。
そのため、一度該当するStatefulSetを削除してから再適用する必要があります。
```bash
$ kubectl delete -f ss-mysql-with-shell.yml # remove statefulset/mysql
$ kubectl apply -f ss-mysql-with-shell.yml
```
````

ついでに、NodePortで繋いでみましょう。

```{literalinclude} sources/svc-pma.yml
:languge: yaml
```

マニフェストを適用後、サービスを確認し、service/pmaにおけるNodePortを確認しておきましょう。

```bash
$ kubectl get svc pma
NAME   TYPE       CLUSTER-IP        EXTERNAL-IP   PORT(S)        AGE
pma    NodePort   192.168.194.220   <none>        80:32523/TCP   113s
```

この場合、127.0.0.1上で32523/tcpでアクセスできるようになっているので、ブラウザでアクセスすると、phpMyAdminの画面が表示されるはずです。
このように、Pod内での通信はlocalhostを使って通信することができます。

```{note}
なぜ `localhost` ではなく `127.0.0.1` なのかというと、`localhost` での接続はIPv6(`::1`)を優先してしまうため、
IPv6側での接続待ち受けに対応していないときに接続が失敗することがあるためです。
そのため、IPv4アドレスを使うことで接続ができます。

どうしても `localhost` を使いたい場合、`mysql`コマンドのオプションに`--protocol=TCP`を付けることで強制できます。
ただ逆にIPv6のTCPを明示する方法が不明なため、確実に切り分けるためにはIPベース(`127.0.0.1`か`::1`)で接続することをおすすめします。

```

