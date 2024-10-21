# Pod内での通信

このセクションは『コンテナ間』の話ですが、ここではPodの中での通信についてです。
Podは必要であれば**複数のコンテナを内包することができる**仕様です、そのため、Pod内のコンテナ間通信も時には必要となります。

Pod内での通信は、Pod内のコンテナ間で行われます。Pod内のコンテナは、同じネットワーク名前空間を共有しているため、localhostを使って通信することができます。
試しに2つのコンテナを内包するPodを作って確認してみましょう。

以前使っている`ss-mysql.yml`のマニフェスト(StatefulSet/mysql)に、ポッド内コンテナを[ひとつ](sources/ss-mysql-with-shell.yml)足してみます。

```{literalinclude} sources/ss-mysql-with-shell.yml
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

shellコンテナを呼び出して、パッケージを追加してからmysql側に接続してみます。

```bash
$ kubectl exec -it statefulset/mysql -c shell -- sh
# apk add --no-cache mariadb-connector-c-dev mariadb-client
# mysql -u myuser --password=mypassword -h mysql mydb
MySQL>      <-- 接続できた(exitしておきましょう `\q`)
```

上記の操作では、接続先を`mysql`としました。これはClusterIPによるホスト名を用いています。
実はPod内では、各コンテナ同じIPを所有しているため、localhostによる接続が可能です。
参考までに各コンテナのIPを確認してみると以下のようになります(試したい方は一度shellコンテナから抜けて行いましょう)。

```bash
kubectl exec -it statefulset/mysql -c mysql -- cat /etc/hosts  # <-- MySQLコンテナ側
# Kubernetes-managed hosts file.
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
fe00::0 ip6-mcastprefix
fe00::1 ip6-allnodes
fe00::2 ip6-allrouters
10.1.0.35       mysql-0.mysql.default.svc.cluster.local mysql-0
$ kubectl exec -it statefulset/mysql -c shell -- cat /etc/hosts  # <-- シェルコンテナ側
# Kubernetes-managed hosts file.
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
fe00::0 ip6-mcastprefix
fe00::1 ip6-allnodes
fe00::2 ip6-allrouters
10.1.0.35       mysql-0.mysql.default.svc.cluster.local mysql-0
```

このことから、同一ホスト上であることもわかるため、localhost(ただしIPベースなので127.0.0.1)を使った通信も確立します。

```bash
# shellコンテナに接続した状態での操作です
/ # mysql -u myuser --password=mypassword -h 127.0.0.1 mydb
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 9
Server version: 8.4.3 MySQL Community Server - GPL

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [mydb]>     # <-- 接続できた(exitしておきましょう `\q`)
```

このように、Pod内での通信はlocalhostを使って通信することができます。

```{note}
なぜ `localhost` ではなく `127.0.0.1` なのかというと、`localhost` での接続はIPv6(`::1`)を優先してしまうため、
IPv6側での接続待ち受けに対応していないときに接続が失敗することがあるためです。
そのため、IPv4アドレスを使うことで接続ができます。

どうしても `localhost` を使いたい場合、`mysql`コマンドのオプションに`--protocol=TCP`を付けることで強制できます。
ただ逆にIPv6のTCPを明示する方法が不明なため、確実に切り分けるためにはIPベース(`127.0.0.1`か`::1`)で接続することをおすすめします。

```

この仕組みを利用すると、**MySQLとphpMyAdminが同居するPod**が作れます。
是非試してみましょう。

- Statefulsetにてmysql-pmaを作成する
  - `ss-mysql.yml`をコピーして実装する
  - pma側はArbitraryの設定は不要となり、ローカルでの接続になるように変数を設定すれば良い
- サービスリソースはそのままでおそらくOK
- このPodは有用かどうかを少し考えてみましょう


