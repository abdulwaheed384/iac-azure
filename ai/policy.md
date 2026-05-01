# Security Policy for Terraform (Azure)

## NET-001
All subnets must have a Network Security Group (NSG) associated.

## NET-002
Virtual Networks must NOT use public DNS servers. Use Azure DNS or internal DNS only.

## NET-003
All Virtual Networks must have DDoS Protection Standard enabled for production workloads.

## LOG-001
All resources must have diagnostic logging enabled and forwarded to Log Analytics.

## TAG-001
All resources must include mandatory tags: environment, owner, cost-center.

## SEC-001
No resource should be publicly exposed unless explicitly required and justified.