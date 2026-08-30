/*
FAB-001 — Northstar ingestion control plane
Target: SQL Database in Microsoft Fabric

This script creates only database schemas. It is safe to rerun and contains
no environment identifiers, endpoints, credentials, or secret values.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

IF SCHEMA_ID(N'ctrl') IS NULL
    EXEC(N'CREATE SCHEMA ctrl AUTHORIZATION dbo;');
GO

IF SCHEMA_ID(N'ops') IS NULL
    EXEC(N'CREATE SCHEMA ops AUTHORIZATION dbo;');
GO

IF SCHEMA_ID(N'audit') IS NULL
    EXEC(N'CREATE SCHEMA audit AUTHORIZATION dbo;');
GO
