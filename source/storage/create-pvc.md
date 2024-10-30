# pvcを作ってみる

では実際にpvcを作ってみましょう。

## まずは作ってみる

Pod同様、マニフェストを作って対応します。
環境上、sc指定無しのpvcとし、デフォルトのstorageclassが使用されるようにします。

vscode上で、`pvc-sample.yml`というファイルを作成し、`pvc`とタイプすると、スニペットが展開されるので、まずはそれを行ってください。

```{literalinclude} src/pvc-snippet.yml
:language: yaml
:name: pvc-sample.yml(スニペット展開まで)
```

その後、必要な部分を書き換えていきます。

```{literalinclude} src/pvc-sample.yml
:language: yaml
:diff: src/pvc-snippet.yml
```

作成したpvcを適用してください。

```pwsh
PS> kubectl apply -f pvc-sample.yml # 実際のファイルのパスにあわせてください
persistentvolumeclaim/test-pvc created
```

適用後、pvcが作成されていることを確認してください。

```pwsh
PS> kubectl get pvc
NAME       STATUS   VOLUME             CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
test-pvc   Bound    pvc-bb189150-(略)     256Mi            RWO       hostpath       <unset>              1s
```

## マニフェストの分析

では今のマニフェストを確認してみましょう。

```{literalinclude} src/pvc-sample.yml
:lamguage: yaml
:linenos:
:emphasize-lines: 1,2,8,10
```

- 1,2行目: apiVersionとkindが指定されています。kindはPersistentVolumeClaimです。
- 8行目: spec.resources.requests.storage にて、ストレージとして必要な容量を設定しています、ここでは256MiBとしています
- 10行目: spec.accessModes にて、アクセスモードを指定しています。ここではReadWriteOnceとしています
  - 名前の通り「1カ所からの読み書き」を意味します、他にはこのような設定が存在し得ます
  - ReadWriteMany: 複数の場所から読み書き可能
  - ReadOnlyMany: 複数の場所から読み込みのみ可能

ここでは指定しませんが、どのようなストレージクラス(sc)から取得するべきかや、ラベルの状態などで選別することもあります。

## 注意点

- pvcを作成したとき、即時に割り当てられる(bind)保証はありません
  - Docker Desktopにおいては即時割り当てが機能するようです
  - その他の環境では、割り当てに時間がかかる場合や、『実際にPodが利用するときに初めて割り当てが発生する』場合もあります
    - kind(K8s in Docker)においては、Podが作成されるときに割り当てが発生するようです

# podから使ってみる

では、実際にPodから使う(Podにpvcによるボリュームを割り当てる)ことを試してみましょう。

```{literalinclude} src/pod-sample.yml
:language: yaml
:emphasize-lines: 15-17,19-22
:linenos:
```

ポイントは2カ所あります。

## Podにおけるボリュームのマウント

マウントは、`volumeMounts`にて指定します。
複数のマウントが考えられるので、各項目をリストで指定します。

* `name:`: マウントしたいボリューム名
* `mountPath:`: マウント先のパス

このときのボリューム名(`name`)は、Pod内での産照明となりますから、他で作成する必要があります。それが19行目以降の`volumes`の部分です。こちらも同様にリストで指定します。

- `name:`: ボリューム名(`volumeMounts`で指定する名前)
- `persistentVolumeClaim.claimName`: どのpvcを利用するか

この操作により、

1. Podが指定のpvcを利用しようとする
2. pvcをチェックします
   1. pv割り当てが起きていればそのまま使います
   2. pv割り当てがなければその場で作成します(ダイナミックプロビジョニング) ※ できない場合、Pendingとなる
3. pvcによって用意されたpvをマウントします


