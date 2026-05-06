from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.exceptions import abort
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模型
from models import db, User, Admin, Student, Course, Grade

# 导入数据库初始化函数
from init_db import init_database

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_management.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    
    # 登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 路由定义
    @app.route('/')
    def index():
        """首页"""
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """用户登录"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('登录成功！', 'success')
                
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('student_dashboard'))
            else:
                flash('用户名或密码错误！', 'error')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """用户注册"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name')
            phone = request.form.get('phone')
            
            # 检查用户名和邮箱是否已存在
            if User.query.filter_by(username=username).first():
                flash('用户名已存在！', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('邮箱已被注册！', 'error')
                return render_template('register.html')
            
            # 创建新用户
            user = User(username=username, email=email, full_name=full_name, phone=phone)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                flash('注册成功！请登录。', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('注册失败，请重试。', 'error')
        
        return render_template('register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """用户登出"""
        logout_user()
        flash('已成功登出！', 'info')
        return redirect(url_for('index'))
    
    # 管理员路由
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        """管理员仪表板"""
        if not current_user.is_admin:
            abort(403)
        
        # 统计数据
        total_users = User.query.count()
        total_students = Student.query.count()
        total_courses = Course.query.count()
        total_grades = Grade.query.count()
        
        recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
        recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html', 
                             total_users=total_users,
                             total_students=total_students,
                             total_courses=total_courses,
                             total_grades=total_grades,
                             recent_students=recent_students,
                             recent_courses=recent_courses)
    
    @app.route('/admin/users')
    @login_required
    def admin_users():
        """用户管理"""
        if not current_user.is_admin:
            abort(403)
        
        users = User.query.all()
        return render_template('admin/users.html', users=users)
    
    @app.route('/admin/users/create', methods=['POST'])
    @login_required
    def admin_users_create():
        """创建用户"""
        if not current_user.is_admin:
            abort(403)
        
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == '1'
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在！', 'error')
            return redirect(url_for('admin_users'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册！', 'error')
            return redirect(url_for('admin_users'))
        
        # 创建新用户
        user = User(username=username, email=email, full_name=full_name, 
                   phone=phone, is_admin=is_admin)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('用户创建成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/<int:user_id>/edit')
    @login_required
    def admin_users_edit(user_id):
        """获取用户编辑数据"""
        if not current_user.is_admin:
            abort(403)
        
        user = User.query.get_or_404(user_id)
        return jsonify({
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'is_admin': user.is_admin
        })
    
    @app.route('/admin/users/<int:user_id>/update', methods=['POST'])
    @login_required
    def admin_users_update(user_id):
        """更新用户"""
        if not current_user.is_admin:
            abort(403)
        
        user = User.query.get_or_404(user_id)
        
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        is_admin = request.form.get('is_admin') == '1'
        
        # 检查用户名和邮箱是否已被其他用户使用
        if User.query.filter(User.id != user.id, User.username == username).first():
            flash('用户名已被使用！', 'error')
            return redirect(url_for('admin_users'))
        
        if User.query.filter(User.id != user.id, User.email == email).first():
            flash('邮箱已被使用！', 'error')
            return redirect(url_for('admin_users'))
        
        try:
            user.username = username
            user.email = email
            user.full_name = full_name
            user.phone = phone
            user.is_admin = is_admin
            
            db.session.commit()
            flash('用户更新成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
    @login_required
    def admin_users_toggle(user_id):
        """切换用户状态"""
        if not current_user.is_admin:
            abort(403)
        
        user = User.query.get_or_404(user_id)
        
        # 不能禁用自己
        if user.id == current_user.id:
            flash('不能禁用自己！', 'error')
            return redirect(url_for('admin_users'))
        
        try:
            user.is_active = not user.is_active
            db.session.commit()
            status = '启用' if user.is_active else '禁用'
            flash(f'用户{status}成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'操作失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_users'))
    
    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @login_required
    def admin_users_delete(user_id):
        """删除用户"""
        if not current_user.is_admin:
            abort(403)
        
        user = User.query.get_or_404(user_id)
        
        # 不能删除自己
        if user.id == current_user.id:
            flash('不能删除自己！', 'error')
            return redirect(url_for('admin_users'))
        
        try:
            db.session.delete(user)
            db.session.commit()
            flash('用户删除成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'删除失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_users'))
    
    # ==================== 学生管理路由 ====================
    @app.route('/admin/students')
    @login_required
    def admin_students():
        """学生管理"""
        if not current_user.is_admin:
            abort(403)
        
        students = Student.query.all()
        users = User.query.filter_by(is_admin=False).all()
        return render_template('admin/students.html', students=students, users=users)
    
    @app.route('/admin/students/create', methods=['POST'])
    @login_required
    def admin_students_create():
        """创建学生"""
        if not current_user.is_admin:
            abort(403)
        
        try:
            user_id = request.form.get('user_id')
            student_id = request.form.get('student_id')
            major = request.form.get('major')
            grade = request.form.get('grade')
            class_name = request.form.get('class_name')
            enrollment_date = datetime.strptime(request.form.get('enrollment_date'), '%Y-%m-%d')
            birth_date = request.form.get('birth_date')
            if birth_date:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            
            address = request.form.get('address')
            emergency_contact = request.form.get('emergency_contact')
            emergency_phone = request.form.get('emergency_phone')
            
            # 检查学号是否已存在
            if Student.query.filter_by(student_id=student_id).first():
                flash('学号已存在！', 'error')
                return redirect(url_for('admin_students'))
            
            # 创建学生记录
            student = Student(
                user_id=user_id,
                student_id=student_id,
                major=major,
                grade=grade,
                class_name=class_name,
                enrollment_date=enrollment_date,
                birth_date=birth_date,
                address=address,
                emergency_contact=emergency_contact,
                emergency_phone=emergency_phone
            )
            
            db.session.add(student)
            db.session.commit()
            flash('学生创建成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_students'))
    
    @app.route('/admin/students/<int:student_id>/edit')
    @login_required
    def admin_students_edit(student_id):
        """获取学生编辑数据"""
        if not current_user.is_admin:
            abort(403)
        
        student = Student.query.get_or_404(student_id)
        return jsonify({
            'html': f'''
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_student_id" class="form-label">学号 *</label>
                        <input type="text" class="form-control" id="edit_student_id" name="student_id" value="{student.student_id}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_major" class="form-label">专业 *</label>
                        <input type="text" class="form-control" id="edit_major" name="major" value="{student.major}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_grade" class="form-label">年级 *</label>
                        <select class="form-control" id="edit_grade" name="grade" required>
                            <option value="大一" {"selected" if student.grade == "大一" else ""}>大一</option>
                            <option value="大二" {"selected" if student.grade == "大二" else ""}>大二</option>
                            <option value="大三" {"selected" if student.grade == "大三" else ""}>大三</option>
                            <option value="大四" {"selected" if student.grade == "大四" else ""}>大四</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="edit_class_name" class="form-label">班级</label>
                        <input type="text" class="form-control" id="edit_class_name" name="class_name" value="{student.class_name or ''}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_enrollment_date" class="form-label">入学时间 *</label>
                        <input type="date" class="form-control" id="edit_enrollment_date" name="enrollment_date" value="{student.enrollment_date.strftime('%Y-%m-%d')}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_birth_date" class="form-label">出生日期</label>
                        <input type="date" class="form-control" id="edit_birth_date" name="birth_date" value="{student.birth_date.strftime('%Y-%m-%d') if student.birth_date else ''}">
                    </div>
                    <div class="mb-3">
                        <label for="edit_address" class="form-label">地址</label>
                        <textarea class="form-control" id="edit_address" name="address" rows="2">{student.address or ''}</textarea>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_emergency_contact" class="form-label">紧急联系人</label>
                        <input type="text" class="form-control" id="edit_emergency_contact" name="emergency_contact" value="{student.emergency_contact or ''}">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_emergency_phone" class="form-label">紧急联系电话</label>
                        <input type="text" class="form-control" id="edit_emergency_phone" name="emergency_phone" value="{student.emergency_phone or ''}">
                    </div>
                </div>
            </div>
            '''
        })
    
    @app.route('/admin/students/<int:student_id>/update', methods=['POST'])
    @login_required
    def admin_students_update(student_id):
        """更新学生"""
        if not current_user.is_admin:
            abort(403)
        
        student = Student.query.get_or_404(student_id)
        
        try:
            student_id_new = request.form.get('student_id')
            major = request.form.get('major')
            grade = request.form.get('grade')
            class_name = request.form.get('class_name')
            enrollment_date = datetime.strptime(request.form.get('enrollment_date'), '%Y-%m-%d')
            birth_date = request.form.get('birth_date')
            if birth_date:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            else:
                birth_date = None
            
            address = request.form.get('address')
            emergency_contact = request.form.get('emergency_contact')
            emergency_phone = request.form.get('emergency_phone')
            
            # 检查学号是否已被其他学生使用
            if Student.query.filter(Student.id != student.id, Student.student_id == student_id_new).first():
                flash('学号已被使用！', 'error')
                return redirect(url_for('admin_students'))
            
            student.student_id = student_id_new
            student.major = major
            student.grade = grade
            student.class_name = class_name
            student.enrollment_date = enrollment_date
            student.birth_date = birth_date
            student.address = address
            student.emergency_contact = emergency_contact
            student.emergency_phone = emergency_phone
            
            db.session.commit()
            flash('学生信息更新成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_students'))
    
    @app.route('/admin/students/<int:student_id>/details')
    @login_required
    def admin_students_details(student_id):
        """获取学生详情"""
        if not current_user.is_admin:
            abort(403)
        
        student = Student.query.get_or_404(student_id)
        return jsonify({
            'html': f'''
            <div class="row">
                <div class="col-md-6">
                    <p><strong>学号：</strong>{student.student_id}</p>
                    <p><strong>姓名：</strong>{student.user.full_name}</p>
                    <p><strong>专业：</strong>{student.major}</p>
                    <p><strong>年级：</strong>{student.grade}</p>
                    <p><strong>班级：</strong>{student.class_name or '-'}</p>
                    <p><strong>入学时间：</strong>{student.enrollment_date.strftime('%Y-%m-%d')}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>出生日期：</strong>{student.birth_date.strftime('%Y-%m-%d') if student.birth_date else '-'}</p>
                    <p><strong>电话：</strong>{student.user.phone or '-'}</p>
                    <p><strong>邮箱：</strong>{student.user.email}</p>
                    <p><strong>地址：</strong>{student.address or '-'}</p>
                    <p><strong>紧急联系人：</strong>{student.emergency_contact or '-'}</p>
                    <p><strong>紧急联系电话：</strong>{student.emergency_phone or '-'}</p>
                </div>
            </div>
            '''
        })
    
    @app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
    @login_required
    def admin_students_delete(student_id):
        """删除学生"""
        if not current_user.is_admin:
            abort(403)
        
        student = Student.query.get_or_404(student_id)
        
        try:
            db.session.delete(student)
            db.session.commit()
            flash('学生删除成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'删除失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_students'))
    
    # ==================== 课程管理路由 ====================
    @app.route('/admin/courses')
    @login_required
    def admin_courses():
        """课程管理"""
        if not current_user.is_admin:
            abort(403)
        
        courses = Course.query.all()
        return render_template('admin/courses.html', courses=courses)
    
    @app.route('/admin/courses/create', methods=['POST'])
    @login_required
    def admin_courses_create():
        """创建课程"""
        if not current_user.is_admin:
            abort(403)
        
        try:
            course_code = request.form.get('course_code')
            course_name = request.form.get('course_name')
            description = request.form.get('description')
            credits = int(request.form.get('credits', 1))
            semester = request.form.get('semester')
            teacher_name = request.form.get('teacher_name')
            max_students = int(request.form.get('max_students', 50))
            classroom = request.form.get('classroom')
            schedule = request.form.get('schedule')
            
            # 检查课程代码是否已存在
            if Course.query.filter_by(course_code=course_code).first():
                flash('课程代码已存在！', 'error')
                return redirect(url_for('admin_courses'))
            
            # 创建课程记录
            course = Course(
                course_code=course_code,
                course_name=course_name,
                description=description,
                credits=credits,
                semester=semester,
                teacher_name=teacher_name,
                max_students=max_students,
                classroom=classroom,
                schedule=schedule
            )
            
            db.session.add(course)
            db.session.commit()
            flash('课程创建成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_courses'))
    
    @app.route('/admin/courses/<int:course_id>/edit')
    @login_required
    def admin_courses_edit(course_id):
        """获取课程编辑数据"""
        if not current_user.is_admin:
            abort(403)
        
        course = Course.query.get_or_404(course_id)
        return jsonify({
            'html': f'''
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_course_code" class="form-label">课程代码 *</label>
                        <input type="text" class="form-control" id="edit_course_code" name="course_code" value="{course.course_code}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_course_name" class="form-label">课程名称 *</label>
                        <input type="text" class="form-control" id="edit_course_name" name="course_name" value="{course.course_name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_description" class="form-label">课程描述</label>
                        <textarea class="form-control" id="edit_description" name="description" rows="3">{course.description or ''}</textarea>
                    </div>
                    <div class="mb-3">
                        <label for="edit_credits" class="form-label">学分 *</label>
                        <input type="number" class="form-control" id="edit_credits" name="credits" min="1" max="10" value="{course.credits}" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_semester" class="form-label">学期 *</label>
                        <select class="form-control" id="edit_semester" name="semester" required>
                            <option value="2024春季" {"selected" if course.semester == "2024春季" else ""}>2024春季</option>
                            <option value="2024秋季" {"selected" if course.semester == "2024秋季" else ""}>2024秋季</option>
                            <option value="2025春季" {"selected" if course.semester == "2025春季" else ""}>2025春季</option>
                            <option value="2025秋季" {"selected" if course.semester == "2025秋季" else ""}>2025秋季</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="edit_teacher_name" class="form-label">教师姓名 *</label>
                        <input type="text" class="form-control" id="edit_teacher_name" name="teacher_name" value="{course.teacher_name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_max_students" class="form-label">最大人数 *</label>
                        <input type="number" class="form-control" id="edit_max_students" name="max_students" min="1" value="{course.max_students}" required>
                    </div>
                    <div class="mb-3">
                        <label for="edit_classroom" class="form-label">教室</label>
                        <input type="text" class="form-control" id="edit_classroom" name="classroom" value="{course.classroom or ''}">
                    </div>
                </div>
            </div>
            <div class="mb-3">
                <label for="edit_schedule" class="form-label">上课时间</label>
                <input type="text" class="form-control" id="edit_schedule" name="schedule" value="{course.schedule or ''}" placeholder="例：周一 9:00-10:40">
            </div>
            '''
        })
    
    @app.route('/admin/courses/<int:course_id>/update', methods=['POST'])
    @login_required
    def admin_courses_update(course_id):
        """更新课程"""
        if not current_user.is_admin:
            abort(403)
        
        course = Course.query.get_or_404(course_id)
        
        try:
            course_code = request.form.get('course_code')
            course_name = request.form.get('course_name')
            description = request.form.get('description')
            credits = int(request.form.get('credits', 1))
            semester = request.form.get('semester')
            teacher_name = request.form.get('teacher_name')
            max_students = int(request.form.get('max_students', 50))
            classroom = request.form.get('classroom')
            schedule = request.form.get('schedule')
            
            # 检查课程代码是否已被其他课程使用
            if Course.query.filter(Course.id != course.id, Course.course_code == course_code).first():
                flash('课程代码已被使用！', 'error')
                return redirect(url_for('admin_courses'))
            
            course.course_code = course_code
            course.course_name = course_name
            course.description = description
            course.credits = credits
            course.semester = semester
            course.teacher_name = teacher_name
            course.max_students = max_students
            course.classroom = classroom
            course.schedule = schedule
            
            db.session.commit()
            flash('课程更新成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_courses'))
    
    @app.route('/admin/courses/<int:course_id>/toggle', methods=['POST'])
    @login_required
    def admin_courses_toggle(course_id):
        """切换课程状态"""
        if not current_user.is_admin:
            abort(403)
        
        course = Course.query.get_or_404(course_id)
        
        try:
            course.is_active = not course.is_active
            db.session.commit()
            status = '启用' if course.is_active else '停用'
            flash(f'课程{status}成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'操作失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_courses'))
    
    @app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
    @login_required
    def admin_courses_delete(course_id):
        """删除课程"""
        if not current_user.is_admin:
            abort(403)
        
        course = Course.query.get_or_404(course_id)
        
        try:
            db.session.delete(course)
            db.session.commit()
            flash('课程删除成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'删除失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_courses'))
    
    # ==================== 成绩管理路由 ====================
    @app.route('/admin/grades')
    @login_required
    def admin_grades():
        """成绩管理"""
        if not current_user.is_admin:
            abort(403)
        
        grades = Grade.query.all()
        students = Student.query.all()
        courses = Course.query.all()
        return render_template('admin/grades.html', grades=grades, students=students, courses=courses)
    
    @app.route('/admin/grades/create', methods=['POST'])
    @login_required
    def admin_grades_create():
        """创建成绩"""
        if not current_user.is_admin:
            abort(403)
        
        try:
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            semester = request.form.get('semester')
            midterm_score = request.form.get('midterm_score')
            final_score = request.form.get('final_score')
            assignment_score = request.form.get('assignment_score')
            
            # 转换为float类型
            midterm_score = float(midterm_score) if midterm_score else None
            final_score = float(final_score) if final_score else None
            assignment_score = float(assignment_score) if assignment_score else None
            
            # 检查是否已存在相同的学生和课程记录
            existing_grade = Grade.query.filter_by(
                student_id=student_id, 
                course_id=course_id, 
                semester=semester
            ).first()
            
            if existing_grade:
                flash('该学生的该课程成绩已存在！', 'error')
                return redirect(url_for('admin_grades'))
            
            # 创建成绩记录
            grade = Grade(
                student_id=student_id,
                course_id=course_id,
                semester=semester,
                midterm_score=midterm_score,
                final_score=final_score,
                assignment_score=assignment_score
            )
            
            # 计算总成绩
            if midterm_score and final_score and assignment_score:
                grade.calculate_total_score()
            
            db.session.add(grade)
            db.session.commit()
            flash('成绩创建成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_grades'))
    
    @app.route('/admin/grades/<int:grade_id>/edit')
    @login_required
    def admin_grades_edit(grade_id):
        """获取成绩编辑数据"""
        if not current_user.is_admin:
            abort(403)
        
        grade = Grade.query.get_or_404(grade_id)
        return jsonify({
            'html': f'''
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_student_id" class="form-label">学生 *</label>
                        <select class="form-control" id="edit_student_id" name="student_id" required>
                            <option value="">选择学生...</option>
                            {''.join([f'<option value="{s.id}" {"selected" if s.id == grade.student_id else ""}>{s.user.full_name} ({s.student_id})</option>' for s in Student.query.all()])}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="edit_course_id" class="form-label">课程 *</label>
                        <select class="form-control" id="edit_course_id" name="course_id" required>
                            <option value="">选择课程...</option>
                            {''.join([f'<option value="{c.id}" {"selected" if c.id == grade.course_id else ""}>{c.course_name}</option>' for c in Course.query.all()])}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="edit_semester" class="form-label">学期 *</label>
                        <select class="form-control" id="edit_semester" name="semester" required>
                            <option value="2024春季" {"selected" if grade.semester == "2024春季" else ""}>2024春季</option>
                            <option value="2024秋季" {"selected" if grade.semester == "2024秋季" else ""}>2024秋季</option>
                            <option value="2025春季" {"selected" if grade.semester == "2025春季" else ""}>2025春季</option>
                            <option value="2025秋季" {"selected" if grade.semester == "2025秋季" else ""}>2025秋季</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="edit_midterm_score" class="form-label">期中成绩</label>
                        <input type="number" class="form-control" id="edit_midterm_score" name="midterm_score" 
                               min="0" max="100" step="0.01" value="{grade.midterm_score or ''}">
                    </div>
                    <div class="mb-3">
                        <label for="edit_final_score" class="form-label">期末成绩</label>
                        <input type="number" class="form-control" id="edit_final_score" name="final_score" 
                               min="0" max="100" step="0.01" value="{grade.final_score or ''}">
                    </div>
                    <div class="mb-3">
                        <label for="edit_assignment_score" class="form-label">作业成绩</label>
                        <input type="number" class="form-control" id="edit_assignment_score" name="assignment_score" 
                               min="0" max="100" step="0.01" value="{grade.assignment_score or ''}">
                    </div>
                </div>
            </div>
            <div class="alert alert-info">
                <small>
                    <strong>当前成绩：</strong><br>
                    总成绩：{grade.total_score:.2f if grade.total_score else '-'}<br>
                    等级：{grade.grade_letter or '-'}
                </small>
            </div>
            '''
        })
    
    @app.route('/admin/grades/<int:grade_id>/update', methods=['POST'])
    @login_required
    def admin_grades_update(grade_id):
        """更新成绩"""
        if not current_user.is_admin:
            abort(403)
        
        grade = Grade.query.get_or_404(grade_id)
        
        try:
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            semester = request.form.get('semester')
            midterm_score = request.form.get('midterm_score')
            final_score = request.form.get('final_score')
            assignment_score = request.form.get('assignment_score')
            
            # 转换为float类型
            midterm_score = float(midterm_score) if midterm_score else None
            final_score = float(final_score) if final_score else None
            assignment_score = float(assignment_score) if assignment_score else None
            
            # 检查是否已存在相同的学生和课程记录（排除当前记录）
            existing_grade = Grade.query.filter(
                Grade.id != grade.id,
                Grade.student_id == student_id, 
                Grade.course_id == course_id, 
                Grade.semester == semester
            ).first()
            
            if existing_grade:
                flash('该学生的该课程成绩已存在！', 'error')
                return redirect(url_for('admin_grades'))
            
            grade.student_id = student_id
            grade.course_id = course_id
            grade.semester = semester
            grade.midterm_score = midterm_score
            grade.final_score = final_score
            grade.assignment_score = assignment_score
            
            # 重新计算总成绩
            if midterm_score and final_score and assignment_score:
                grade.calculate_total_score()
            else:
                grade.total_score = None
                grade.grade_letter = None
            
            db.session.commit()
            flash('成绩更新成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_grades'))
    
    @app.route('/admin/grades/<int:grade_id>/recalculate', methods=['POST'])
    @login_required
    def admin_grades_recalculate(grade_id):
        """重新计算成绩"""
        if not current_user.is_admin:
            abort(403)
        
        grade = Grade.query.get_or_404(grade_id)
        
        try:
            if grade.midterm_score and grade.final_score and grade.assignment_score:
                grade.calculate_total_score()
                db.session.commit()
                return jsonify({'success': True, 'message': '成绩重新计算完成'})
            else:
                return jsonify({'success': False, 'error': '缺少必要的成绩数据'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/admin/grades/<int:grade_id>/delete', methods=['POST'])
    @login_required
    def admin_grades_delete(grade_id):
        """删除成绩"""
        if not current_user.is_admin:
            abort(403)
        
        grade = Grade.query.get_or_404(grade_id)
        
        try:
            db.session.delete(grade)
            db.session.commit()
            flash('成绩删除成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'删除失败：{str(e)}', 'error')
        
        return redirect(url_for('admin_grades'))
    
    # 学生路由
    @app.route('/student/dashboard')
    @login_required
    def student_dashboard():
        """学生仪表板"""
        if current_user.is_admin:
            abort(403)
        
        student_profile = current_user.student_profile
        if not student_profile:
            flash('学生档案不存在！', 'error')
            return redirect(url_for('index'))
        
        # 获取学生成绩
        grades = Grade.query.filter_by(student_id=student_profile.id).all()
        
        # 计算GPA
        total_credits = 0
        weighted_score = 0
        
        for grade in grades:
            if grade.total_score and grade.course.credits:
                total_credits += grade.course.credits
                weighted_score += grade.total_score * grade.course.credits
        
        gpa = weighted_score / total_credits if total_credits > 0 else 0
        
        return render_template('student/dashboard.html', 
                             student_profile=student_profile,
                             grades=grades,
                             gpa=gpa)
    
    # ==================== 学生个人资料管理路由 ====================
    @app.route('/student/profile')
    @login_required
    def student_profile():
        """学生个人资料页面"""
        if current_user.is_admin:
            abort(403)
        
        student_profile = current_user.student_profile
        if not student_profile:
            flash('学生档案不存在！', 'error')
            return redirect(url_for('index'))
        
        # 获取学生的成绩记录
        grades = Grade.query.filter_by(student_id=student_profile.id).all()
        
        return render_template('student/profile.html', 
                             student_profile=student_profile,
                             grades=grades)
    
    @app.route('/student/edit', methods=['GET', 'POST'])
    @login_required
    def student_edit():
        """编辑学生个人信息"""
        if current_user.is_admin:
            abort(403)
        
        student_profile = current_user.student_profile
        if not student_profile:
            flash('学生档案不存在！', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            try:
                # 更新用户信息
                full_name = request.form.get('full_name')
                phone = request.form.get('phone')
                address = request.form.get('address')
                emergency_contact = request.form.get('emergency_contact')
                emergency_phone = request.form.get('emergency_phone')
                
                # 更新用户表
                current_user.full_name = full_name
                current_user.phone = phone
                
                # 更新学生档案
                student_profile.address = address
                student_profile.emergency_contact = emergency_contact
                student_profile.emergency_phone = emergency_phone
                
                db.session.commit()
                flash('个人信息更新成功！', 'success')
                return redirect(url_for('student_profile'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'更新失败：{str(e)}', 'error')
        
        return render_template('student/edit_profile.html', 
                             student_profile=student_profile)
    
    @app.route('/student/change-password', methods=['GET', 'POST'])
    @login_required
    def student_change_password():
        """学生修改密码"""
        if current_user.is_admin:
            abort(403)
        
        if request.method == 'POST':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # 验证当前密码
            if not current_user.check_password(current_password):
                flash('当前密码错误！', 'error')
                return render_template('student/change_password.html')
            
            # 验证新密码
            if new_password != confirm_password:
                flash('新密码和确认密码不一致！', 'error')
                return render_template('student/change_password.html')
            
            if len(new_password) < 6:
                flash('密码长度至少6位！', 'error')
                return render_template('student/change_password.html')
            
            try:
                # 更新密码
                current_user.set_password(new_password)
                db.session.commit()
                flash('密码修改成功！', 'success')
                return redirect(url_for('student_profile'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'密码修改失败：{str(e)}', 'error')
        
        return render_template('student/change_password.html')
    
    @app.route('/student/courses')
    @login_required
    def student_courses():
        """学生课程列表"""
        if current_user.is_admin:
            abort(403)
        
        student_profile = current_user.student_profile
        if not student_profile:
            flash('学生档案不存在！', 'error')
            return redirect(url_for('index'))
        
        # 获取学生的所有课程
        grades = Grade.query.filter_by(student_id=student_profile.id).all()
        courses = [grade.course for grade in grades]
        
        return render_template('student/courses.html', 
                             courses=courses,
                             student_profile=student_profile)
    
    @app.route('/student/grades')
    @login_required
    def student_grades():
        """学生成绩查看"""
        if current_user.is_admin:
            abort(403)
        
        student_profile = current_user.student_profile
        if not student_profile:
            flash('学生档案不存在！', 'error')
            return redirect(url_for('index'))
        
        # 获取学生的所有成绩
        grades = Grade.query.filter_by(student_id=student_profile.id).all()
        
        return render_template('student/grades.html', 
                             grades=grades,
                             student_profile=student_profile)
    
    # API接口
    @app.route('/api/stats')
    @login_required
    def api_stats():
        """获取统计数据的API"""
        if not current_user.is_admin:
            return jsonify({'error': '权限不足'}), 403
        
        stats = {
            'users': User.query.count(),
            'students': Student.query.count(),
            'courses': Course.query.count(),
            'grades': Grade.query.count()
        }
        return jsonify(stats)
    
    # 错误处理
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员（如果不存在）
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', 
                            full_name='系统管理员', is_admin=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("创建默认管理员账户: admin / admin123")
        
        # 创建示例学生
        student_user = User.query.filter_by(username='student1').first()
        if not student_user:
            student_user = User(username='student1', email='student1@example.com',
                              full_name='张三', phone='13800138001')
            student_user.set_password('student123')
            db.session.add(student_user)
            db.session.commit()
            
            # 创建学生档案
            student = Student(user_id=student_user.id, student_id='2021001',
                            major='计算机科学与技术', grade='2021级', class_name='计科1班',
                            enrollment_date=datetime.strptime('2021-09-01', '%Y-%m-%d'),
                            birth_date=datetime.strptime('2003-05-15', '%Y-%m-%d'))
            db.session.add(student)
            db.session.commit()
            print("创建示例学生账户: student1 / student123")

if __name__ == '__main__':
    # 创建数据库和示例数据
    with app.app_context():
        db.create_all()
        init_database()
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
