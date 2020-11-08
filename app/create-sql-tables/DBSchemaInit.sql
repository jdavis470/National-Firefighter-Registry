CREATE DATABASE FIREFIGHTER
GO

CREATE SCHEMA WORKER
GO

USE FIREFIGHTER
GO

CREATE TABLE [Worker](
	[WorkerID] [varchar](40) NOT NULL,
	[StudyCode] [varchar](50) NOT NULL,
	[GenderCode] [varchar](20) NULL,
	[EthnicityCode] [varchar](20) NULL,
	[StatusCode] [nvarchar](1) NULL,
	[CurrentResidentialStreet] [varchar](500) NULL,
	[CurrentResidentialCity] [varchar](50) NULL,
	[CurrentResidentialStateProv] [varchar](50) NULL,
	[CurrentResidentialPostalCode] [varchar](10) NULL,
	[CurrentResidentialCountry] [varchar](50) NULL,
	[BirthDate]  AS (case when isdate(((([Birthyear]+'-')+[BirthMonth])+'-')+[BirthDay])=(1) then CONVERT([date],((([Birthyear]+'-')+[BirthMonth])+'-')+[BirthDay],(111))  end),
	[BirthMonth] [varchar](2) NULL,
	[BirthDay] [varchar](2) NULL,
	[Birthyear] [varchar](4) NULL,
	[BirthPlaceCountry] [varchar](50) NULL,
	[BirthPlaceCity] [varchar](50) NULL,
	[BirthPlaceStateProv] [varchar](50) NULL,
	[LastObservedDate]  AS (case when isdate(((([LastObservedyear]+'-')+[LastObservedMonth])+'-')+[LastObservedDay])=(1) then CONVERT([date],((([LastObservedyear]+'-')+[LastObservedMonth])+'-')+[LastObservedDay],(111))  end),
	[LastObservedMonth] [varchar](2) NULL,
	[LastObservedDay] [varchar](2) NULL,
	[LastObservedyear] [varchar](4) NULL,
	[SSN] [varchar](50) NULL,
	[LastName] [varchar](50) NULL,
	[FirstName] [varchar](50) NULL,
	[MiddleName] [varchar](50) NULL,
	[LastNameAlias] [varchar](50) NULL,
	[FirstNameAlias] [varchar](50) NULL,
	[MiddleNameAlias] [varchar](50) NULL,
	[Site] [varchar](50) NULL,
	[DiagnosedWithCancer] [bit] NULL,
	[DiagnosedWithCancerStateProv] [varchar](50) NULL,
	[PrimaryEmailAddress] [varchar](300) NULL,
	[OptInEmails] [bit] NULL,
	[MobilePhoneNumber] [varchar](15) NULL,
	[OptInTextMessages] [bit] NULL,
	[Comments] [varchar](1000) NULL,
	[IdmsID] [int] NULL,
	[ImportCode] [varchar](2500) NULL,
	[SourceFile] [varchar](2500) NULL,
	[LastUpdateDate] [datetime] NULL,
	[LastUpdatedBy] [varchar](255) NULL,
	[CreateDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL 
)

CREATE TABLE [WorkerRace](
	[WorkerID] [varchar](40) NOT NULL,
	[StudyCode] [varchar](50) NOT NULL,
	[RaceCode] [varchar](20) NOT NULL,
	[ImportCode] [varchar](2500) NULL,
	[SourceFile] [varchar](2500) NULL,
	[LastUpdateDate] [datetime] NULL,
	[LastUpdatedBy] [varchar](255) NULL,
	[CreateDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL 
)