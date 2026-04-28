terraform {
  cloud {
    organization = "iac-ai-org"

    workspaces {
      name = "iac-azure-workspace"
    }
  }
}

provider "azurerm" {
  features {}
}