resource "azurerm_resource_group" "network_rg" {
  name     = "rg-network-demo-ai"
  location = "UK South"

  tags = {
    environment = "dev"
    project     = "ai-iac"
  }
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-demo-ai-project"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.network_rg.location
  resource_group_name = azurerm_resource_group.network_rg.name

    dns_servers = ["8.8.8.8", "8.8.4.4"]


  tags = {
    environment = "dev"
    project     = "ai-iac"
  }
}

resource "azurerm_subnet" "subnet" {
  name                 = "subnet-demo"
  resource_group_name  = azurerm_resource_group.network_rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}