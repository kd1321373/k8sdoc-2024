# サービスディスカバリ

実は前述のアドレス(URL)では、起動したhttpdにアクセスすることはできませんでした。
これは、K8sの仕組みにより、Pod(コンテナ)に対して直接アクセスすることができないためです。
コンテナは実際は『どこで起動するかがわからない』という状態です。複数のノードがある場合、どこで適用されるかはその時の状態に依存しています。
そこで、どこで起動したかを抽象化したものが『サービス』です。
サービスは、Podに対して『名前』をつけることができ、その名前でアクセスすることができます。
このときに、コンテナに付与した『ラベル』が効果を発揮します。

## サービスのマニフェストを作成する

では、先程作ったhttpdに対応するサービスディスカバリを行ってみます。
そのためのマニフェストは以下のようになります。

```{literalinclude} ./src/service-httpd.yml
:name: sevice-httpd.yml
:language: yaml
```

## 適用して確認してみよう

こちらも適用してみましょう、手順は同じです。

```bash
$ kubectl apply -f service-httpd.yml
service/httpd created
```

```bash
$ kubectl get svc
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
httpd        LoadBalancer   10.109.24.86   localhost     8080:31160/TCP   3s
kubernetes   ClusterIP      10.96.0.1      <none>        443/TCP          3h30m
```

`get`のあとが`svc`となっているので注意してください。

この状態で、`http://localhost:8080`にアクセスすると、先程と同様にhttpdのページが表示されるはずです。

## 本当に中のコンテナが見えているのか?

では、今回使ったマニフェストを逆に適用して取り消ししてみます。

```bash
$ kubectl delete -f service-httpd.yml
$ kubectl get svc
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   3h33m
```

この状態で、`http://localhost:8080`にアクセスすると、もう見えません、エラーになるはずです(キャッシュが出ることはあります)。


## なんでこんな面倒なことをするのか?

- マニフェストにより明文化されることで『どう動くべきか』がはっきりわかる
- マニフェストを満たさない状況ではできる限り満たすようにシステムが自律的に動いてくれる
  - 諸事情でそれでもダメと言うときもありますが、それはそれで別の問題です
