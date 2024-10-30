# クリーンナップ

K8sの環境は、マニフェストがクラスタに残っていると、ずっとその状態を維持しようとし続けます。
そのため、マニフェスト(リソース)を削除しないと、再起動しても(Docker Desktopを起動するたびに)バックで起動してしまいます。

## マニフェストを削除する

マニフェストを渡すと、含まれるリソースを削除できます。

 ```bash
 $ kubectl delete -f deployment-httpd.yml -f httpd.yml
 $ kubectl get svc
 $ kubectl get deploy
 ```

 それぞれ存在しないことが確認できます。
 これで簡単な一巡りは終了です。
