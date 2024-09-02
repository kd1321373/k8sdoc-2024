# httpdを立ててみる

まず、簡単なところでhttpd(Webサーバー)を立ててみましょう。

## おさらい: Dockerでのはどうやった?

Dockerのレベルで考えれば、以下の操作でコンテを立ち上げることになります。

```bash
$ docker run -p 8080:80 httpd
```

これで、 http://127.0.0.1:8080/ でApacheのhttpdによるデフォルトページが起動するはずです。

```{figure} images/docker-httpd-result.png
Docker上で普通に立ち上げたシンプルなWebサーバー
```

```{warning}
ページ確認後、`Ctrl+C`で停止しておいてください。さもないと、同一ポートで待ち受け状態に使用を試みるアプリケーションに支障が出ます。
```

