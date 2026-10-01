#!/usr/bin/env bash
# Deploys the Enterprise AI Operations Assistant to Azure Container Apps.
# Usage: ./deploy.sh <resource-group> <location>
set -euo pipefail

RESOURCE_GROUP="${1:?Usage: ./deploy.sh <resource-group> <location>}"
LOCATION="${2:-eastus}"

echo "==> Creating resource group: $RESOURCE_GROUP in $LOCATION"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

read -rsp "Postgres admin password: " PG_PASSWORD; echo
read -rsp "Anthropic API key: " ANTHROPIC_KEY; echo

echo "==> Deploying infrastructure (Bicep)"
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file main.bicep \
  --parameters postgresAdminPassword="$PG_PASSWORD" anthropicApiKey="$ANTHROPIC_KEY"

echo "==> Building and pushing container images"
ACR_NAME=$(az deployment group show -g "$RESOURCE_GROUP" -n main --query properties.outputs.acrLoginServer.value -o tsv | cut -d. -f1)
az acr login --name "$ACR_NAME"

docker build -t "$ACR_NAME.azurecr.io/ai-ops-backend:latest" ../../backend
docker push "$ACR_NAME.azurecr.io/ai-ops-backend:latest"

docker build -t "$ACR_NAME.azurecr.io/ai-ops-frontend:latest" ../../frontend
docker push "$ACR_NAME.azurecr.io/ai-ops-frontend:latest"

echo "==> Rolling out latest images"
az containerapp update --name ai-ops-backend --resource-group "$RESOURCE_GROUP" \
  --image "$ACR_NAME.azurecr.io/ai-ops-backend:latest"
az containerapp update --name ai-ops-frontend --resource-group "$RESOURCE_GROUP" \
  --image "$ACR_NAME.azurecr.io/ai-ops-frontend:latest"

echo "==> Done. Fetching public URLs:"
az deployment group show -g "$RESOURCE_GROUP" -n main --query properties.outputs
