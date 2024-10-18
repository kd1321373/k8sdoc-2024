# ノードポート指定

クラスタIPは、クラスタ内に専用の窓口IPを作成することで、クラスタ内のPodからアクセスできるようにしていました。
そのほかの手段として、ノードポート(NodePort)というものがあります。
これを使用すると、クラスタ外からのアクセスも可能になるという仕組みが追加されます。

```{note}
ノードポート指定をすると、前提としてクラスタIPが作成されます。
そして、ノードに外部から接続できさえすれば、指定ポートを使ったアクセスが可能になるという構造です。
```

ノードポートを指定するには、Serviceの`spec.type`を`NodePort`に変更します。
残りはクラスタIPの時と同じです。

```{literalinclude} sources/svc-mysql-nodeport.yml
:language: yaml
:name: svc-mysql-nodeport.yml
:emphasize-lines: 6
```

このマニフェストを適用すると、設定が変更されます。

```bash
$ kubectl apply -f svc-mysql-nodeport.yml
service/mysql configured
$ kubectl get svc
NAME         TYPE        CLUSTER-IP        EXTERNAL-IP   PORT(S)          AGE
kubernetes   ClusterIP   192.168.194.129   <none>        443/TCP          68m
mysql        NodePort    192.168.194.213   <none>        3306:31696/TCP   41m <-- 31696がノードポート
```

前述の通り、NodePortはClusterIPも作っているため、Pod間のアクセスは同様にホスト名(mysql)にて可能です。

```bash
$ kubectl exec -it deploy/ubuntu -- mysql -h mysql -u myuser --password=mypassword mydb
...(中略)...
mysql>      # 確認できたら抜けてください
```

その一方で、ノードのIPが取得できれば、外部からでもアクセス可能となります。

````{note}
実はDocker Desktopではこの処理が行えません。
理由は、Docker Desktopにおいて、Linuxの仮想マシンを作成してその中でK8sクラスタを構成している(=ノードも仮想マシンの内側)にあるため、直接アクセスできません。

そのため、Docker DesktopのK8s機能では、NodePort指定のサービスが入ったときに、割り当てるポート番号をlocalhostの未使用ポート番号にし、**127.0.0.1(ループバック)上でバインドして中継する**ようにしています。

```{figure} images/k8s-dockerdesktop.drawio.png
Docker Desktop(やOrbStack)が裏でやっている穴開けの概念図
```

この仕組みにより、疑似的にですがノードへのアクセスが確立するようになっています。
```bash
$ kubectl get svc
NAME         TYPE        CLUSTER-IP        EXTERNAL-IP   PORT(S)          AGE
kubernetes   ClusterIP   192.168.194.129   <none>        443/TCP          68m
mysql        NodePort    192.168.194.213   <none>        3306:31696/TCP   41m
```
であれば、 127.0.0.1:31696 へのアクセスにより、ノード内のPod(の指定ポート)に繋がるようになっています。

````

