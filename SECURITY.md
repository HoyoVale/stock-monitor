# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| < 0.4.0 | :x:                |

## Reporting a Vulnerability

**Do not open a public issue.**

Report via GitHub Security Advisory:
https://github.com/HoyoVale/stock-monitor/security/advisories/new

### Response SLA
- Acknowledgment: within 48 hours
- Assessment + fix: 3-14 days depending on severity
- Disclosure: coordinated, after fix released

## Security Features

- Rate limiting: configurable via `RATE_LIMIT` env (default 60/min)
- JWT authentication with configurable expiry (`JWT_EXPIRE_MINUTES`)
- CORS origins controlled via `CORS_ORIGINS` env
- CodeQL analysis on push/PR + weekly schedule
- Dependabot with grouped updates
- All actions pinned to commit SHA

## Production Checklist

Before deploying to production:
- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Set `CORS_ORIGINS` to specific domain(s)
- [ ] Set `RATE_LIMIT` to production-appropriate value
- [ ] Run `alembic upgrade head` for database migrations
- [ ] Enable HTTPS
