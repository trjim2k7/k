# Monitoring Runbook, On-Call Rotation, and Incident Response Templates

This document outlines standard operating procedures for common alerts, defines an on-call rotation structure, and provides a template for effective incident response.

---

## Runbook for Common Alerts

This section details common alerts, their potential causes, and systematic troubleshooting steps to resolve them.

### Alert: High CPU Utilization

*   **Description:** Server CPU usage exceeds 90% for 5 minutes.
*   **Severity:** High
*   **Possible Causes:**
    *   Code inefficiency (e.g., infinite loops, unoptimized algorithms)
    *   Traffic surge (legitimate or malicious)
    *   Rogue process (e.g., unintended cron job, runaway script)
    *   Resource contention (e.g., database lock, I/O wait affecting CPU)
*   **Troubleshooting Steps:**
    1.  **Check System Processes:**
        *   Log into the affected server(s).
        *   Use `top`, `htop`, or ` glances` to identify resource-intensive applications or processes.
        *   `top -b -n 1 | head -n 20` (for a snapshot)
        *   `ps aux --sort=-%cpu | head -n 10` (to list top CPU processes)
    2.  **Review Recent Deployments:**
        *   Check deployment logs or CI/CD pipelines for any recent code changes that might introduce performance regressions.
        *   Consult application performance monitoring (APM) tools for new anomalies correlating with deployments.
    3.  **Analyze Traffic Patterns:**
        *   Examine load balancer metrics, web server access logs, or CDN dashboards for unusual traffic spikes.
        *   Determine if the surge is legitimate user traffic or a potential attack (e.g., DDoS).
    4.  **Application-Specific Checks:**
        *   For database servers: Check slow query logs, connection counts, and active transactions.
        *   For web servers: Review access logs for specific high-load endpoints.
        *   Review application logs for errors or repeated warning messages that might indicate an underlying issue causing high CPU.
*   **Resolution:**
    *   **Reduce CPU Load:** Terminate rogue processes (if safe), throttle incoming requests (if due to traffic surge), or apply temporary resource limits.
    *   **Deploy Fix:** Rollback recent problematic deployments or deploy an emergency hotfix for identified code inefficiencies.
    *   **Scale Infrastructure:** If due to legitimate traffic growth, scale up (increase instance size) or scale out (add more instances) to distribute the load.
    *   **Optimize Code/Configuration:** Identify and optimize database queries, application code, or server configurations causing excessive CPU usage.

### Alert: Low Disk Space

*   **Description:** Disk usage on a critical volume exceeds 80%.
*   **Severity:** Medium
*   **Possible Causes:**
    *   Log file growth (e.g., verbose logging, unrotated logs)
    *   Large temporary files (e.g., failed uploads, incomplete operations)
    *   Application data accumulation (e.g., caches, database files, user uploads)
    *   Backup files not being cleaned up
    *   System snapshots
*   **Troubleshooting Steps:**
    1.  **Identify Large Files/Directories:**
        *   Log into the affected server.
        *   Use `df -h` to see overall disk usage per mount point.
        *   Navigate to the affected mount point and use `du -sh *` or `du -sh ./*` to identify large directories.
        *   `du -ax / | sort -rh | head -n 20` (to find top 20 largest files/directories from root)
        *   `find /var/log -type f -name "*.log" -print0 | xargs -0 du -h | sort -rh | head -n 10` (to find large log files)
    2.  **Clear Old Logs or Temporary Files:**
        *   Rotate logs using `logrotate` or manually truncate old log files: `> /path/to/large.log` (use with extreme caution, ensure application handles file truncation).
        *   Delete temporary files: `rm -rf /tmp/*` (be aware of active processes using /tmp).
        *   Check application-specific temporary directories.
    3.  **Review Application Data:**
        *   Check for accumulated cache files that can be safely cleared.
        *   For database servers, review database size and consider archiving or purging old data.
    4.  **Check for Unmounted Volumes:**
        *   Sometimes, old data persists if a new volume was mounted over an existing directory without properly migrating/deleting the underlying data.
*   **Resolution:**
    *   **Free Up Disk Space:** Delete unnecessary files, archive old logs/data, clear caches.
    *   **Configure Log Rotation:** Ensure `logrotate` or similar tools are properly configured for all application and system logs.
    *   **Provision More Storage:** If the data growth is legitimate and necessary, expand the existing disk size or add a new volume.
    *   **Implement Data Retention Policies:** Define and automate policies for purging old data.

### Alert: API Latency Spike

*   **Description:** Average API response time exceeds 500ms for 1 minute.
*   **Severity:** High
*   **Possible Causes:**
    *   Database issues (e.g., slow queries, connection exhaustion, deadlocks)
    *   External service dependencies (e.g., third-party API slowness, network issues)
    *   High load (e.g., legitimate traffic surge, misconfigured caching)
    *   Inefficient code or recent deployment regressions
    *   Resource exhaustion (e.g., CPU, memory, network I/O on application servers)
*   **Troubleshooting Steps:**
    1.  **Check Database Performance Metrics:**
        *   Examine database CPU, memory, I/O, active connections, and query execution times.
        *   Look for specific slow queries that might be contributing to the latency.
        *   Check for database locks or deadlocks.
    2.  **Verify Status of External APIs/Dependencies:**
        *   Check the status pages of any third-party services your API relies on.
        *   Monitor network latency to these external services from your application servers.
        *   Review internal service mesh/API gateway metrics for downstream service health.
    3.  **Review Application Logs for Errors:**
        *   Look for a sudden increase in application errors (e.g., 5xx errors, exceptions, connection timeouts) that might indicate a problem.
        *   Check for specific error messages that point to a bottleneck.
    4.  **Inspect Recent Code Changes/Deployments:**
        *   Rollback to a previous known-good version if a recent deployment correlates with the latency spike.
        *   Review code changes for potential performance anti-patterns or resource-intensive operations.
    5.  **Analyze Application Server Metrics:**
        *   Check CPU, memory, network I/O, and garbage collection metrics on the application instances.
        *   Identify if specific endpoints are experiencing higher load or resource consumption.
    6.  **Review Load Balancer/Gateway Metrics:**
        *   Check incoming request rates, error rates, and connection counts at the load balancer or API gateway level.
*   **Resolution:**
    *   **Optimize Queries/Database:** Tune slow database queries, add missing indexes, or scale database resources.
    *   **Address External Service Issues:** Engage with the external service provider, implement circuit breakers, or introduce caching for external calls.
    *   **Scale Application:** Add more application instances (horizontal scaling) or upgrade existing instances (vertical scaling) to handle increased load.
    *   **Rollback Bad Deployment:** Revert to a stable version of the application code.
    *   **Implement Caching:** Introduce or optimize caching layers (e.g., CDN, application-level cache, Redis) to reduce load on backend services.
    *   **Traffic Management:** Implement rate limiting or circuit breaking to protect overloaded services.

---

## On-Call Rotation Template

This template defines the structure for on-call responsibilities and escalation paths to ensure timely incident response.

*   **Primary On-Call:** [Name/Team]
    *   **Shift:** Monday - Sunday, 9 AM - 5 PM local time
    *   **Responsibilities:** First point of contact for all incoming alerts and incidents. Acknowledges, triages, and attempts resolution.
*   **Secondary On-Call:** [Name/Team]
    *   **Shift:** Monday - Sunday, 5 PM - 9 AM local time
    *   **Responsibilities:** Covers off-hours. Acts as a backup for the Primary On-Call during their shift if the primary is unavailable or requires assistance.
*   **Escalation Path:**
    1.  **Primary On-Call:** First attempt to contact. If no response within 5 minutes or cannot resolve.
    2.  **Secondary On-Call:** If Primary is unresponsive or requires assistance. If no response within 10 minutes or cannot resolve.
    3.  **DevOps Team Lead:** If both Primary and Secondary are unresponsive or the incident requires higher-level decision-making or broader team coordination.
    4.  **Engineering Manager:** For severe, prolonged, or highly impactful incidents requiring executive awareness or resource allocation.
*   **Tools:**
    *   **Alerting/Paging:** PagerDuty (or Opsgenie, VictorOps)
    *   **Communication:** Slack (dedicated incident channel), Zoom (for incident bridge)
    *   **Monitoring:** Grafana, Prometheus, Datadog, New Relic (or equivalent APM)
    *   **Logs:** ELK Stack (Elasticsearch, Logstash, Kibana), Splunk, Datadog Logs
    *   **Runbook/Documentation:** Confluence, GitHub Wiki, internal documentation portal

---

## Incident Response Template

This template outlines roles, responsibilities, and a standardized flow for managing and resolving incidents effectively.

### Key Incident Roles

*   **Incident Commander (IC):**
    *   **Role:** The single leader for the incident. Responsible for the overall management of the incident, making critical decisions, and ensuring the incident progresses towards resolution.
    *   **Key Responsibilities:**
        *   Declare the incident and determine its severity.
        *   Assign roles (CL, TL, etc.).
        *   Maintain a clear overview of the incident status.
        *   Prioritize actions and direct resources.
        *   Ensure effective communication.
        *   Decide when the incident is resolved.

*   **Communications Lead (CL):**
    *   **Role:** Manages all internal and external communications related to the incident.
    *   **Key Responsibilities:**
        *   Provide regular, clear updates to stakeholders (internal teams, management, customers if necessary).
        *   Draft incident reports and post-mortems.
        *   Monitor communication channels for questions and provide answers.
        *   Shield the technical team from distractions.

*   **Technical Lead (TL):**
    *   **Role:** Directs the technical investigation, diagnosis, and resolution of the incident.
    *   **Key Responsibilities:**
        *   Leads the technical troubleshooting effort.
        *   Gathers necessary technical information (logs, metrics, errors).
        *   Identifies potential root causes.
        *   Proposes and implements mitigation and resolution steps.
        *   Briefs the IC on technical progress and findings.

### Incident Flow

1.  **Detection:**
    *   An alert is triggered by monitoring systems (e.g., high CPU, latency spike, disk full).
    *   A user or customer reports an issue impacting service.
    *   The on-call engineer acknowledges the alert/report.

2.  **Assessment:**
    *   The on-call engineer (or IC if escalation is immediate) assesses the severity and impact of the incident.
    *   Determine if a full incident response (with roles) is required.
    *   **Incident Commander (IC)** is assigned and takes charge.
    *   **IC** assigns **Communications Lead (CL)** and **Technical Lead (TL)**.
    *   An incident bridge (Zoom/Slack channel) is created for coordination.

3.  **Investigation:**
    *   **Technical Lead (TL)** and the technical team investigate the issue.
    *   Gather relevant data: logs, metrics, recent deployments, configuration changes.
    *   Hypothesize potential causes and test them.
    *   Identify the root cause or primary contributing factor.

4.  **Mitigation:**
    *   Implement temporary fixes or workarounds to reduce the impact and restore partial or full service.
    *   Examples: Rollback a deployment, restart a service, block malicious IP addresses, apply a temporary configuration change.
    *   **Goal:** Stop the bleeding and stabilize the system quickly.

5.  **Resolution:**
    *   Implement a permanent fix for the identified root cause.
    *   Verify that the fix is effective and the system is fully operational and stable.
    *   **IC** confirms resolution and declares the incident closed.

6.  **Post-Mortem / Review:**
    *   Within 24-48 hours of incident resolution, the **IC** leads a blameless post-mortem meeting.
    *   Document the incident: timeline, root cause, impact, mitigation steps, resolution, and lessons learned.
    *   Identify actionable items (e.g., monitoring improvements, code fixes, runbook updates, training).
    *   Assign owners and deadlines for these action items.
    *   Share the post-mortem with relevant teams and stakeholders.

7.  **Communication:**
    *   **Communications Lead (CL)** provides regular updates throughout the incident lifecycle.
    *   Updates should include: what happened, current status, impact, next steps, estimated time to resolution (if known).
    *   Frequency of updates is determined by incident severity and progress.
    *   Final communication confirms resolution and next steps (e.g., post-mortem availability).