USE school_booking;
GO

INSERT INTO dbo.classes (code, name, description, capacity)
VALUES
    ('MATH-101', 'Mathematics Foundations', 'Basic arithmetic, algebra, and logic.', 30),
    ('SCI-201', 'Introduction to Science', 'Scientific method and practical experiments.', 28),
    ('ENG-110', 'English Communication', 'Writing and speaking fundamentals.', 25),
    ('CS-120', 'Computer Basics', 'Digital literacy and problem-solving using software.', 24);
GO
