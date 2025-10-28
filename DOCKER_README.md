# Grafana Pinger - Host Management API

Docker image за Host Management API компонент на Network Monitoring Stack.

## Какво е това?

`djok/grafana-pinger` е REST API за динамично управление на мониторинг targets в Prometheus + Grafana + Blackbox Exporter stack. Позволява добавяне, редакция и изтриване на хостове за ICMP/HTTP/TCP мониториране без да се налага ръчна редакция на конфигурационни файлове.

## Функционалности

- ✅ REST API за CRUD операции на мониторинг хостове
- ✅ Web UI за управление на хостове
- ✅ Автоматично генериране на Prometheus file_sd_config файлове
- ✅ Поддръжка на групи и labels
- ✅ Bulk операции за масово добавяне на хостове
- ✅ Health check endpoint
- ✅ CORS enabled за интеграция с Grafana

## Quick Start

### С Docker Compose (препоръчително)

Виж пълния stack на: https://github.com/YOUR_REPO/smokeping-docker

```yaml
services:
  host-api:
    image: djok/grafana-pinger:latest
    container_name: host-api
    restart: unless-stopped
    environment:
      - TARGETS_DIR=/targets
    volumes:
      - targets-data:/targets
    ports:
      - "5000:5000"

volumes:
  targets-data:
```

### Standalone

```bash
docker run -d \
  --name host-api \
  -p 5000:5000 \
  -v $(pwd)/targets:/targets \
  -e TARGETS_DIR=/targets \
  djok/grafana-pinger:latest
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### List Hosts
```bash
GET /api/hosts
```

### Add Host
```bash
POST /api/hosts
Content-Type: application/json

{
  "target": "192.168.1.1",
  "name": "My Router",
  "group": "network"
}
```

### Delete Host
```bash
DELETE /api/hosts/{id}
```

### Update Host
```bash
PUT /api/hosts/{id}
Content-Type: application/json

{
  "name": "Updated Name",
  "group": "new-group"
}
```

### Bulk Add
```bash
POST /api/hosts/bulk
Content-Type: application/json

{
  "hosts": [
    {"target": "10.0.0.1", "name": "Server 1", "group": "servers"},
    {"target": "10.0.0.2", "name": "Server 2", "group": "servers"}
  ]
}
```

### List Groups
```bash
GET /api/groups
```

## Web UI

Отвори браузър на `http://localhost:5000` за да видиш Web UI за управление на хостове.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGETS_DIR` | `/targets` | Директория за съхранение на Prometheus targets |

## Volumes

- `/targets` - Persistent storage за hosts.json файла (Prometheus file_sd config)

## Integration с Prometheus

API-то генерира `hosts.json` файл в Prometheus file_sd_config формат:

```json
[
  {
    "targets": ["192.168.1.1"],
    "labels": {
      "id": "unique-id",
      "name": "My Router",
      "group": "network",
      "created": "2025-10-28T12:00:00"
    }
  }
]
```

Prometheus конфигурация:

```yaml
scrape_configs:
  - job_name: 'icmp-ping'
    metrics_path: /probe
    params:
      module: [icmp]
    file_sd_configs:
      - files:
          - '/targets/hosts.json'
        refresh_interval: 30s
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

## Ports

- `5000` - HTTP API и Web UI

## Architecture

```
Web UI/API Client
       │
       ▼
  Flask REST API
       │
       ▼
  hosts.json (file_sd)
       │
       ▼
  Prometheus ──► Blackbox Exporter ──► Monitored Hosts
```

## Health Check

Container включва healthcheck:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/api/health')"]
  interval: 30s
  timeout: 5s
  retries: 3
```

## Security

- API няма вградена authentication - използвай reverse proxy (Nginx/Traefik) за auth
- CORS е enabled за integration с Grafana
- Препоръчва се използване зад reverse proxy в production

## Support

- GitHub Issues: https://github.com/YOUR_REPO/smokeping-docker/issues
- Full Documentation: https://github.com/YOUR_REPO/smokeping-docker

## License

MIT License

## Author

Built with Claude Code
