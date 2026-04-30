# Internal Cloud Security Policy

## Network Security

1. SSH (port 22) must NOT be exposed to 0.0.0.0/0
2. HTTP (port 80) must not be publicly exposed without HTTPS enforcement
3. NSGs must be associated with all subnets
4. Public DNS servers are not allowed (use Azure DNS)
5. Outbound internet access must be restricted

## Governance

6. All resources must have tags
7. Resource groups must follow naming standards