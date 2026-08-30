CREATE TABLE [ctrl].[Schedule] (
    [release_id]             UNIQUEIDENTIFIER NOT NULL,
    [schedule_key]           VARCHAR (100)    NOT NULL,
    [schedule_type]          VARCHAR (20)     NOT NULL,
    [iana_time_zone]         VARCHAR (100)    NOT NULL,
    [trigger_alias]          VARCHAR (100)    NOT NULL,
    [daily_local_start]      TIME (0)         NULL,
    [eligibility_window_min] INT              NULL,
    [interval_minutes]       INT              NULL,
    [event_alias]            VARCHAR (100)    NULL,
    [is_catchup_enabled]     BIT              CONSTRAINT [DF_ctrl_Schedule_catchup] DEFAULT ((1)) NOT NULL,
    CONSTRAINT [PK_ctrl_Schedule] PRIMARY KEY CLUSTERED ([release_id] ASC, [schedule_key] ASC),
    CONSTRAINT [CK_ctrl_Schedule_interval] CHECK ([interval_minutes] IS NULL OR [interval_minutes]>=(1) AND [interval_minutes]<=(10080)),
    CONSTRAINT [CK_ctrl_Schedule_safe_aliases] CHECK (NOT [trigger_alias] like '%://%' AND NOT [trigger_alias] like '%=%' AND ([event_alias] IS NULL OR NOT [event_alias] like '%://%' AND NOT [event_alias] like '%=%')),
    CONSTRAINT [CK_ctrl_Schedule_shape] CHECK ([schedule_type]='DAILY' AND [daily_local_start] IS NOT NULL AND [eligibility_window_min] IS NOT NULL OR [schedule_type]='INTERVAL' AND [interval_minutes] IS NOT NULL OR [schedule_type]='EVENT' AND [event_alias] IS NOT NULL OR [schedule_type]='MANUAL'),
    CONSTRAINT [CK_ctrl_Schedule_type] CHECK ([schedule_type]='MANUAL' OR [schedule_type]='EVENT' OR [schedule_type]='INTERVAL' OR [schedule_type]='DAILY'),
    CONSTRAINT [CK_ctrl_Schedule_window] CHECK ([eligibility_window_min] IS NULL OR [eligibility_window_min]>=(1) AND [eligibility_window_min]<=(1440)),
    CONSTRAINT [FK_ctrl_Schedule_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

