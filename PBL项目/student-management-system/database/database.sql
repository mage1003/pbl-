-- 学生信息管理系统数据库结构
-- 创建时间: 2024年12月
-- 版本: v1.0

-- =============================================
-- 1. 用户表 (users)
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- 创建用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- =============================================
-- 2. 管理员表 (admins)
-- =============================================
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    permissions TEXT,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建管理员表索引
CREATE INDEX idx_admins_user_id ON admins(user_id);

-- =============================================
-- 3. 学生表 (students)
-- =============================================
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    major VARCHAR(100) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    class_name VARCHAR(50),
    enrollment_date DATE NOT NULL,
    birth_date DATE,
    address TEXT,
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建学生表索引
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_students_major ON students(major);

-- =============================================
-- 4. 课程表 (courses)
-- =============================================
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    description TEXT,
    credits INTEGER DEFAULT 1,
    semester VARCHAR(20) NOT NULL,
    teacher_name VARCHAR(100) NOT NULL,
    max_students INTEGER DEFAULT 50,
    classroom VARCHAR(100),
    schedule VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- 创建课程表索引
CREATE INDEX idx_courses_code ON courses(course_code);
CREATE INDEX idx_courses_teacher ON courses(teacher_name);
CREATE INDEX idx_courses_semester ON courses(semester);

-- =============================================
-- 5. 成绩表 (grades)
-- =============================================
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    midterm_score REAL,
    final_score REAL,
    assignment_score REAL,
    total_score REAL,
    grade_letter VARCHAR(5),
    semester VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id, semester)
);

-- 创建成绩表索引
CREATE INDEX idx_grades_student_id ON grades(student_id);
CREATE INDEX idx_grades_course_id ON grades(course_id);
CREATE INDEX idx_grades_semester ON grades(semester);

-- =============================================
-- 插入测试数据
-- =============================================

-- 插入管理员用户
INSERT OR IGNORE INTO users (username, email, password_hash, full_name, is_admin) VALUES 
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQBa9V3j5.5z3uW', '系统管理员', 1);

-- 插入学生用户
INSERT OR IGNORE INTO users (username, email, password_hash, full_name, phone) VALUES 
('student1', 'student1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQBa9V3j5.5z3uW', '张三', '13800138001'),
('student2', 'student2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQBa9V3j5.5z3uW', '李四', '13800138002'),
('student3', 'student3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewQBa9V3j5.5z3uW', '王五', '13800138003');

-- 插入学生档案
INSERT OR IGNORE INTO students (user_id, student_id, major, grade, class_name, enrollment_date, birth_date, address, emergency_contact, emergency_phone) VALUES 
((SELECT id FROM users WHERE username = 'student1'), '2021001', '计算机科学与技术', '2021级', '计科1班', '2021-09-01', '2003-05-15', '北京市海淀区中关村大街1号', '张父', '13900139001'),
((SELECT id FROM users WHERE username = 'student2'), '2021002', '软件工程', '2021级', '软工1班', '2021-09-01', '2003-07-22', '北京市海淀区中关村大街2号', '李母', '13900139002'),
((SELECT id FROM users WHERE username = 'student3'), '2021003', '信息安全', '2021级', '安信1班', '2021-09-01', '2003-09-10', '北京市海淀区中关村大街3号', '王父', '13900139003');

-- 插入课程数据
INSERT OR IGNORE INTO courses (course_code, course_name, description, credits, semester, teacher_name, max_students, classroom, schedule) VALUES 
('CS101', '程序设计基础', '介绍程序设计的基本概念和方法', 3, '2021-2022-1', '陈教授', 80, 'A101', '周一 14:00-16:00'),
('CS102', '数据结构与算法', '学习基本数据结构和算法设计', 4, '2021-2022-2', '李教授', 60, 'A102', '周二 10:00-12:00'),
('CS201', '数据库系统', '关系数据库理论和实践', 3, '2022-2023-1', '王教授', 70, 'B201', '周三 14:00-16:00'),
('CS202', '计算机网络', '网络协议和系统架构', 3, '2022-2023-2', '赵教授', 60, 'B202', '周四 10:00-12:00'),
('CS301', '软件工程', '软件开发和项目管理', 2, '2023-2024-1', '刘教授', 50, 'C301', '周五 14:00-16:00');

-- 插入成绩数据
INSERT OR IGNORE INTO grades (student_id, course_id, midterm_score, final_score, assignment_score, total_score, grade_letter, semester) VALUES 
-- 张三的成绩
((SELECT id FROM students WHERE student_id = '2021001'), (SELECT id FROM courses WHERE course_code = 'CS101'), 85, 88, 90, 87.7, 'B', '2021-2022-1'),
((SELECT id FROM students WHERE student_id = '2021001'), (SELECT id FROM courses WHERE course_code = 'CS102'), 78, 82, 85, 81.7, 'B', '2021-2022-2'),
((SELECT id FROM students WHERE student_id = '2021001'), (SELECT id FROM courses WHERE course_code = 'CS201'), 92, 89, 91, 90.3, 'A', '2022-2023-1'),
((SELECT id FROM students WHERE student_id = '2021001'), (SELECT id FROM courses WHERE course_code = 'CS202'), 88, 85, 87, 86.6, 'B', '2022-2023-2'),
-- 李四的成绩
((SELECT id FROM students WHERE student_id = '2021002'), (SELECT id FROM courses WHERE course_code = 'CS101'), 90, 92, 89, 90.7, 'A', '2021-2022-1'),
((SELECT id FROM students WHERE student_id = '2021002'), (SELECT id FROM courses WHERE course_code = 'CS102'), 85, 88, 86, 86.6, 'B', '2021-2022-2'),
((SELECT id FROM students WHERE student_id = '2021002'), (SELECT id FROM courses WHERE course_code = 'CS201'), 87, 90, 88, 88.3, 'B', '2022-2023-1'),
-- 王五的成绩
((SELECT id FROM students WHERE student_id = '2021003'), (SELECT id FROM courses WHERE course_code = 'CS101'), 82, 85, 88, 85.0, 'B', '2021-2022-1'),
((SELECT id FROM students WHERE student_id = '2021003'), (SELECT id FROM courses WHERE course_code = 'CS102'), 80, 83, 82, 81.9, 'B', '2021-2022-2'),
((SELECT id FROM students WHERE student_id = '2021003'), (SELECT id FROM courses WHERE course_code = 'CS201'), 89, 91, 90, 90.0, 'A', '2022-2023-1');

-- =============================================
-- 创建视图 (便于查询)
-- =============================================

-- 学生详细信息视图
CREATE VIEW IF NOT EXISTS v_student_details AS
SELECT 
    s.id,
    s.student_id,
    u.username,
    u.full_name,
    u.email,
    u.phone,
    s.major,
    s.grade,
    s.class_name,
    s.enrollment_date,
    s.birth_date,
    s.address,
    s.emergency_contact,
    s.emergency_phone,
    s.created_at
FROM students s
JOIN users u ON s.user_id = u.id;

-- 成绩详细信息视图
CREATE VIEW IF NOT EXISTS v_grade_details AS
SELECT 
    g.id,
    g.student_id,
    s.student_id as student_number,
    u.full_name as student_name,
    c.course_code,
    c.course_name,
    c.credits,
    g.midterm_score,
    g.final_score,
    g.assignment_score,
    g.total_score,
    g.grade_letter,
    g.semester,
    g.created_at,
    g.updated_at
FROM grades g
JOIN students s ON g.student_id = s.id
JOIN users u ON s.user_id = u.id
JOIN courses c ON g.course_id = c.id;

-- =============================================
-- 触发器 (自动更新updated_at字段)
-- =============================================

CREATE TRIGGER IF NOT EXISTS update_grades_updated_at 
AFTER UPDATE ON grades
FOR EACH ROW
BEGIN
    UPDATE grades SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- =============================================
-- 数据完整性约束
-- =============================================

-- 确保成绩在合理范围内
CREATE TRIGGER IF NOT EXISTS validate_grade_scores
BEFORE INSERT ON grades
FOR EACH ROW
BEGIN
    -- 检查分数是否在合理范围内
    SELECT CASE
        WHEN NEW.midterm_score < 0 OR NEW.midterm_score > 100 THEN
            RAISE(ABORT, '期中成绩必须在0-100之间')
        WHEN NEW.final_score < 0 OR NEW.final_score > 100 THEN
            RAISE(ABORT, '期末成绩必须在0-100之间')
        WHEN NEW.assignment_score < 0 OR NEW.assignment_score > 100 THEN
            RAISE(ABORT, '作业成绩必须在0-100之间')
    END;
END;

-- 自动计算总分和等级
CREATE TRIGGER IF NOT EXISTS calculate_grade_total
BEFORE INSERT ON grades
FOR EACH ROW
BEGIN
    -- 如果所有分数都存在，计算总分
    SELECT CASE
        WHEN NEW.midterm_score IS NOT NULL 
             AND NEW.final_score IS NOT NULL 
             AND NEW.assignment_score IS NOT NULL THEN
            NEW.total_score = NEW.midterm_score * 0.3 + NEW.final_score * 0.5 + NEW.assignment_score * 0.2,
            NEW.grade_letter = CASE
                WHEN NEW.total_score >= 90 THEN 'A'
                WHEN NEW.total_score >= 80 THEN 'B'
                WHEN NEW.total_score >= 70 THEN 'C'
                WHEN NEW.total_score >= 60 THEN 'D'
                ELSE 'F'
            END
    END;
END;

-- =============================================
-- 数据库统计信息
-- =============================================

-- 显示表统计信息
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'students' as table_name, COUNT(*) as record_count FROM students
UNION ALL
SELECT 'courses' as table_name, COUNT(*) as record_count FROM courses
UNION ALL
SELECT 'grades' as table_name, COUNT(*) as record_count FROM grades
UNION ALL
SELECT 'admins' as table_name, COUNT(*) as record_count FROM admins;

-- 完成数据库初始化
-- 总计插入记录: 用户4人, 学生3人, 课程5门, 成绩10条
