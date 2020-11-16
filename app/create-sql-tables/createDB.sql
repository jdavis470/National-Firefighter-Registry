-- This is the main caller for each script
SET NOCOUNT ON
GO

USE master
GO

PRINT 'CREATING DATABASE - DFSE_FRB_WORKER'
IF EXISTS (SELECT 1 FROM SYS.DATABASES WHERE NAME = 'DFSE_FRB_WORKER')
DROP DATABASE [DFSE_FRB_WORKER]
GO
CREATE DATABASE [DFSE_FRB_WORKER]
GO

PRINT 'CREATING SCHEMA - worker'
IF EXISTS (SELECT 1 FROM SYS.SCHEMAS WHERE NAME = 'worker')
DROP SCHEMA [worker]
GO
USE [DFSE_FRB_WORKER]
GO
CREATE SCHEMA [worker]
GO

PRINT 'CREATING EXAMPLE USER - PeterPan'
CREATE LOGIN [PeterPan] WITH PASSWORD = 'Password!123'
GO
CREATE USER [workerGroup1]
  FROM LOGIN [PeterPan]
  WITH DEFAULT_SCHEMA = [worker];
GO
GRANT
      SELECT, INSERT, UPDATE, DELETE, ALTER
ON SCHEMA::[worker]
      TO [workerGroup1]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

:On Error exit

PRINT 'CREATING TABLE - Worker'
:r ./sqlfiles/worker.Worker.Table.sql
PRINT 'CREATING TABLE - WorkerRace'
:r ./sqlfiles/worker.WorkerRace.Table.sql
PRINT 'CREATING TABLE - WorkerFireDepartment'
:r ./sqlfiles/worker.WorkerFireDepartment.Table.sql
PRINT 'CREATING TABLE - WorkerObservation'
:r ./sqlfiles/worker.WorkerObservation.Table.sql

PRINT 'DATABASE CREATE IS COMPLETE'
GO