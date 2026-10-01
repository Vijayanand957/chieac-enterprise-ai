// Provisions: Container Registry, PostgreSQL Flexible Server, Log Analytics,
// Container Apps Environment, and two Container Apps (backend + frontend).
param location string = resourceGroup().location
param namePrefix string = 'aiops'
param postgresAdminUser string = 'aiopsadmin'
@secure()
param postgresAdminPassword string
@secure()
param anthropicApiKey string

var acrName = '${namePrefix}acr${uniqueString(resourceGroup().id)}'
var pgServerName = '${namePrefix}-pg-${uniqueString(resourceGroup().id)}'
var envName = '${namePrefix}-env'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: true }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${namePrefix}-logs'
  location: location
  properties: { sku: { name: 'PerGB2018' } }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: pgServerName
  location: location
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    administratorLogin: postgresAdminUser
    administratorLoginPassword: postgresAdminPassword
    version: '16'
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: 7 }
  }
}

resource pgDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  parent: postgres
  name: 'ai_ops'
}

resource pgFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01-preview' = {
  parent: postgres
  name: 'AllowAzureServices'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: envName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource backendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ai-ops-backend'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: { external: true, targetPort: 8000 }
      registries: [{ server: '${acrName}.azurecr.io', username: acr.listCredentials().username, passwordSecretRef: 'acr-password' }]
      secrets: [
        { name: 'acr-password', value: acr.listCredentials().passwords[0].value }
        { name: 'anthropic-api-key', value: anthropicApiKey }
        { name: 'db-password', value: postgresAdminPassword }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: '${acrName}.azurecr.io/ai-ops-backend:latest'
          resources: { cpu: json('1.0'), memory: '2Gi' }
          env: [
            { name: 'ANTHROPIC_API_KEY', secretRef: 'anthropic-api-key' }
            { name: 'DATABASE_URL', value: 'postgresql+asyncpg://${postgresAdminUser}:${postgresAdminPassword}@${postgres.properties.fullyQualifiedDomainName}:5432/ai_ops' }
            { name: 'ENVIRONMENT', value: 'production' }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 3 }
    }
  }
}

resource frontendApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ai-ops-frontend'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: { external: true, targetPort: 3000 }
      registries: [{ server: '${acrName}.azurecr.io', username: acr.listCredentials().username, passwordSecretRef: 'acr-password' }]
      secrets: [{ name: 'acr-password', value: acr.listCredentials().passwords[0].value }]
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: '${acrName}.azurecr.io/ai-ops-frontend:latest'
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [{ name: 'NEXT_PUBLIC_API_URL', value: 'https://${backendApp.properties.configuration.ingress.fqdn}/api/v1' }]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 3 }
    }
  }
}

output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'
output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'
output acrLoginServer string = acr.properties.loginServer
