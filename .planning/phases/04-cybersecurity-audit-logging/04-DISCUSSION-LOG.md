# Phase 4: Cybersecurity & Audit Logging Discussion Log

**Date:** 2026-08-13
**Phase:** 04 - Cybersecurity & Audit Logging

## Area 1: Audit Logging Architecture (SECU-01, SECU-04)
- **Options Considered:**
  1. Unified DB `AuditLog` table with `category`, `severity`, `action`, `actor_id`, `ip_address`, and JSON `details` (Selected).
  2. Separate `SecurityEvent` and `AdminAuditLog` tables in PostgreSQL.
- **Decision:** Unified `AuditLog` table capturing all security events and admin actions in a single queryable audit trail.

## Area 2: OWASP API Security Controls (SECU-02)
- **Options Considered:**
  1. Custom FastAPI Middleware adding standard OWASP headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, HSTS, CSP) + global request sanitization (Selected).
  2. Basic FastAPI CORS middleware only.
- **Decision:** Custom middleware enforcing OWASP security headers on all HTTP responses.

## Area 3: Threat Intelligence Simulation (SECU-03)
- **Options Considered:**
  1. Deterministic mock `ThreatIntelService` with pre-configured malicious IP subnets (Tor exit nodes, proxy networks, botnets) returning threat score (0-100) and risk category (Selected).
  2. Random threat score generator on request headers.
- **Decision:** Deterministic `ThreatIntelService` analyzing client IP addresses against simulated threat feeds.

## Area 4: Threat Action Enforcement
- **Options Considered:**
  1. Automatically block high-risk threat IPs ($\ge 80$), log a `CRITICAL` security event, and override payment execution to `BLOCKED` (Selected).
  2. Log security event only for admin visualization without blocking requests.
- **Decision:** Real-time threat enforcement blocking transfers and logging `CRITICAL` audit events when threat score $\ge 80$.
