# オートヒーリング

K8sを使うことによる恩恵として、オートヒーリング機構があります。
起動するものがコンテナであるため、ベースのイメージが同じならば同じ状況で起動することが期待できます。
ですので、コンテナが消失しても、それを検出すれば適当に再起動するという仕組みです。

実際に簡単な操作で確認してみましょう(細かいことをやり出すといろいろ面倒)。

## Dockerレベルでコンテナを消してオートヒーリングを見てみる

Dockerレベルで中をのぞき見してみます。
Docker Desktopでは、K8sがDockerのコンテナシステムを共有しているため、のぞき見できます。

```bash
$ docker ps
CONTAINER ID   IMAGE                                                                            COMMAND                   CREATED          STATUS          PORTS     NAMES
d2f4b4b24c70   a49fd2c04c02                                                                     "httpd-foreground"        2 seconds ago    Up 1 second               k8s_httpd_httpd-6f8c7bfc4f-pr5f6_default_b52f19ae-4a37-4288-9945-1148197386b0_0
c24c9410e83f   vsc--1a61b0efe717089ad9e5ae76b5563a1f36e0d5ec46e004348c31f0fb42ed5136-features   "/bin/sh -c 'echo Co…"   20 minutes ago   Up 20 minutes             awesome_swartz
```

これはあくまで一例ですが、`k8s_httpd_httpd-なんちゃら` というすごい長い名前のコンテナが稼働状態にあると思います。
このコンテナを消してみましょう。コンテナ名をターミナル上でコピーしてから行います。

```bash
$ docker container rm -f k8s_httpd_httpd-6f8c7bfc4f-pr5f6_default_b52f19ae-4a37-4288-9945-1148197386b0_0
$ docker ps
CONTAINER ID   IMAGE                                                                            COMMAND                   CREATED          STATUS          PORTS     NAMES
430bad028acd   a49fd2c04c02                                                                     "httpd-foreground"        2 seconds ago    Up 1 second               k8s_httpd_httpd-6f8c7bfc4f-pr5f6_default_b52f19ae-4a37-4288-9945-1148197386b0_1
c24c9410e83f   vsc--1a61b0efe717089ad9e5ae76b5563a1f36e0d5ec46e004348c31f0fb42ed5136-features   "/bin/sh -c 'echo Co…"   22 minutes ago   Up 22 minutes             awesome_swartz
```

地味ですが、変わったことに気づきましたか(末尾0→1)。
K8sが消失したコンテナを検知し、適切に再起動してくれていることがわかります。

k8sのレベルで見るとすれば、ポッド(Pod)という単位で見ることになります。

```bash
$ kubectl get pods
NAME                     READY   STATUS    RESTARTS   AGE
httpd-6f8c7bfc4f-pr5f6   1/1     Running   1          3m1s
```

RESTARTSが1と出ています、これは今コンテナを強制的に消したことによる再起動がカウントされているからです。
ポッドがほぼコンテナと思って大丈夫です(今のうちは)。

ポッドのレベルで消すと、関連するコンテナが破棄されます(その結果再起動も発生する)。

```bash
$ kubectl delete pod httpd-6f8c7bfc4f-pr5f6
$ kubectl get pods
NAME                     READY   STATUS    RESTARTS   AGE
httpd-6f8c7bfc4f-rnzdp   1/1     Running   0          21s
```

RESTARTSが0に戻ってしまいました、これはポッドそのものが消失したことで、新しいポッドが再生成されたためです(ポッドのIDが前と変わっている)。
いずれにしても、オートヒーリングにより、コンテナに繋がる部分が適宜再起動してくれることがわかります。

