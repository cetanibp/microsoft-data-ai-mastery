CREATE TABLE [ctrl].[ObjectSchedule] (
    [release_id]              UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key]    VARCHAR (150)    NOT NULL,
    [schedule_key]            VARCHAR (100)    NOT NULL,
    [deadline_offset_minutes] INT              NULL,
    CONSTRAINT [PK_ctrl_ObjectSchedule] PRIMARY KEY CLUSTERED ([release_id] ASC, [ingestion_object_key] ASC, [schedule_key] ASC),
    CONSTRAINT [CK_ctrl_ObjectSchedule_deadline] CHECK ([deadline_offset_minutes] IS NULL OR [deadline_offset_minutes]>=(0) AND [deadline_offset_minutes]<=(10080)),
    CONSTRAINT [FK_ctrl_ObjectSchedule_object] FOREIGN KEY ([release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ctrl_ObjectSchedule_schedule] FOREIGN KEY ([release_id], [schedule_key]) REFERENCES [ctrl].[Schedule] ([release_id], [schedule_key])
);


GO

