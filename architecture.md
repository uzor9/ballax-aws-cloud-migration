
# Ballax Technologies — AWS Architecture

```mermaid
flowchart TB
    User["Administrator's Laptop"]

    subgraph AWS["AWS — eu-north-1"]
        subgraph VPC["Custom VPC — 10.0.0.0/24"]
            subgraph Public["Public Subnet — 10.0.0.0/25"]
                EC2["EC2 — Amazon Linux 2023"]
                Nginx["Nginx — 127.0.0.1:8080"]
                Gunicorn["Gunicorn + Flask API — 127.0.0.1:8000"]

                EC2 --> Nginx
                Nginx --> Gunicorn
            end

            subgraph Private["Private Database Connectivity"]
                RDS[("Amazon RDS — MySQL")]
            end
        end
    end

    User -->|"SSH tunnel — port 22"| EC2
    Gunicorn -->|"TLS-encrypted MySQL — port 3306"| RDS
```

## Architecture Notes

- The EC2 instance provides the application compute environment.
- Nginx and Gunicorn listen only on the EC2 loopback interface.
- SSH port forwarding provides access without exposing the API publicly.
- Amazon RDS is not publicly accessible.
- Security groups restrict network access between components.
- Flask connects to MySQL using a dedicated application database account.

