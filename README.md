# dns-health-auditor

A practical, zero-dependency-heavy Python CLI that audits a domain's DNS health — checks core records, email authentication (SPF / DKIM / DMARC), DNSSEC, and propagation across public resolvers. Designed for IT ops, SREs, and security teams who need a fast, scriptable second opinion on a zone's configuration.

## What it checks

| Category | Checks |
|---|---|
| **Core records** | `A`, `AAAA`, `MX`, `NS`, `SOA`, `CNAME` at apex |
| **Email auth** | SPF syntax + lookups, DMARC policy + coverage, DKIM selector discovery |
| **DNSSEC** | `DNSKEY` and `DS` presence, algorithm inspection |
| **Propagation** | Parallel lookups across 8 public resolvers (Cloudflare, Google, Quad9, OpenDNS, Level3, Verisign, AdGuard, dns0.eu) with disagreement detection |
| **Performance** | Median and p95 resolver response times |
| **Hygiene** | Duplicate SPF records, `+all` wildcards, missing `v=` tags, long TTLs on apex A records, MX pointing to CNAME, etc. |

Each finding is scored `INFO` / `WARN` / `FAIL` and a final letter grade (A+ → F) is computed so you can track zones over time.

## Install

```bash
pip install dns-health-auditor
# or, from source:
git clone https://github.com/intruderfr/dns-health-auditor.git
cd dns-health-auditor
pip install -e .
```

Requires Python 3.9+. The only runtime dependency is [`dnspython`](https://www.dnspython.org/).

## Usage

```bash
# Audit a single domain (human-readable table)
dns-audit example.com

# JSON output — pipe to jq, ingest into a SIEM, or diff against yesterday's run
dns-audit example.com --json > example.com.json

# Audit multiple domains from a file, one per line
dns-audit -f domains.txt --json

# Only run a subset of checks
dns-audit example.com --checks records,email

# Specify DKIM selectors to probe (defaults to the common set)
dns-audit example.com --dkim-selectors google,k1,selector1,selector2,mandrill

# Use a specific resolver instead of system DNS for the authoritative lookup
dns-audit example.com --resolver 1.1.1.1

# Exit non-zero on any FAIL — useful for CI pipelines
dns-audit example.com --fail-on fail
```

### Example output

```
DNS Health Report — example.com                                  Grade: B+
────────────────────────────────────────────────────────────────────────
[PASS] A        93.184.216.34
[PASS] AAAA     2606:2800:220:1:248:1893:25c8:1946
[PASS] NS       a.iana-servers.net, b.iana-servers.net (2 authoritative)
[PASS] MX       no MX record — domain will not receive email (informational)
[PASS] SPF      v=spf1 -all  (0 DNS lookups, within the 10-lookup RFC limit)
[WARN] DMARC    p=none — policy is monitor-only, no enforcement
[PASS] DNSSEC   RSASHA256 / 2048-bit, DS published at parent
[WARN] TTL      apex A record TTL of 86400s is higher than recommended 3600s
[PASS] PROP     all 8 public resolvers agree on A record
────────────────────────────────────────────────────────────────────────
Score: 87/100    9 checks, 0 fails, 2 warns    runtime 1.84s
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed (or only `INFO`/`WARN` with `--fail-on fail`) |
| `1` | Any `FAIL` encountered (with `--fail-on fail`, the default) |
| `2` | CLI/usage error |
| `3` | Resolution error — couldn't contact any resolver |

## Programmatic use

```python
from dns_auditor import audit_domain

report = audit_domain("example.com", dkim_selectors=["google", "k1"])
print(report.grade)           # "B+"
print(report.score)            # 87
for finding in report.findings:
    print(finding.severity, finding.check, finding.message)
```

## Why this exists

DNS misconfiguration is still one of the cheapest ways to lose email deliverability, leak subdomains, or fail a security audit. Dozens of online tools do one piece of this — but at 3 AM when a customer says "our emails are going to spam," you want something you can `pip install`, run offline, diff against yesterday, and drop into a GitHub Actions job that fails the build before the change hits production.

That's the whole pitch. No SaaS, no sign-up, no dashboard — just a CLI and a JSON report.

## Roadmap

- [ ] BIMI record check (`default._bimi.<domain>`)
- [ ] MTA-STS and TLS-RPT
- [ ] CAA record validation
- [ ] Shodan / CT-log subdomain enumeration (opt-in)
- [ ] GitHub Action wrapper

## License

MIT — see [LICENSE](LICENSE).

## Author

**Aslam Ahamed** — Head of IT @ Prestige One Developments, Dubai
[LinkedIn](https://www.linkedin.com/in/aslam-ahamed/) · [@intruderfr](https://github.com/intruderfr)
