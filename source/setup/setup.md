# Kubernetes環境の構築

Kubernetes(K8s)は環境構築に少し時間がかかるので、説明に入る前に構築準備だけしておきます。

## K8s機能の有効化

本授業では、Docker Desktopを使っています。このシステムではK8s環境(開発用)が構築可能です。
現状では意味不明かもしれませんが、1マスター・1ノードの構成となります。

設定方法は簡単で、Docker Desktopの設定画面からK8sを有効化するだけです。

```{figure} ./images/enable-k8s-on-dd.png
Docker Desktopの設定画面からK8sを有効化する
```

有効化すると、しばらく必要な環境構築を行うので、しばらく待ちます。完了後、ダッシュボード下部にK8sの状態が表示されます。

```{figure} ./images/k8s-status.png
起動している状態(K8s)
```
