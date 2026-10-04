# Production Observability & Autonomous Scheduler Configuration

## 1. Autonomous Scheduling Architecture

The pipeline health monitor (`py -m solution monitor`) detects batch freshness, candidate volume drift, silent zero-candidate failures, unhandled exceptions, and review noise (e.g., low-confidence proposal ratio exceeding 25%).

To make detection fully autonomous rather than relying on manual operator commands, three scheduling configurations are supported:

1. **GitHub Actions Scheduled Canary** (Cloud CI/CD): Automatically executes hourly at 17 minutes past the hour via `.github/workflows/pipeline-health.yml`.
2. **Systemd Timer & Service** (Production Linux Host): Reliable system-level periodic execution with failure restart policies.
3. **Cron Job** (Standard Unix / Containerized Cron): Lightweight scheduled invocation.

---

## 2. Linux Cron Configuration

Deploy to `/etc/cron.d/june-tapes-monitor` or the application user's crontab (`crontab -e`):

```cron
# Run BetterBark pipeline health check every hour at minute 0
# Exits 0 on healthy, exits 1 on alert conditions; routes stdout/stderr and triggers alert handler on non-zero exit
0 * * * * appuser /opt/june-tapes/scripts/run_monitor_and_alert.sh >> /var/log/june-tapes/monitor.log 2>&1
```

### Alert Wrapper Script: `scripts/run_monitor_and_alert.sh`
```bash
#!/usr/bin/env bash
set -eo pipefail

APP_DIR="/opt/june-tapes"
cd "$APP_DIR"

# Run monitor and capture JSON output
HEALTH_JSON=$(python -m solution monitor --expected-calls 140 --max-age-seconds 3600 2>&1) || EXIT_CODE=$?

if [ "${EXIT_CODE:-0}" -ne 0 ]; then
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ALERT: Health check failed with code $EXIT_CODE"
    
    # Route payload to Slack Webhook
    curl -s -X POST -H 'Content-type: application/json' \
      --data @- "$SLACK_ALERT_WEBHOOK_URL" <<EOF
    {
      "channel": "#ai-ops-alerts",
      "username": "June-Tapes-Monitor",
      "icon_emoji": ":rotating_light:",
      "attachments": [
        {
          "color": "danger",
          "title": "Pipeline Health Degradation Alert",
          "text": "The June Tapes customer issue pipeline reported an operational warning or error.",
          "fields": [
            { "title": "Exit Code", "value": "${EXIT_CODE}", "short": true },
            { "title": "Timestamp", "value": "$(date -u +'%Y-%m-%d %H:%M:%S UTC')", "short": true },
            { "title": "Diagnosis", "value": "\`\`\`${HEALTH_JSON}\`\`\`", "short": false }
          ],
          "actions": [
            {
              "type": "button",
              "text": "Inspect Review Queue",
              "url": "https://dashboard.betterbark.internal/pipeline/triage"
            }
          ]
        }
      ]
    }
EOF

    # Route high-severity incident to PagerDuty Events v2 API
    curl -s -X POST "https://events.pagerduty.com/v2/enqueue" \
      -H 'Content-Type: application/json' \
      -d @- <<EOF
    {
      "routing_key": "$PAGERDUTY_INTEGRATION_KEY",
      "event_action": "trigger",
      "payload": {
        "summary": "BetterBark Pipeline Health Monitor Failure (Code $EXIT_CODE)",
        "source": "june-tapes-production-worker",
        "severity": "warning",
        "custom_details": $HEALTH_JSON
      }
    }
EOF
fi
```

---

## 3. Systemd Unit & Timer Configuration

For enterprise production deployments (e.g., Ubuntu/RHEL EC2 or Bare Metal):

### `/etc/systemd/system/june-tapes-monitor.service`
```ini
[Unit]
Description=BetterBark Pipeline Health Monitor
After=network.target

[Service]
Type=OneShot
User=betterbark
WorkingDirectory=/opt/june-tapes
Environment="PYTHONPATH=/opt/june-tapes"
EnvironmentFile=/etc/june-tapes/environment
ExecStart=/usr/bin/python3 -m solution monitor --expected-calls 140 --max-age-seconds 3600
StandardOutput=append:/var/log/june-tapes/monitor.log
StandardError=append:/var/log/june-tapes/monitor.log
ExecStopPost=/opt/june-tapes/scripts/systemd_alert_handler.sh $SERVICE_RESULT $EXIT_CODE
```

### `/etc/systemd/system/june-tapes-monitor.timer`
```ini
[Unit]
Description=Hourly execution of BetterBark Pipeline Monitor
Requires=june-tapes-monitor.service

[Timer]
OnCalendar=*-*-* *:00:00
Persistent=true
RandomizedDelaySec=60

[Install]
WantedBy=timers.target
```

Enable and start with:
```sh
systemctl daemon-reload
systemctl enable --now june-tapes-monitor.timer
```

---

## 4. Concrete Alert Route Example

When `monitor` encounters an anomaly—such as low-confidence proposals exceeding the 25% threshold (currently 30/94, triggering code `HIGH_LOW_CONFIDENCE_SHARE`)—it emits structured JSON:

```json
{
  "healthy": false,
  "evaluated_at": "2026-10-04T17:28:00Z",
  "alerts": [
    {
      "code": "HIGH_LOW_CONFIDENCE_SHARE",
      "severity": "WARNING",
      "metric": "low_confidence_share",
      "current_value": 0.3191,
      "threshold": 0.2500,
      "detail": "30 of 94 queued proposals flagged as low-confidence (file-new-low), exceeding 25% tolerance threshold."
    }
  ],
  "metrics": {
    "calls_processed": 140,
    "candidates_found": 228,
    "queued_for_review": 94,
    "queue_by_action": {
      "file-new": 42,
      "file-new-low": 30,
      "corroborate": 22
    },
    "batch_age_seconds": 124.5
  }
}
```

### PagerDuty Webhook Alert Payload Delivered:
```json
{
  "routing_key": "pd-service-key-betterbark-ai",
  "event_action": "trigger",
  "dedup_key": "june-tapes-high-low-confidence",
  "payload": {
    "summary": "[WARNING] Pipeline Health: 31.9% low-confidence proposals exceeds 25% threshold",
    "timestamp": "2026-10-04T17:28:00Z",
    "source": "worker-us-west-2.betterbark.internal",
    "severity": "warning",
    "component": "pipeline-judge",
    "group": "data-quality",
    "custom_details": {
      "queued_total": 94,
      "low_confidence_count": 30,
      "high_confidence_count": 42,
      "corroboration_count": 22,
      "recommended_action": "Review queue noise in review_queue.md; inspect recent judge prompt or lexicon adjustments."
    }
  }
}
```

---

## 5. GitHub Actions Autonomous CI Canary

As implemented in `.github/workflows/pipeline-health.yml`:
- **Trigger**: Hourly cron (`17 * * * *`) and on-demand `workflow_dispatch`.
- **Isolation**: Runs in standard clean container, executes unit tests, performs full review without filing, and evaluates `monitor`.
- **Self-Healing Issue Management**:
  - If unhealthy: Opens an operator GitHub issue labeled `pipeline-alert` or updates existing open issue.
  - If healthy: Automatically closes any open operator GitHub issue.
- **Guardrails**: Hardcoded to never invoke `apply`. Sinks remain 100% unwritten.
