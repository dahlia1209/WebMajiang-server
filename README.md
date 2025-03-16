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
$containerapp=$(-Join ("webmajiang-containerapp"))
$containerenvironment=$(-Join ("webmajiang-", $yyyyMMddHHmm ,"-containerenv"))
$acr=$(-Join ("webmajiang", $yyyyMMddHHmm))
$image="webmajiangimg:latest"
$startup="uvicorn app.main:app --host 0.0.0.0 --port 80"
$webappurl=$(-Join ("https://",$webapp,".azurewebsites.net"))

az group create --name $rg --location $location --tags "yyyyMMddHHmm=$yyyyMMddHHmm"
az acr create --resource-group $rg --name $acr --sku Basic --admin-enabled  true
az acr build --resource-group $rg --registry $acr --image $image
az containerapp up --name $containerapp --resource-group $rg --location $location --environment  $containerenvironment --image "$acr.azurecr.io/$image" --target-port 80 --ingress external --query properties.configuration.ingress.fqdn
$customDomainVerificationId=$(az containerapp show -n $containerapp -g $rg --query "properties.customDomainVerificationId" -o tsv)
$fqdn=$(az containerapp show -n $containerapp -g $rg --query "properties.configuration.ingress.fqdn" -o tsv)
az network dns record-set cname set-record -g nakamura-rg -z ryu-nakamura.com -n webmajiang-backend -c $fqdn


az appservice plan create --name $webappplan --resource-group $rg --sku B1 --is-linux 
az webapp create --resource-group $rg --plan $webappplan --name $webapp --assign-identity [system] --role AcrPull --scope "/subscriptions/a89c86cd-422c-44a3-8ce5-00447d39a27e/resourceGroups/$rg" --acr-use-identity --acr-identity [system] --container-image-name "$acr.azurecr.io/$image" --query "hostNames[0]" -o tsv
az webapp config set --resource-group $rg --name $webapp --startup-file $startup --query "name" -o tsv

#リソース削除
$rg=$(az group list --query "[? contains(name,'webmajiang')].name" -o tsv)
az group delete  --name $rg  --yes

```