#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AppenderQuery错误修复验证脚本
"""

import os
import sys
import sqlite3

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_appendix_query_fix():
    """测试AppenderQuery错误修复"""
    print("🔍 AppenderQuery错误修复验证")
    print("=" * 40)
    
    # 1. 检查修复的文件
    print("\n1. 检查修复的文件...")
    
    # 检查app.py中的修复
    try:
        with open('src/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'grades = Grade.query.filter_by(student_id=student_profile.id).all()' in content:
                print("  ✅ 后端查询修复：grades列表获取")
            else:
                print("  ❌ 后端查询修复：未找到grades列表获取")
            
            if 'grades=grades' in content:
                print("  ✅ 后端传递修复：传递grades变量给模板")
            else:
                print("  ❌ 后端传递修复：未找到grades变量传递")
    except Exception as e:
        print(f"  ❌ 检查app.py失败: {e}")
    
    # 检查模板中的修复
    try:
        with open('src/templates/student/profile.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'student_profile.grades' not in content:
                print("  ✅ 模板修复：移除了student_profile.grades使用")
            else:
                print("  ❌ 模板修复：仍存在student_profile.grades使用")
            
            if 'grades|length' in content:
                print("  ✅ 模板修复：使用grades|length过滤器")
            else:
                print("  ❌ 模板修复：未找到grades|length过滤器")
    except Exception as e:
        print(f"  ❌ 检查profile.html失败: {e}")
    
    # 2. 检查数据库
    print("\n2. 检查数据库状态...")
    try:
        db_path = 'database/student_management.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查学生数据
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
            student_count = cursor.fetchone()[0]
            print(f"  📊 学生用户数: {student_count}")
            
            # 检查成绩数据
            cursor.execute("SELECT COUNT(*) FROM grades")
            grade_count = cursor.fetchone()[0]
            print(f"  📊 成绩记录数: {grade_count}")
            
            conn.close()
            
            if student_count > 0 and grade_count > 0:
                print("  ✅ 数据库状态：测试数据完整")
            else:
                print("  ⚠️  数据库状态：测试数据不足")
        else:
            print("  ❌ 数据库文件不存在")
    except Exception as e:
        print(f"  ❌ 数据库检查失败: {e}")
    
    # 3. 功能测试说明
    print("\n3. 手动测试说明...")
    print("  📋 测试步骤:")
    print("     1. 启动系统: python src/app.py")
    print("     2. 访问: http://localhost:5000")
    print("     3. 登录学生: student1 / student123")
    print("     4. 点击用户名 → 个人资料")
    print("     5. 验证页面正常显示，无TypeError错误")
    
    # 4. 修复验证结果
    print("\n4. 修复验证结果...")
    print("  ✅ 错误类型: TypeError - AppenderQuery对象没有len()")
    print("  ✅ 修复方法: 后端执行查询 + 模板使用实际数据")
    print("  ✅ 修复位置: student_profile路由和profile.html模板")
    print("  ✅ 验证状态: 代码修复完成，等待功能测试")
    
    return True

def main():
    """主函数"""
    print("🐛 AppenderQuery错误修复验证")
    print("=" * 50)
    
    test_appendix_query_fix()
    
    print("\n" + "=" * 50)
    print("📋 修复总结:")
    print("• 问题：AppenderQuery对象无法使用length过滤器")
    print("• 原因：模板中直接使用SQLAlchemy Query对象")
    print("• 解决：在后端执行查询，传递实际数据列表")
    print("• 状态：代码修复完成，功能测试待验证")
    
    print("\n🎯 下一步:")
    print("1. 启动系统测试功能")
    print("2. 验证学生个人资料页面正常显示")
    print("3. 确认所有数据统计功能正常")

if __name__ == "__main__":
    main()