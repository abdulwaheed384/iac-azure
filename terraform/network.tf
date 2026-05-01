resource "azurerm_resource_group" "rg" {
  name     = "rg-network-demo-ai"
  location = "UK South"
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-demo-ai"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  dns_servers = ["8.8.8.8", "4.2.2.2"]
}

resource "azurerm_subnet" "subnet" {
  name                 = "subnet-demo"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}