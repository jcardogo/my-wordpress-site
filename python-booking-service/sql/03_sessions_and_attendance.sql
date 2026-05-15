USE school_booking;
GO

IF OBJECT_ID('dbo.attendance_logs', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.attendance_logs;
END
GO

IF OBJECT_ID('dbo.class_sessions', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.class_sessions;
END
GO

CREATE TABLE dbo.class_sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    class_id INT NOT NULL,
    session_title NVARCHAR(150) NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NULL,
    end_time TIME NULL,
    location NVARCHAR(150) NULL,
    created_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_class_sessions_classes FOREIGN KEY (class_id) REFERENCES dbo.classes(id)
);
GO

CREATE TABLE dbo.attendance_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    session_id INT NOT NULL,
    student_id INT NOT NULL,
    attendance_status NVARCHAR(20) NOT NULL,
    notes NVARCHAR(500) NULL,
    marked_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_attendance_logs_sessions FOREIGN KEY (session_id) REFERENCES dbo.class_sessions(id),
    CONSTRAINT FK_attendance_logs_students FOREIGN KEY (student_id) REFERENCES dbo.students(id),
    CONSTRAINT UQ_attendance_session_student UNIQUE (session_id, student_id)
);
GO

CREATE INDEX IX_class_sessions_date ON dbo.class_sessions(session_date);
CREATE INDEX IX_attendance_status ON dbo.attendance_logs(attendance_status);
GO
