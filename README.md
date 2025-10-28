# Network Monitoring Stack

Модерен network monitoring stack с Grafana, Prometheus и Blackbox Exporter за мониториране на latency, jitter и packet loss на 100-500 хоста.

## 🎯 Функционалности

- ✅ **Latency Monitoring** - ICMP ping latency measurements
- ✅ **Jitter Tracking** - Standard deviation of latency over time
- ✅ **Packet Loss Detection** - Monitoring на загубени пакети
- ✅ **Multi-Protocol Support** - ICMP, HTTP, TCP, DNS monitoring
- ✅ **Web UI за Host Management** - Добавяй/изтривай хостове без config файлове
- ✅ **Beautiful Dashboards** - Pre-configured Grafana dashboards
- ✅ **Alerting** - Configurable alerts via AlertManager
- ✅ **Grafana Authentication** - Единна автентикация за всичко
- ✅ **Scalable** - Support за 100-500+ хоста
- ✅ **Self-hosted** - 100% free и open source

## 🏗️ Архитектура

```
           User Browser
                │
                ▼
         Nginx Reverse Proxy (Port 80)
         │                     │
         │ /                   │ /host-api/
         ▼                     ▼
    Grafana (3000)      Host API (5000)
         │                     │
    Dashboards            REST API для хостове
         │                     │
         │              targets/*.json
         ▼                     │
   Prometheus (9090) ◄────────┘
         │
         ▼
   Blackbox Exporter (9115)
         │
         ▼
   Monitored Hosts
```

**Компоненти:**
- **Nginx** - Reverse proxy, обединява всички services на порт 80
- **Grafana** - Visualization, Dashboards & Authentication
- **Host API** - REST API за управление на хостове (достъпен на /host-api/)
- **Prometheus** - Time-series database (90 дни retention)
- **Blackbox Exporter** - Network probes (ICMP, HTTP, TCP, DNS)
- **AlertManager** - Alert routing & notifications

## 🚀 Бърз старт

### Предпоставки

- Docker
- Docker Compose
- 2GB RAM минимум
- 10GB disk space за данни

### Инсталация

**Docker Image**: Проектът използва pre-built Docker image от DockerHub: [`djok/grafana-pinger`](https://hub.docker.com/r/djok/grafana-pinger)

1. **Клонирай репозиторито**:
```bash
git clone <repository-url>
cd smokeping-docker
```

2. **Създай .env файл**:
```bash
cp .env.example .env
```

3. **Редактирай .env файла**:
```bash
# Промени default password!
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password
```

4. **Добави твоите хостове в Prometheus конфигурацията**:

Редактирай `config/prometheus/prometheus.yml` и добави твоите targets:

```yaml
  - job_name: 'icmp-ping'
    metrics_path: /probe
    params:
      module: [icmp]
    static_configs:
      - targets:
          - 192.168.1.1      # Твой router
          - 192.168.1.10     # Сървър 1
          - example.com      # External host
          # Добави повече хостове тук
        labels:
          group: 'production'
```

5. **Стартирай stack-а**:
```bash
docker-compose up -d
```

6. **Провери статуса**:
```bash
docker-compose ps
```

7. **Отвори Grafana**:
   - URL: http://localhost (всичко е на порт 80 през Nginx reverse proxy)
   - Grafana: http://localhost/
   - Host Management UI: http://localhost/host-api/
   - Username: `admin` (или каквото си задал в .env)
   - Password: `your-secure-password`

### 🌐 Production Deployment

За production deployment на публичен домейн (напр. `smokeping.fiber.bg`):

1. **Редактирай `.env` файла**:
```bash
GRAFANA_ROOT_URL=http://smokeping.fiber.bg
SERVER_DOMAIN=smokeping.fiber.bg
```

2. **Restart services**:
```bash
docker-compose down
docker-compose up -d
```

3. **Конфигурирай DNS** - добави A record за твоя домейн към IP-то на сървъра

4. **За HTTPS** - виж [PRODUCTION.md](PRODUCTION.md) за детайлни инструкции

📖 **Пълно Production ръководство**: [PRODUCTION.md](PRODUCTION.md)

## 📊 Dashboards

### Network Latency Monitoring Dashboard

Pre-configured dashboard с:

- **Overview Gauges**:
  - Hosts Up/Down count
  - Average Latency

- **Latency Graph**: Real-time latency за всички хостове
- **Jitter Graph**: Standard deviation tracking
- **Packet Loss Graph**: 5-minute average packet loss
- **Host Status Table**: Summary table с цветово кодиране

Dashboard-ът се зарежда автоматично при старт на Grafana.

### Host Management Dashboard

**Вграден Web UI за управление на хостове!**

1. Влез в Grafana: http://localhost:3000
2. Отиди на **Dashboards → Host Management**
3. Добавяй/изтривай хостове директно от UI-я
4. Използва Grafana authentication - **един login за всичко!**

**Функции:**
- ➕ Добавяне на хост (IP/hostname, име, група)
- ❌ Изтриване на хост
- 📊 Real-time статистики
- 🔄 Auto-refresh всеки 30 секунди
- 🏷️ Групиране на хостове

**Без restart на Prometheus!** Prometheus автоматично зарежда промените на всеки 30 секунди.

## ⚙️ Конфигурация

### Добавяне на нови хостове

#### Опция 1: Чрез Web UI (Препоръчително) ⭐

1. Влез в Grafana
2. Отвори **Dashboards → Host Management**
3. Попълни формата:
   - **Hostname/IP**: `192.168.1.100` или `example.com`
   - **Display Name**: `My Server`
   - **Group**: `production`
4. Кликни **Add Host**
5. Готово! Prometheus автоматично ще го зареди

#### Опция 2: Чрез API

```bash
curl -X POST http://localhost:5000/api/hosts \
  -H "Content-Type: application/json" \
  -d '{
    "target": "192.168.1.100",
    "name": "My Server",
    "group": "production"
  }'
```

#### Опция 3: Ръчно (legacy метод)

1. Редактирай `config/prometheus/prometheus.yml`
2. Добави хостовете в `static_configs` секцията
3. Рестартирай Prometheus:
```bash
docker-compose restart prometheus
```

### Групиране на хостове

Използвай `labels` за организация:

```yaml
- targets:
    - 8.8.8.8
    - 1.1.1.1
  labels:
    group: 'dns'
    location: 'external'

- targets:
    - 192.168.1.1
    - 192.168.1.2
  labels:
    group: 'infrastructure'
    location: 'datacenter1'
```

### Alert конфигурация

Alerts са дефинирани в `config/prometheus/alerts.yml`:

- **HostDown**: Host е unreachable за > 2 минути
- **HighLatency**: Latency > 500ms за > 5 минути
- **PacketLoss**: > 10% packet loss за > 5 минути
- **VeryHighLatency**: Latency > 1s за > 2 минути

#### Конфигуриране на нотификации

Редактирай `config/alertmanager/alertmanager.yml` за Slack, Email, Telegram или Discord нотификации.

**Пример за Slack**:

```yaml
receivers:
  - name: 'critical-alerts'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: '🚨 {{ .GroupLabels.alertname }}'
```

**Пример за Email**:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@yourdomain.com'
```

## 🔧 Управление

### Стартиране
```bash
docker-compose up -d
```

### Спиране
```bash
docker-compose down
```

### Преглед на логове
```bash
# Всички сървизи
docker-compose logs -f

# Конкретен сървиз
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f blackbox-exporter
```

### Рестартиране
```bash
docker-compose restart
```

### Изтриване на данни (ВНИМАНИЕ!)
```bash
docker-compose down -v
```

### Backup на данни

```bash
# Backup на Prometheus данни
docker run --rm -v smokeping-docker_prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data

# Backup на Grafana данни
docker run --rm -v smokeping-docker_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

### Restore на данни

```bash
# Restore Prometheus
docker run --rm -v smokeping-docker_prometheus-data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/prometheus-backup.tar.gz --strip 1"

# Restore Grafana
docker run --rm -v smokeping-docker_grafana-data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/grafana-backup.tar.gz --strip 1"
```

## 📈 Performance Tips

### За 100-500 хоста:

1. **Scrape Interval**: 30s (default) е добър баланс
   - По-нисък интервал (15s) = повече данни, по-голямо натоварване
   - По-висок интервал (60s) = по-малко данни, по-ниско натоварване

2. **Retention**: 90 дни (default)
   - Промени в `docker-compose.yml`: `--storage.tsdb.retention.time=90d`

3. **Resource Limits**:

```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🛡️ Security

### Grafana Security

1. **Променi default password**:
   - Редактирай `.env` файла
   - Не използвай `admin/admin` в production!

2. **Създай допълнителни users**:
   - Grafana UI → Configuration → Users
   - Задай различни роли: Admin, Editor, Viewer

3. **Enable HTTPS** (за production):
   - Добави reverse proxy (Nginx/Traefik)
   - Конфигурирай SSL сертификати

### Network Security

1. **Firewall правила**:
   - Grafana: Port 3000 (само от trusted networks)
   - Prometheus: Port 9090 (само internal)
   - Blackbox: Port 9115 (само internal)
   - AlertManager: Port 9093 (само internal)

2. **Docker network isolation**: Stack-ът използва изолирана `monitoring` мрежа

## 🐛 Troubleshooting

### Blackbox Exporter не може да прави ping

**Проблем**: `permission denied` errors

**Решение**: Контейнерът има `cap_add: NET_RAW` но на някои системи може да се наложи:

```bash
# На хост машината
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"
```

### Prometheus не вижда targets

1. Провери конфигурацията:
```bash
docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

2. Провери Prometheus UI: http://localhost:9090/targets

### Grafana dashboard-ите не се зареждат

1. Провери permissions:
```bash
docker-compose exec grafana ls -la /var/lib/grafana/dashboards
```

2. Провери provisioning:
```bash
docker-compose logs grafana | grep -i dashboard
```

### Високо memory usage на Prometheus

- Намали retention period
- Увеличи RAM на контейнера
- Оптимизирай scrape intervals

## 📦 Docker Volumes

- `prometheus-data`: Prometheus time-series data (90 дни)
- `grafana-data`: Grafana dashboards, users, settings
- `alertmanager-data`: AlertManager notification state

## 🔗 Полезни линкове

- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Blackbox Exporter**: http://localhost:9115

## 📝 Структура на проекта

```
smokeping-docker/
├── docker-compose.yml          # Main stack configuration
├── .env.example                # Environment variables template
├── .dockerignore
├── .gitignore
├── README.md
└── config/
    ├── prometheus/
    │   ├── prometheus.yml      # Prometheus scrape config
    │   └── alerts.yml          # Alert rules
    ├── blackbox/
    │   └── blackbox.yml        # Probe configurations
    ├── alertmanager/
    │   └── alertmanager.yml    # Notification routing
    └── grafana/
        ├── provisioning/
        │   ├── datasources/
        │   │   └── prometheus.yml
        │   └── dashboards/
        │       └── default.yml
        └── dashboards/
            └── network-latency.json  # Main dashboard
```

## 🛠️ Development

### Building Locally

Ако искаш да build-неш host-api image-а локално вместо да използваш DockerHub:

1. Промени `docker-compose.yml`:
```yaml
  host-api:
    build:
      context: ./api
      dockerfile: Dockerfile
    # image: djok/grafana-pinger:latest  # comment this line
```

2. Build и стартирай:
```bash
docker-compose build host-api
docker-compose up -d
```

### Pushing Updates to DockerHub

```bash
# Build image
docker-compose build host-api

# Tag за DockerHub
docker tag smokeping-docker-host-api:latest djok/grafana-pinger:latest

# Push to DockerHub
docker push djok/grafana-pinger:latest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 👨‍💻 Author

Created with Claude Code

---

**Забележка**: Този stack е оптимизиран за 100-500 хоста с self-hosted, free решение за network latency, jitter и packet loss monitoring.
