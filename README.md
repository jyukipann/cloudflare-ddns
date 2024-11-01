# cloudflare-ddns

```
curl -w "\n" --request GET 
  --url https://api.cloudflare.com/client/v4/zones/{Zone ID}/dns_records
  --header "Content-Type: application/json" 
  --header "X-Auth-Email: {メールアドレス}"
  --header "X-Auth-Key: {Global API Key}"
```
でrecord-idが取得できる