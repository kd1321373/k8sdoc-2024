# ノードポート指定

クラスタIPは、クラスタ内に専用の窓口IPを作成することで、クラスタ内のPodからアクセスできるようにしていました。
そのほかの手段として、ノードポート(NodePort)というものがあります。
これを使用すると、クラスタ外からのアクセスも可能になるという仕組みが追加されます。

ノードポート指定をすると、前提として**クラスタIPが作成**されます。
そして、ノードに外部から接続**できさえ**すれば、指定ポートを使ったアクセスが可能になるという構造です。

ノードポートを指定するには、Serviceの`spec.type`を`NodePort`に変更します。
残りはクラスタIPの時と同じです。

```{literalinclude} sources/svc-mysql-nodeport.yml
:language: yaml
:name: svc-mysql-nodeport.yml
:emphasize-lines: 6
```

このマニフェストを適用すると、設定が変更されます(ClusterIPモードであったとしても同一リソースを指定すると上書きされます)。

```bash
$ kubectl apply -f svc-mysql-nodeport.yml
service/mysql configured
$ kubectl get svc
NAME         TYPE        CLUSTER-IP        EXTERNAL-IP   PORT(S)          AGE
kubernetes   ClusterIP   192.168.194.129   <none>        443/TCP          68m
mysql        NodePort    192.168.194.213   <none>        3306:31696/TCP   41m <-- 31696がノードポート
```

前述の通り、NodePortはClusterIPも作っているため、Pod間のアクセスは同様にホスト名(mysql)にて可能です。
`kubectl port-forward`後にブラウザでpmaに繋いでもらえば、ホスト名`mysql`で同様にアクセス可能です。

その一方で、ノードのIPが取得できれば、外部からでもアクセス可能となります。

- ノードのIPを取得する方法は、`kubectl get nodes -o wide`で確認できます(OrbStack上で確認済み)
- miniKubeの場合は、`minikube ip`で取得できます

# Docker Desktopのちょっと特殊な事情

実はDocker Desktopではこの処理が行えません。

```bash
$ kubectl get nodes -o wide
NAME             STATUS   ROLES           AGE     VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE         KERNEL-VERSION    CONTAINER-RUNTIME
docker-desktop   Ready    control-plane   2d15h   v1.30.2   192.168.65.3   <none>        Docker Desktop   6.10.4-linuxkit   docker://27.2.0
```

一件取得できている(192.168.65.3)できているように見えます。
ですが、このIPアドレスに対して、外部(WindowsやmacOSホスト)からはアクセスできません。

```bash
# macOS上での実験例
$ ping -c4 -t1 192.168.65.3
PING 192.168.65.3 (192.168.65.3): 56 data bytes
ping: sendto: Host is down
ping: sendto: Host is down
Request timeout for icmp_seq 0

--- 192.168.65.3 ping statistics ---
2 packets transmitted, 0 packets received, 100.0% packet loss
```

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



