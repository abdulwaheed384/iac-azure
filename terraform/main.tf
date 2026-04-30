terraform {
  cloud {
    organization = "iac-ai-org"

    workspaces {
      name = "iac-azure-workspace"
    }
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}