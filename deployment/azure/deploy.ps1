<#
    AzureRM 6.3.0
#>
Param(
    $webAppName,
    $resourceGroupName, 
    $appServicePlanTier,
    $region,
    $hostingPlanName,
    $subId

)

Login-AzureRmAccount -Subscription $subId
New-AzureRmResourceGroup -Name $resourceGroupName -Location $region -Force
$params = @{
 appname = $webAppName
 hostingPlanName = $hostingPlanName 
 hostingEnvironment = "" 
 location = $region 
 sku = "Free" 
 workerSize = "0"
 skuCode = "F1" 
 serverFarmResourceGroup =  $resourceGroupName 
 subscriptionId = $subId

}

Write-Host "INFO: START ARM DEPLOY" -ForegroundColor Yellow
$deployment = New-AzureRmResourceGroupDeployment -Name "Deployment" -ResourceGroupName $resourceGroupName -Mode Incremental `
-TemplateFile "$PSScriptRoot\template.json" -TemplateParameterObject $params
Write-Host "INFO: END ARM DEPLOY" -ForegroundColor Yellow
Write-Host "INFO: START ZIP" -ForegroundColor Yellow
New-Item -Path "$PSScriptRoot\temp" -ItemType Directory | Out-Null
Copy-Item -Path "$PSScriptRoot\..\..\spotbot\*" -Destination "$PSScriptRoot\temp" -Exclude "venv", ".idea", "__pycache__" -Recurse
Copy-Item -Path "$PSScriptRoot\webAppConfig\*" -Destination "$PSScriptRoot\temp"
Add-Type -assembly "system.io.compression.filesystem"
[io.compression.zipfile]::CreateFromDirectory("$PSScriptRoot\temp", "$PSScriptRoot\deploy.zip") 
Write-Host "INFO: END ZIP" -ForegroundColor Yellow
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $deployment.Outputs["username"].Value, $deployment.Outputs["password"].Value)))
$apiUrl = "https://$webAppName.scm.azurewebsites.net/api/zipdeploy"
$filePath = "$PSScriptRoot\deploy.zip"
Write-Host "INFO: START ZIP DEPLOYMENT" -ForegroundColor Yellow
Invoke-RestMethod -Uri $apiUrl -Headers @{Authorization=("Basic {0}" -f $base64AuthInfo)} -Method POST -InFile $filePath -ContentType "multipart/form-data"
Write-Host "INFO: END ZIP DEPLOYMENT" -ForegroundColor Yellow
Write-Host "INFO: START CLEAN UP" -ForegroundColor Yellow
Remove-Item "$PSScriptRoot\temp" -Recurse -Force
Remove-Item "$PSScriptRoot\deploy.zip" -Force
Write-Host "INFO: END CLEAN UP" -ForegroundColor Yellow



