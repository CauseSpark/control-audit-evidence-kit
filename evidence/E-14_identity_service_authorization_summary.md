# Authorization summary: Acme Enterprise Identity Service

> FICTIONAL. Provided to Internal Audit to support inherited controls.

| Field | Value |
|---|---|
| System | Acme Enterprise Identity Service (SSO and MFA) |
| Authorization | ATO signed 2026-03-10 by Morgan Lee, CIO and AO |
| Authorization term | 3 years, with ongoing monitoring |
| Most recent ConMon report | 2026-09-05, no open High findings |
| Controls offered for inheritance | IA-2, IA-2(1), IA-2(2), IA-5, AC-7 |

## Portal configuration (confirmed by the identity team on 2026-09-30)

- The HR Portal application is registered as a SAML 2.0 relying party.
- The access policy for the portal requires MFA for every sign-in. No exclusion groups are set.
- Lockout: 10 failed attempts in 15 minutes locks the account for 30 minutes.

/s/ Identity Services Manager (fictional)
