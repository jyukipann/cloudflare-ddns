# cloudflare-ddns

```
curl -w "\n" --request GET 
  --url https://api.cloudflare.com/client/v4/zones/{Zone ID}/dns_records
  --header "Content-Type: application/json" 
  --header "X-Auth-Email: {メールアドレス}"
  --header "X-Auth-Key: {Global API Key}"
```
でrecord-idが取得できる

## memo
dockerでcronはきつそうなので、osのcronを使う
```bash
export EDITOR=nano
crontab -e
```
でcronを設定する
```bash
*/5 * * * * python /Users/juki/Workspace/cloudflare-ddns/ddns_updater.py
```
で5分ごとに実行される