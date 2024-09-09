# デプロイメントとその裏側

**デプロイメント(deployment, deploy)** は、実際にポッドを作って管理するために広く使われているリソースです。

## ポッドではダメなの?

ポッドに関して簡単にでも知ると、コンテナはポッドが管理しているんだからポッドが用意できれば問題無いと考えると思います。
しかし、実際の運用上、ポッドだけではコンテナの管理が不十分です。

- ポッドそのものが不意に消失する可能性はあります(突発的なリソース不足から作成不能になる)
- ポッドの構成が変更される(マニフェスト更新で利用するイメージやリソースが変更される)

こういった状況に対応するため、ポッドを管理するためのリソースというものが存在します。
それがデプロイメントであり、配下の概念リソースとしてレプリカセット(replicaset, rs)も存在します。

```{figure} images/deploy-rs-pod.drawio.png
:align: center
```

## デプロイメントを作成してみる流れ

実際にデプロイメントリソースを作ってみます。
ここでは、少しまともな動きをするコンテナを作って対応してみます。

- 起動するとWebのポートを開く(80/tcp)
- リクエスト受けると、サーバー上の時間と、サーバーのホスト名をJSONで返す
  - 時間は `time` のキーで、 ホスト名は `host` のキーで返す

### サービスコンテナのイメージ作成

上記の役割を持つイメージをまず作成します。
ここでは、Pythonのbottleを使ってサクッと作ってみます。

1. ディレクトリhostbotを作成します
2. その中に、2つのファイルを作成します
   1. `serve.py`(Pythonコード)
   2. `requirements.txt`(依存関係記述)
3. hostbotと同じ場所に`Dockerfile`を作成します

```{literalinclude} sources/hostbot/serve.py
:name: hostbot/serve.py
:language: python
```

```{literalinclude} sources/hostbot/requirements.txt
:name: hostbot/requirements.txt
```

```{literalinclude} sources/Dockerfile
:name: Dockerfile
```

ファイルを用意したら、イメージをビルドします。
このイメージはDocker Hubへプッシュすることを前提とするため、以下に注意してください。

- タグを必ず付与してください、ここでは `v1` とします
- イメージ名は必ずDocker Hubのアカウント名を含めてください、ここでは `yourname/hostbot` とします

```bash
$ docker build -t yourname/hostbot:v1 .
$ docker push yourname/hostbot:v1
```

### まずはポッドで作ってみる

デプロイメントに入る前に、ポッドのレベルで作ってみます。

```{literalinclude} sources/pod-hostbot.yml
:language: yaml
:emphasize-lines: 16-17
```

これはWebサービスのため、外部との接続があります、そのため`spec.containers[0].ports`にポート情報を入れています。

適用して、ポートフォワードで接続させてみます。

```
$ kubectl apply -f pod-hostbot.yml
$ kubectl get pod/hostbot # Ready 1/1になるまで待つ
$ kubectl port-forward pod/hostbot 8080:80
```

これでブラウザで繋ぐと、JSON形式で時刻とホスト名が返ってくるはずです。

```{figure} images/hostbot-return.png
:align: center

pod/hostbotに対してリクエストを送った結果
```

確認できたら、`kubectl port-forward`を `Ctrl+C` で終了してから、リソースを削除します。

```bash
$ kubectl delete pod/hostbot
```

### デプロイメントを作成する

では、同様の挙動をデプロイメントで記述してみます。

```{literalinclude} sources/deploy-hostbot.yml
:language: yaml
```

同様に適用し、ポートフォワードで接続させてみます。

```bash
$ kubectl apply -f deploy-hostbot.yml
$ kubectl get deploy/hostbot # Ready 1/1になるまで待つ
$ kubectl port-forward deploy/hostbot 8080:80
```

こちらでも同様に接続できることでしょう。

```{figure} images/hostbot-return-deploy.png
:align: center

同様に取得可能 (ただしホスト名が異なる)
```

### デプロイメントを読み下してみる

では、デプロイメントの記述について確認してみます。

```{literalinclude} sources/deploy-hostbot.yml
:language: yaml
:lines: 2-7
:linenos:
:lineno-start: 2
```

リソースの設定とメタデータなのでここはいいでしょう。

```{literalinclude} sources/deploy-hostbot.yml
:language: yaml
:lines: 8-12
:linenos:
:lineno-start: 8
```

8行目以下がデプロイメントにおける仕様となります。
少しややこしいことになっていますが、おちついて読んでいけば大丈夫です。

- `replicas: 1` レプリカ(複製)の指定です、初期値である1を明示しています、ここに指定した数だけポッドが存在することを正しい状態とします
- `selector` は、このデプロイメントが管理するべきポッドを『探す方法』を提示するために使います
  - ここでは、`matchLabels` に `name: hostbot` というラベルを持つポッドを管理するという意味です
  - 逆に言えば、ポッドは生成時に `name: hostbot` というラベルを持つことが求められます

つまり、この時点では指定した状態(`name=hostbot`のラベルを持つ)のポッドが存在しないといけないということを示し、それを見つけて管理するようにデプロイメントの仕様が書かれたことになります。

では、そのようなポッドをどのように作るのでしょうか。
ポッドは複数できる可能性がある(replicas)ため、ポッドの作成方法を『テンプレート』という形で指定します。

```{literalinclude} sources/deploy-hostbot.yml
:language: yaml
:lines: 13-27
:linenos:
:lineno-start: 13
```

`spec.template` がそのテンプレートになります。
じつはここ、ポッドのマニフェストほぼ同じになっています。
なんならポッドマニフェストで動くものを作成してから、デプロイメントに書き換えるという方法も普通にとれます。

### 誰がポッドを作るのか

デプロイメントのマニフェストを読むことで、マニフェスト中のteplate部分に書かれた内容に基づくポッドが生成されることが出てきました。
しかしデプロイメントが直接ポッドを作るわけではありません。

1. マニフェストを受けて、デプロイメントリソースが作成されます
2. デプロイメントリソースは、条件を満たすポッドを作るために、 **レプリカセット** というリソースを生成します(このときにポッドのテンプレートが渡される)
3. レプリカセットは、渡されたテンプレートを元にポッドを作成します、作成するべき数は、デプロイメントリソースの `replicas` によって指定されます
4. デプロイメントは、`spec.matchLabels`の条件にみあうポッドが生成されるまで待ちます

関係性をざっくり描けば、以下のように考えられます。

```{figure} images/deploy-rs-pod-2.drawio.png
:align: center

デプロイメント〜レプリカセット〜ポッドの関係
```

```{note}
なので、該当するReplicaSetリソースをdeleteすると、Deploymentがそれに気づいてくれるのか、再生成されます。
そしてRSがdeleteされる際、配下のポッド(とコンテナ)も削除されてしまっています。

もちろんDeploymentによりRS再生成につられてPodも再生成されています。
```

