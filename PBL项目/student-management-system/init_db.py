#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生信息管理系统 - 数据库初始化脚本
用于创建数据库表和插入初始数据
"""

import sys
import os
import sqlite3
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import db, User, Admin, Student, Course, Grade

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建所有表
    db.create_all()
    print("✓ 数据库表创建成功")
    
    # 创建默认管理员账户
    create_default_admin()
    
    # 创建示例数据
    create_sample_data()
    
    print("✓ 数据库初始化完成！")
    print("\n演示账户信息:")
    print("管理员: admin / admin123")
    print("学生:   student1 / student123")

def create_default_admin():
    """创建默认管理员账户"""
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            full_name='系统管理员',
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("✓ 默认管理员账户创建成功")

def create_sample_data():
    """创建示例数据"""
    # 创建示例学生用户
    students_data = [
        {
            'username': 'student1',
            'email': 'student1@example.com',
            'full_name': '张三',
            'phone': '13800138001',
            'student_id': '2021001',
            'major': '计算机科学与技术',
            'grade': '2021级',
            'class_name': '计科1班',
            'enrollment_date': '2021-09-01',
            'birth_date': '2003-05-15',
            'address': '北京市海淀区中关村大街1号',
            'emergency_contact': '张父',
            'emergency_phone': '13900139001'
        },
        {
            'username': 'student2',
            'email': 'student2@example.com',
            'full_name': '李四',
            'phone': '13800138002',
            'student_id': '2021002',
            'major': '软件工程',
            'grade': '2021级',
            'class_name': '软工1班',
            'enrollment_date': '2021-09-01',
            'birth_date': '2003-07-22',
            'address': '北京市海淀区中关村大街2号',
            'emergency_contact': '李母',
            'emergency_phone': '13900139002'
        },
        {
            'username': 'student3',
            'email': 'student3@example.com',
            'full_name': '王五',
            'phone': '13800138003',
            'student_id': '2021003',
            'major': '信息安全',
            'grade': '2021级',
            'class_name': '安信1班',
            'enrollment_date': '2021-09-01',
            'birth_date': '2003-09-10',
            'address': '北京市海淀区中关村大街3号',
            'emergency_contact': '王父',
            'emergency_phone': '13900139003'
        }
    ]
    
    # 创建用户和档案
    for student_data in students_data:
        existing_user = User.query.filter_by(username=student_data['username']).first()
        if not existing_user:
            # 创建用户
            user = User(
                username=student_data['username'],
                email=student_data['email'],
                full_name=student_data['full_name'],
                phone=student_data['phone']
            )
            user.set_password('student123')
            db.session.add(user)
            db.session.flush()  # 获取用户ID
            
            # 创建学生档案
            student = Student(
                user_id=user.id,
                student_id=student_data['student_id'],
                major=student_data['major'],
                grade=student_data['grade'],
                class_name=student_data['class_name'],
                enrollment_date=datetime.strptime(student_data['enrollment_date'], '%Y-%m-%d'),
                birth_date=datetime.strptime(student_data['birth_date'], '%Y-%m-%d'),
                address=student_data['address'],
                emergency_contact=student_data['emergency_contact'],
                emergency_phone=student_data['emergency_phone']
            )
            db.session.add(student)
    
    db.session.commit()
    print("✓ 示例学生数据创建成功")
    
    # 创建课程数据
    courses_data = [
        {
            'course_code': 'CS101',
            'course_name': '程序设计基础',
            'description': '介绍程序设计的基本概念和方法',
            'credits': 3,
            'semester': '2021-2022-1',
            'teacher_name': '陈教授',
            'max_students': 80,
            'classroom': 'A101',
            'schedule': '周一 14:00-16:00'
        },
        {
            'course_code': 'CS102',
            'course_name': '数据结构与算法',
            'description': '学习基本数据结构和算法设计',
            'credits': 4,
            'semester': '2021-2022-2',
            'teacher_name': '李教授',
            'max_students': 60,
            'classroom': 'A102',
            'schedule': '周二 10:00-12:00'
        },
        {
            'course_code': 'CS201',
            'course_name': '数据库系统',
            'description': '关系数据库理论和实践',
            'credits': 3,
            'semester': '2022-2023-1',
            'teacher_name': '王教授',
            'max_students': 70,
            'classroom': 'B201',
            'schedule': '周三 14:00-16:00'
        },
        {
            'course_code': 'CS202',
            'course_name': '计算机网络',
            'description': '网络协议和系统架构',
            'credits': 3,
            'semester': '2022-2023-2',
            'teacher_name': '赵教授',
            'max_students': 60,
            'classroom': 'B202',
            'schedule': '周四 10:00-12:00'
        },
        {
            'course_code': 'CS301',
            'course_name': '软件工程',
            'description': '软件开发和项目管理',
            'credits': 2,
            'semester': '2023-2024-1',
            'teacher_name': '刘教授',
            'max_students': 50,
            'classroom': 'C301',
            'schedule': '周五 14:00-16:00'
        }
    ]
    
    # 创建课程
    for course_data in courses_data:
        existing_course = Course.query.filter_by(course_code=course_data['course_code']).first()
        if not existing_course:
            course = Course(**course_data)
            db.session.add(course)
    
    db.session.commit()
    print("✓ 课程数据创建成功")
    
    # 创建成绩数据
    create_grades_data()

def create_grades_data():
    """创建成绩数据"""
    # 获取学生和课程对象
    students = Student.query.all()
    courses = Course.query.all()
    
    grades_data = [
        # 张三的成绩
        {'student': '2021001', 'course': 'CS101', 'midterm': 85, 'final': 88, 'assignment': 90, 'semester': '2021-2022-1'},
        {'student': '2021001', 'course': 'CS102', 'midterm': 78, 'final': 82, 'assignment': 85, 'semester': '2021-2022-2'},
        {'student': '2021001', 'course': 'CS201', 'midterm': 92, 'final': 89, 'assignment': 91, 'semester': '2022-2023-1'},
        {'student': '2021001', 'course': 'CS202', 'midterm': 88, 'final': 85, 'assignment': 87, 'semester': '2022-2023-2'},
        
        # 李四的成绩
        {'student': '2021002', 'course': 'CS101', 'midterm': 90, 'final': 92, 'assignment': 89, 'semester': '2021-2022-1'},
        {'student': '2021002', 'course': 'CS102', 'midterm': 85, 'final': 88, 'assignment': 86, 'semester': '2021-2022-2'},
        {'student': '2021002', 'course': 'CS201', 'midterm': 87, 'final': 90, 'assignment': 88, 'semester': '2022-2023-1'},
        
        # 王五的成绩
        {'student': '2021003', 'course': 'CS101', 'midterm': 82, 'final': 85, 'assignment': 88, 'semester': '2021-2022-1'},
        {'student': '2021003', 'course': 'CS102', 'midterm': 80, 'final': 83, 'assignment': 82, 'semester': '2021-2022-2'},
        {'student': '2021003', 'course': 'CS201', 'midterm': 89, 'final': 91, 'assignment': 90, 'semester': '2022-2023-1'}
    ]
    
    for grade_data in grades_data:
        # 查找学生和课程
        student = Student.query.filter_by(student_id=grade_data['student']).first()
        course = Course.query.filter_by(course_code=grade_data['course']).first()
        
        if student and course:
            # 检查是否已存在该成绩记录
            existing_grade = Grade.query.filter_by(
                student_id=student.id,
                course_id=course.id,
                semester=grade_data['semester']
            ).first()
            
            if not existing_grade:
                grade = Grade(
                    student_id=student.id,
                    course_id=course.id,
                    midterm_score=grade_data['midterm'],
                    final_score=grade_data['final'],
                    assignment_score=grade_data['assignment'],
                    semester=grade_data['semester']
                )
                # 计算总分和等级
                grade.calculate_total_score()
                db.session.add(grade)
    
    db.session.commit()
    print("✓ 成绩数据创建成功")

def show_statistics():
    """显示数据库统计信息"""
    print("\n=== 数据库统计信息 ===")
    print(f"用户总数: {User.query.count()}")
    print(f"学生总数: {Student.query.count()}")
    print(f"课程总数: {Course.query.count()}")
    print(f"成绩记录总数: {Grade.query.count()}")
    print(f"管理员总数: {Admin.query.count()}")

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        init_database()
        show_statistics()
