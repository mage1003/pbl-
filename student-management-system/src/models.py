from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户表 - 基础用户信息"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Admin(db.Model):
    """管理员表 - 扩展管理员信息"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    permissions = db.Column(db.Text)  # JSON格式存储权限
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('admin_profile', uselist=False))
    
    def __repr__(self):
        return f'<Admin {self.user.username if self.user else "Unknown"}>'

class Student(db.Model):
    """学生表 - 学生详细信息"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    major = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=False)  # 年级
    class_name = db.Column(db.String(50))  # 班级
    enrollment_date = db.Column(db.Date, nullable=False)
    birth_date = db.Column(db.Date)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    
    def __repr__(self):
        return f'<Student {self.student_id}>'

class Course(db.Model):
    """课程表 - 课程信息"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, default=1)
    semester = db.Column(db.String(20), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    max_students = db.Column(db.Integer, default=50)
    classroom = db.Column(db.String(100))
    schedule = db.Column(db.String(200))  # 上课时间
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Course {self.course_code}>'

class Grade(db.Model):
    """成绩表 - 学生成绩记录"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    midterm_score = db.Column(db.Float)
    final_score = db.Column(db.Float)
    assignment_score = db.Column(db.Float)
    total_score = db.Column(db.Float)
    grade_letter = db.Column(db.String(5))  # A, B, C, D, F
    semester = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # 关联关系
    student = db.relationship('Student', backref=db.backref('grades', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('grades', lazy='dynamic'))
    
    def calculate_total_score(self):
        """计算总成绩"""
        if self.midterm_score and self.final_score and self.assignment_score:
            self.total_score = (self.midterm_score * 0.3 + 
                              self.final_score * 0.5 + 
                              self.assignment_score * 0.2)
            self.grade_letter = self.get_letter_grade(self.total_score)
            return True
        return False
    
    def get_letter_grade(self, score):
        """根据分数获取字母等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def __repr__(self):
        return f'<Grade Student:{self.student_id} Course:{self.course_id}>'
