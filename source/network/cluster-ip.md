# クラスタIP

PodのIPアドレスは固定ではないということがわかりました。
ではどうするといいのでしょうか?
より大枠で固定させるための方法として、クラスタIPというのがあります。
これは、Serviceというリソースを使って、Podに対して固定のIPアドレスを割り当てる方法です。

K8sでは、ノードの集合をクラスタ(cluster; 集合体)として扱います。
このクラスタに対して、IPアドレスを割り当てることができ、これはクラスタが存続する限りは固定とみなせます。
このIPアドレスをクラスタIPと呼びます。

クラスタIPを作るには、Serviceというリソースを使います。
こちらもスニペット(`svc`といった具合に入れれば出ます)から作成できるので、試してみましょう。

```{literalinclude} sources/svc-snippet.yml
:language: yaml
:name: svc-snippet.yml
```

ここから少し書き換えて実際に使えるサービスにしてみます。

```{literalinclude} sources/svc-mysql.yml
:language: yaml
:name: svc-mysql.yml
```

参考: 変更点はこちら

```{literalinclude} sources/svc-mysql.yml
:language: yaml
:diff: sources/svc-snippet.yml
```

このマニフェストを適用し、service/mysqlを作って、確認してみましょう。

```bash
$ kubectl apply -f svc-mysql.yml
$ kubectl get svc
NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP    18h
mysql        ClusterIP   10.101.218.244   <none>        3306/TCP   6s
```

```{note}
先客として`kubernetes`というサービスがありますが、これはK8sのクラスタを指すものです。
ここでは無視しておいてください。
```

今回の環境では、mysqlというサービスに対して、クラスタIP 10.101.218.244が割り当てられました。
実際にこのアドレスで接続できるか、pmaから繋いでみます。

```{figure} images/pma-connect-with-clusterip.png

ClusterIPの値でログイン
```

```{figure} images/pma-login-with-clusterip-result.png

ログインできた
```

たしかに接続できましたね。

### どうしてこうなるの?

細かく見ておきましょう。

- `metadata.name`: サービスの名前
- `spec.selector`: どのPodに対してサービスを提供するか
  - ここでは`app: mysql`としているので、`app=mysql`というラベルを持つPodに対してサービスを提供します
- `spec.type`: サービスの形式、ここでは`ClusterIP`を設定しています
- `spec.ports`: サービスが提供するポート
  - `port`: サービスが提供するポート
  - `targetPort`: Podが提供するポート

これを図式すると、以下のようになります。

```{figure} images/cluster-ip.drawio.png
ClusterIPによる接続図
```

もちろん、Pod同士での接続はIPレベルでは可能(図中破線の矢印)です。しかし、PodのIPは固定されないため、クラスタIPを使って固定のIPを割り当てることにより、安定した接続が可能となります。

さらに、このクラスタIPは、クラスタの中で用意されている**DNSサーバーによって名前解決が可能**となっています。これはマニフェスト上では`metadata.name`で指定されているものとなっています。**今回の設定では`mysql`となっていた**ので、この名前でも接続可能です。

```{note}
一度pmaでログアウトして、IPアドレスの代わりにホスト名(`mysql`)でのログインをしてみてください。
ClusterIP設定の今であれば接続可能です。
```

このように、クラスタIPを使うことで、Pod同士の接続を安定させることができます。

````{note}
いちいちクラスタIPというPodの外のIPを使うのって遠回りなのでは? と思うかもしれません。
でもこれはたまたま今回の環境がこうなっているだけです。たとえばノードが複数存在するときもあるわけで、その時も含めて違和感なく接続できるようにするためにこのような形式になっているのです。
```{figure} images/cluster-ip-2nodes.drawio.png
クラスタ内にノードが複数あるケースとClusterIP
```
````
