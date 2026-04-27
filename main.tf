provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-demo-ai-project"
  location = "UK South"
}

resource "azurerm_storage_account" "storage" {
  name                     = "storage-aw-demo-78645"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}