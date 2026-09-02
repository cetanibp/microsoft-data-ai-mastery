# OPS-002 credential-free runtime

`observability.py` implements the executable SLO and routing contract without a database, Fabric workspace, endpoint, credential, or external notification destination.

It proves:

- attempts collapse to one logical occurrence;
- warnings remain accepted;
- a correctly enforced quality block does not become a platform-reliability failure;
- an unsafe quality block is a zero-tolerance breach;
- duration includes retry and recovery time;
- freshness stops at accepted publication;
- approved exclusions remain visible;
- error-budget consumption is deterministic;
- Development and Test simulate routing while Production requests notification; and
- deduplication is stable and P1 suppression is rejected.

The SQL Database objects are the durable deployment target. This Python module is a portable executable specification and test oracle, not a second operational store.
