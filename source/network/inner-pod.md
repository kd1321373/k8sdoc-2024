# Pod内での通信

Pod内での通信は、Pod内のコンテナ間で行われます。Pod内のコンテナは、同じネットワーク名前空間を共有しているため、localhostを使って通信することができます。
試しに2つのコンテナを内包するPodを作って確認してみましょう。

```{literalinclude} sources/mysql-and-controller.yml
:language: yaml
:name: mysql-and-controller.yml
```

このマニフェストを適用して、Pod状態を確認してください。
起動確認後、ポッド内コンテナに接続して、通信の確認をしてみます。

```shell
PS> kubectl exec -it mysql-and-controller -c controller -- sh
# apk update
# apk add mariadb-client mariadb-connector-c-dev
# mysql -u root -h 127.0.0.1 -p # マニフェスト記載のroot用パスワードを入力
```
