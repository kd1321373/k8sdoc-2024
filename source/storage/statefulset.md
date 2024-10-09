# ストレージを伴うPod

ストレージを必要とするPodは、データベースやキャッシュのサーバーという形で利用されることが多いです。
では、DeploymentとPVCの組み合わせで実際に作ってみましょう。

* MySQLの起動するPodを管理するDeploymentを作成
* MySQLのデータを保存するためのPVCを作成

という構成になります。

## DeploymentによるMySQLのPodの作成

まずは、MySQLのPodを管理するDeploymentを作成します。
ここでは他と混ざらないように、`deploy-mysql`というディレクトリを用意して、その中で作業を行います。

```{literalinclude} src/deploy-mysql/mysql.yml
:language: yaml
:name: deploy-mysql/mysql.yml
```

こちらを適用すると、`deploy/mysql`が作成されますが、一行に起動待ちの状態になります。

```{note}
なぜでしょうか?
Pod状態を確認してみましょう。

`kubectl events` で取得するといいでしょう。
```

続いて、PVCを作成します。

```{literalinclude} src/deploy-mysql/pvc.yml
:language: yaml
:name: deploy-mysql/pvc.yml
```

こちらも適用すると、`pvc/mysql-pvc`が作成されます。
この名前で`deploy/mysql`が待ち受けていますので、少し後に検出されて該当Podが起動に入れます。

````{note}
実は今回ディレクトリを用意して二つのマニフェストを作成しました。
これは、`kubectl`を使うときに少し楽になります。
`-f`でディレクトリを渡した場合、そのディレクトリ直下のYAMLファイルを全て適用します。

```bash
# deploy-mysqlディレクトリ内の全てのYAMLファイルを適用
$ kubectl apply -f deploy-mysql
...
# deploy-mysqlディレクトリ内の全てのYAMLファイルで適用されるリソースを削除
$ kubectl delete -f deploy-mysql
```
````

では、この状態でスケールアウトしてみるとどうなるでしょうか?

```pwsh
PS> kubectl scale deployment/mysql --replicas=2
PS> kubectl get deploy
PS> kubectl get pods
PS> kubectl get pvc # けっこう危険なことになってます
NAME         STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
mysql-pvc    Bound    pvc-8ecd68aa   512Mi      RWO            standard       <unset>                 43s
```

PVCが1つしかないのに、Podが2つ起動してしまいました。ということは二つのPodが同じPVCをマウントしていることになりました。
データベースでこのような状態は動作の保証がなされませんので、このような状態は避けるべきです。
つまり、それぞれにPVCの割り当てをしなくてはいけませんが、どうしたらいいのでしょうか… となってしまいます。

## StatefulSet

そこで登場するのが**StatefulSet**です。StatefulSetは、Podと付随するストレージを一緒に管理できるリソースになっています。

StatefulSetはDeploymentと似ていますが、以下のような特徴があります。

- Podに順序を持たせることができます
  - Deploymentでは生成される(レプリケーションされる)Podに順序の保証がありません
  - StatefulSetではPodの名前にインデックスが付与され、その順序が保証されます
    - 最初のものは普通は0、次は1、という具合です
    - レプリケーションが発生したときも基本的にこの順番となります
- 付随するストレージも一緒に管理できます
  - DeploymentではPodとPVCは別々に管理されます
  - StatefulSetではPodとPVCが一緒に管理されます
    - Podの名前にインデックスが付与されるので、それに合わせてPVCも作成されます

StatefulSetを使ってMySQLを作成してみましょう。

```{literalinclude} src/ss-mysql.yml
:language: yaml
:name: ss-mysql.yml
```

これを適用すると、`statefulset.apps/mysql`リソースが作成されます。
そして、定義されたPVCが作成され、そのPVCによってPodが起動されます。

```pwsh
PS> kubectl apply -f ss-mysql.yml
statefulset.apps/mysql created

PS> kubectl get pods
NAME      READY   STATUS    RESTARTS   AGE
mysql-0   0/1     Pending   0          3s   # PVC割り当て待ち
...
PS> kubectl get pods
NAME      READY   STATUS    RESTARTS   AGE
mysql-0   1/1     Running   0          6s   # 割り当て後起動する

PS> kubectl get pvc
NAME         STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
db-mysql-0   Bound    pvc-5a8c9e2d(略)   256Mi           RWO       standard       <unset>              90s
```

各関連リソースに"0"が付いているのが、先程説明した『順序』です。
このとき、スケールアウトをしてみるとどうなるでしょうか。

```pwsh
PS> kubectl scale statefulset/mysql --replicas=2
statefulset.apps/mysql scaled
PS> kubectl get statefulset
NAME    READY   AGE
mysql   2/2     12m
PS> kubectl get pods
NAME      READY   STATUS    RESTARTS   AGE
mysql-0   1/1     Running   0          12m
mysql-1   1/1     Running   0          12s
PS>  kubectl get pvc
NAME         STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
db-mysql-0   Bound    pvc-5a8c9e2d...   256Mi      RWO            standard       <unset>              12m
db-mysql-1   Bound    pvc-72dc694c...   256Mi      RWO            standard       <unset>              14s
```
と、順序立ててPodとPVCが作成されていることがわかります。
逆にスケールダウンしてみます。

```pwsh
PS> kubectl scale statefulset/mysql --replicas=1
statefulset.apps/mysql scaled
PS> kubectl get statefulset
NAME    READY   AGE
mysql   1/1     15m
PS> kubectl get pods
NAME      READY   STATUS    RESTARTS   AGE
mysql-0   1/1     Running   0          14m
PS> kubectl get pvc
NAME         STATUS   VOLUME         CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
db-mysql-0   Bound    pvc-5a8c9e2d...   256Mi      RWO            standard       <unset>              12m
db-mysql-1   Bound    pvc-72dc694c...   256Mi      RWO            standard       <unset>              14s
```

PVCは1番が残っていますね。つまり次のスケールアウト時に1番が出たときにはこちらがマウントされることになります。
このように、StatefulSetはPodとPVCを一緒に管理することができるので、データベースなどのストレージを伴うPodを管理するときに便利です。
消えても別に変わらない情報のみを持つのであれば、Deploymentで十分でしょうから、どちらを使うかはアプリケーションの性質により検討することになります。

