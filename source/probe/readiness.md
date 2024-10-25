# リーディネスプローブ

リーディネスプローブは、アプリケーションがリクエストを処理できる状態になっているかどうかを確認するために使用されます。リーディネスプローブは、アプリケーションがリクエストを処理できる状態になるまで待機することができます。

たとえば、以下のようなシチュエーションが考えられると思います。

- バックエンドでDBに接続するようなアプリケーションが、DBに接続できるまで待機する
- DB自身が接続可能になるまで待機する
- Webサーバーがコンテンツの配信が完了するまで待機する

ここでは、以下を想定してみます。

- データベースのPodがある
- データベースの起動までは時間がかかる

簡単なMySQLのPodを作成してみます。

```{literalinclude} src/pod-mysql-nowait.yml
:language: yaml
:name: pod-mysql-nowait.yml
```

MySQLの公式イメージでは、Podが稼働してからMySQLが起動するまでに、大雑把に以下の行程を踏んでいます。

1. 仮のMySQLサーバーを起動
2. データベースの初期化
3. 管理者パスワードの設定(`MYSQL_ROOT_PASSWORD`もしくは`MYSQL_RANDOM_ROOT_PASSWORD`)
4. 初期データベースおよびアクセスアカウントの作成(`MYSQL_DATABASE/USER/PASSWORD`)
5. 仮サーバーの終了
6. 本サーバーの起動 → 待機状態(ここで利用可能になる)

実際に起動中の様子を見るためには、マニフェスト適用の直後にログを出すことが重要です。
遅れると途中からになってしまうので、`;`を使って繋いですぐに出すようにしてみましょう。

少し長くなりますが、以下のようになります。
```bash
# macOS環境での実行例: 適用後に1秒待つのは、Podが立ち上がるまでの時間を考慮しています
$ kubectl apply -f pod-mysql-nowait.yml; sleep 1; kubectl logs pod/mysql-nowait --follow
pod/mysql-nowait created
2024-10-24 23:36:32+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.4.3-1.el9 started.
2024-10-24 23:36:33+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
2024-10-24 23:36:33+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 8.4.3-1.el9 started.
2024-10-24 23:36:34+00:00 [Note] [Entrypoint]: Initializing database files
2024-10-24T23:36:34.382862Z 0 [System] [MY-015017] [Server] MySQL Server Initialization - start. # 仮サーバー起動→各種初期化
2024-10-24T23:36:34.384383Z 0 [System] [MY-013169] [Server] /usr/sbin/mysqld (mysqld 8.4.3) initializing of server in progress as process 80
2024-10-24T23:36:34.413645Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
2024-10-24T23:36:35.496542Z 1 [System] [MY-013577] [InnoDB] InnoDB initialization has ended.
(中略)
2024-10-24 23:37:00+00:00 [Note] [Entrypoint]: Stopping temporary server
2024-10-24T23:37:00.420146Z 13 [System] [MY-013172] [Server] Received SHUTDOWN from user root. Shutting down mysqld (Version: 8.4.3).
2024-10-24T23:37:01.702739Z 0 [System] [MY-010910] [Server] /usr/sbin/mysqld: Shutdown complete (mysqld 8.4.3)  MySQL Community Server - GPL.
2024-10-24T23:37:01.702771Z 0 [System] [MY-015016] [Server] MySQL Server - end.
2024-10-24 23:37:02+00:00 [Note] [Entrypoint]: Temporary server stopped

2024-10-24 23:37:02+00:00 [Note] [Entrypoint]: MySQL init process done. Ready for start up.

2024-10-24T23:37:02.472610Z 0 [System] [MY-015015] [Server] MySQL Server - start. # 本サーバー起動
2024-10-24T23:37:02.746586Z 0 [System] [MY-010116] [Server] /usr/sbin/mysqld (mysqld 8.4.3) starting as process 1
2024-10-24T23:37:02.775622Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
2024-10-24T23:37:04.099598Z 1 [System] [MY-013577] [InnoDB] InnoDB initialization has ended.
(中略)
2024-10-24T23:37:05.216810Z 0 [System] [MY-011323] [Server] X Plugin ready for connections. Bind-address: '::' port: 33060, socket: /var/run/mysqld/mysqlx.sock
2024-10-24T23:37:05.216922Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.4.3'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
```

実験環境では、仮サーバー起動〜本番サーバーの起動(実際に使える状態になる)まで、約30秒かかりました。
Podの立場からはこの状況を把握することはできず、コンテナが起動中であるためにRunningですが、他のコンテナからアクセスされると困る状況です。実際には(接続できないのに)Ready側が即座に1/1という状況です。

そこで、リーディネスプローブを準備してみます。
リーディネスプローブを含むプローブでは、いくつかの手法でアプリケーションの状態を確認することができます。

- コマンドを実行してみる(戻り値で判断)
- HTTPリクエストを送ってみる(ステータスコードで判断)
- TCPソケットを開いてみる(接続できるかで判断)
- ファイルの存在を確認してみる(存在するかで判断) 等

ここでは、MySQLの`mysqladmin`コマンドを使って、MySQLが起動しているかどうかを確認する方法を試してみます。
コマンドライン的には以下のように走らせます。

```bash
$ mysqladmin ping -u root --password=password -h 127.0.0.1
```

これをリーディネスプローブとして設定すると、マニフェストは以下のようになります。

```{literalinclude} src/pod-mysql-readinessprobe.yml
:language: yaml
:name: pod-mysql-readinessprobe.yml
:diff: src/pod-mysql-nowait.yml
```
※ 全体のマニフェストはこちらから --> [pod-mysql-readinessprobe.yml](src/pod-mysql-readinessprobe.yml)

- `exec`: コマンドを実行する
  - `command`: 実行するコマンドライン(配列渡し)
- initialDelaySeconds: コンテナが起動してから最初に実行するまでの秒数
- periodSeconds: チェックを行う間隔(一度実行した後に指定秒間待つ)
- timeoutSeconds: タイムアウトまでの秒数

これにより、ポッドが外部からのコネクションが可能になる状態まで、ポッド状態としては0/1の状態となります。
