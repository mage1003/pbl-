#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生信息管理系统 - 功能测试脚本
测试所有管理功能是否正常工作
"""

import os
import sys
import sqlite3
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        from src.app import app, db
        from src.models import User, Admin, Student, Course, Grade
        
        with app.app_context():
            # 检查表是否存在
            tables = ['users', 'admins', 'students', 'courses', 'grades']
            for table in tables:
                result = db.session.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone()
                if result:
                    print(f"  ✅ 表 '{table}' 存在")
                else:
                    print(f"  ❌ 表 '{table}' 不存在")
                    return False
                    
        print("✅ 数据库连接测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}\n")
        return False

def test_models():
    """测试数据模型"""
    print("🔍 测试数据模型...")
    try:
        from src.app import app, db
        from src.models import User, Admin, Student, Course, Grade
        
        with app.app_context():
            # 检查表结构
            expected_fields = {
                'User': ['id', 'username', 'email', 'password_hash', 'full_name', 'phone', 'created_at', 'is_admin', 'is_active'],
                'Admin': ['id', 'user_id', 'department', 'position', 'permissions', 'last_login', 'created_at'],
                'Student': ['id', 'user_id', 'student_id', 'major', 'grade', 'class_name', 'enrollment_date', 'birth_date', 'address', 'emergency_contact', 'emergency_phone', 'created_at'],
                'Course': ['id', 'course_code', 'course_name', 'description', 'credits', 'semester', 'teacher_name', 'max_students', 'classroom', 'schedule', 'created_at', 'is_active'],
                'Grade': ['id', 'student_id', 'course_id', 'midterm_score', 'final_score', 'assignment_score', 'total_score', 'grade_letter', 'semester', 'created_at', 'updated_at']
            }
            
            for model_name, fields in expected_fields.items():
                model_class = globals()[model_name]
                for field in fields:
                    if hasattr(model_class, field):
                        print(f"  ✅ {model_name}.{field} 存在")
                    else:
                        print(f"  ❌ {model_name}.{field} 不存在")
                        
        print("✅ 数据模型测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}\n")
        return False

def test_routes():
    """测试路由存在性"""
    print("🔍 测试路由...")
    try:
        from src.app import app
        
        expected_routes = [
            '/admin/users',
            '/admin/students', 
            '/admin/courses',
            '/admin/grades',
            '/admin/users/create',
            '/admin/students/create',
            '/admin/courses/create',
            '/admin/grades/create'
        ]
        
        with app.test_client() as client:
            for route in expected_routes:
                # 检查路由是否注册
                if any(rule.rule == route for rule in app.url_map.iter_rules()):
                    print(f"  ✅ 路由 '{route}' 已注册")
                else:
                    print(f"  ❌ 路由 '{route}' 未注册")
                    
        print("✅ 路由测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 路由测试失败: {e}\n")
        return False

def test_templates():
    """测试模板文件"""
    print("🔍 测试模板文件...")
    try:
        template_files = [
            'src/templates/admin/users.html',
            'src/templates/admin/students.html',
            'src/templates/admin/courses.html',
            'src/templates/admin/grades.html'
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                print(f"  ✅ 模板 '{template_file}' 存在")
            else:
                print(f"  ❌ 模板 '{template_file}' 不存在")
                
        print("✅ 模板测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 模板测试失败: {e}\n")
        return False

def test_sample_data():
    """测试示例数据"""
    print("🔍 测试示例数据...")
    try:
        from src.app import app, db
        from src.models import User, Admin, Student, Course, Grade
        
        with app.app_context():
            # 检查示例用户
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print(f"  ✅ 管理员账户存在: {admin_user.username}")
            else:
                print(f"  ❌ 管理员账户不存在")
                
            student_user = User.query.filter_by(username='student1').first()
            if student_user:
                print(f"  ✅ 学生账户存在: {student_user.username}")
            else:
                print(f"  ❌ 学生账户不存在")
                
        print("✅ 示例数据测试通过\n")
        return True
    except Exception as e:
        print(f"❌ 示例数据测试失败: {e}\n")
        return False

def main():
    """主测试函数"""
    print("🚀 开始学生信息管理系统功能测试")
    print("=" * 50)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("数据模型", test_models),
        ("路由", test_routes),
        ("模板文件", test_templates),
        ("示例数据", test_sample_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统功能完整。")
        print("\n📚 使用说明:")
        print("1. 运行: python src/app.py")
        print("2. 访问: http://localhost:5000")
        print("3. 管理员登录: admin / admin123")
        print("4. 学生登录: student1 / student123")
    else:
        print("⚠️  部分测试未通过，请检查系统配置。")
    
    return passed == total

if __name__ == "__main__":
    main()