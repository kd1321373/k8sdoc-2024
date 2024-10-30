# headlamp GUI

headlampは、Docker Desktopの拡張機能(Extension)で提供されているK8sのUI機能です。
監視目的であればとりあえず使えそうなので、ここで試してみましょう。

## インストール方法

ダッシュボードを開き、Extensions(拡張機能)にて検索してみてください。
見つけたらインストールしましょう。

```{figure} ./images/headlamp.drawio.png
headlampの検索とインストール
```

インストールには少し時間がかかりますが、完了すると使えるようになります。

## 呼び出し方

インストール完了後、Extensionsのリストにheadlampが出現するので、クリックすることで切り替えられます。

```{figure} ./images/hl-dashboard.drawio.png
headlampダッシュボード(トップ画面)
```

Clustersがある場合、**docker-desktop** を選択することで、クラスタ内の情報が見られるようになります。

