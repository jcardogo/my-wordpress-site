IF DB_ID('school_booking') IS NULL
BEGIN
    CREATE DATABASE school_booking;
END
GO

USE school_booking;
GO

IF OBJECT_ID('dbo.bookings', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.bookings;
END
GO

IF OBJECT_ID('dbo.classes', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.classes;
END
GO

IF OBJECT_ID('dbo.students', 'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.students;
END
GO

CREATE TABLE dbo.students (
    id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(150) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE TABLE dbo.classes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    code NVARCHAR(40) NOT NULL UNIQUE,
    name NVARCHAR(150) NOT NULL,
    description NVARCHAR(500) NULL,
    capacity INT NOT NULL DEFAULT 25,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE TABLE dbo.bookings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    tracking_id NVARCHAR(36) NOT NULL UNIQUE,
    status NVARCHAR(20) NOT NULL DEFAULT 'booked',
    booked_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIMEOFFSET NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_bookings_students FOREIGN KEY (student_id) REFERENCES dbo.students(id),
    CONSTRAINT FK_bookings_classes FOREIGN KEY (class_id) REFERENCES dbo.classes(id),
    CONSTRAINT UQ_booking_per_student_class UNIQUE (student_id, class_id)
);
GO

CREATE INDEX IX_bookings_tracking_id ON dbo.bookings(tracking_id);
CREATE INDEX IX_students_email ON dbo.students(email);
GO
