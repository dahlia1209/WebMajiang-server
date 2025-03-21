## アプリケーション起動

```sh
cd C:\src\WebMajiang-server
.\env\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## テスト

```sh
cd C:\src\WebMajiang-server\tests
pytest -v
```

## パッケージ
```sh
pip freeze > requirements.txt

```

## デプロイ
```sh

#リソース作成・デプロイ
$yyyyMMddHHmm=$(az group list --query "[? contains(name,'webmajiang')].tags.yyyyMMddHHmm" -o tsv)
$rg=$(az group list --query "[? contains(name,'webmajiang')].name" -o tsv)
if ([System.String]::IsNullOrEmpty($rg)){
    $yyyyMMddHHmm=$(Get-Date -Format "yyyyMMddHHmm")
    $rg=$(-Join ("webmajiang-", $yyyyMMddHHmm ,"-rg"))
    }
$location="westus2"
$webapp=$(-Join ("webmajiang-", $yyyyMMddHHmm ,"-app"))
$webappplan=$(-Join ("webmajiang-", $yyyyMMddHHmm ,"-plan"))
$containerapp=$(-Join ("webmajiang-", $yyyyMMddHHmm ,"-ca"))
$containerenvironment=$(-Join ("webmajiang-", $yyyyMMddHHmm ,"-containerenv"))
$image="ghcr.io/dahlia1209/webmajiang-server:main"

az group create --name $rg --location $location --tags "yyyyMMddHHmm=$yyyyMMddHHmm"
az containerapp up --name $containerapp --resource-group $rg --location $location --environment  $containerenvironment --image $image --target-port 80 --ingress external --registry-username dahlia1209 --registry-server ghcr.io --registry-password $(Get-Content ".\.env" |   Where-Object { $_ -match "^github_token=" } |   ForEach-Object { $_.Split('=')[1].Trim() }  )
$customDomainVerificationId=$(az containerapp show -n $containerapp -g $rg --query "properties.customDomainVerificationId" -o tsv)
$fqdn=$(az containerapp show -n $containerapp -g $rg --query "properties.configuration.ingress.fqdn" -o tsv)
az network dns record-set cname set-record -g nakamura-rg -z ryu-nakamura.com -n webmajiang-backend -c $fqdn
az network dns record-set txt add-record -g nakamura-rg -z ryu-nakamura.com -n asuid.webmajiang-backend -v $customDomainVerificationId    

#リソース削除
$rg=$(az group list --query "[? contains(name,'webmajiang')].name" -o tsv)
az group delete  --name $rg  --yes

```