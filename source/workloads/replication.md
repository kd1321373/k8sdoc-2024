# レプリケーション

## レプリケーションとは

レプリケーションは、稼働している(させようとしている)ポッドの数を増やすことです。
増やすことで、接続に使えるサーバーを増加させることができ、信頼性向上に繋げることになります。

デプロイメントリソースにおいては、`spec.replicas`フィールドにレプリカ数を指定することで、レプリケーションを行うことができます。

```{literalinclude} sources/deploy-hostbot.yml
:language: yaml
:line: 8-9
```

この指示により、配下として生成するRSに対し「1つのポッドを生成するように」と指示されます。
この値を調整すると、その数だけポッドが生成されるようになります。

### コマンドによるレプリケーション

マニフェストによる操作の前に、コマンドライン(`kubectl`)でのレプリケーションを試してみましょう。
一時的な操作をするときに役立つので、知っておくことを推奨しています。

```{warning}
進める前に、前節のデプロイメントを作成・適用しておいてください。
```

現在のdeploy,rs,podsを確認してみます。
掲載の都合上、他のリソースは省略しています。

```bash
$ kubectl get deploy
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
hostbot   1/1     1            1           168m

$ kubectl get rs
NAME                DESIRED   CURRENT   READY   AGE
hostbot-78ddbf657   1         1         1       12m

$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGEctl get pods
hostbot-78ddbf657-skzms   1/1     Running   0          13m
```

`kubectl`のレプリケーション操作は、`kubectl scale` を使います。
試しに、レプリケーション数2にしてみます。

```bash
$ kubectl scale deploy/hostbot --replicas=2
deployment.apps/hostbot scaled
```

では、各リソースを見直してみましょう。

```bash
$ kubectl get deploy
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
hostbot   2/2     2            2           172m

$ kubectl get rs
NAME                DESIRED   CURRENT   READY   AGE
hostbot-78ddbf657   2         2         2       16m

$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
hostbot-78ddbf657-skzms   1/1     Running   0          16m
hostbot-78ddbf657-wcj64   1/1     Running   0          46s
```

`hostbot-78ddbf657-wcj64` という新しいポッドが生成されていることが確認できます。
これは、ReplicaSetによる『あるべき姿』がポッド数2と再規定されたことで、新たにポッドが生成された結果です。

この操作を用いて、少し実験をしてみましょう。

 - レプリケーション数を4にして、実際にポッド数が4になったかは確認してください
 - その後、レプリケーション数を2にして、 **素早く** ポッドがどのような状態になっているかを確認してください
 - レプリケーション数を0にしたらどうなるでしょうか? 実行前に妄想し、実際に行ってください(同様に『素早く』ポッドをチェックしてみると良いでしょう)
 - deploy/hostbotに対するレプリケーション数を1に戻した上で、rs/hostbot-XXXXXXXX(実際のIDは確認すること)のみレプリケーション数4にしたらどうなるでしょうか
   - どうしてそのようになるのでしょうか? その理由を考えてみてください

### マニフェストによるレプリケーション

マニフェストに記述することで、デプロイメントリソースにおいてもレプリケーションを行うことができます。
以下の変更例は、レプリカ数を3に設定しています。

```{literalinclude} sources/deploy-hostbot-3.yml
:language: yaml
:lines: 8-10
:emphasize-lines: 2
:line-start: 8
```

これを適用すると、ポッド数が3になります。
