Use the full commands below from the repository root. Do not launch another native Phoenix or Guardrails instance on the same published ports. Compose waits for configured healthy dependencies, but Phoenix is only service_started in this file. The API Docker health check is liveness; it is not an end-to-end quality probe. If a port is already in use, inspect its owner before changing API_PORT or GATEWAY_PORT. A container-name conflict can follow overlapping Compose operations: stop the competing operation, inspect ps -a and preserve volumes. Do not remove unrelated orphan containers automatically.

The complete command sequence is in the companion lab guide.

Use one Compose project and one operation at a time.