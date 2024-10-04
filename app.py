import os
import schedule
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import jdatetime

# ایجاد پوشه templates اگر وجود ندارد
if not os.path.exists('templates'):
    os.makedirs('templates')

# ایجاد فایل register_phone.html
with open('templates/register_phone.html', 'w', encoding='utf-8') as f:
    f.write(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت‌نام کاربر</title>
</head>
<body>
    <h1>ثبت‌نام کاربر</h1>
    <form method="post">
        <label for="name">نام:</label><br>
        <input type="text" id="name" name="name" required><br><br>
        <label for="gender">جنسیت:</label><br>
        <select id="gender" name="gender" required>
            <option value="male">مرد</option>
            <option value="female">زن</option>
        </select><br><br>
        <label for="height">قد (سانتی‌متر):</label><br>
        <input type="text" id="height" name="height" required><br><br>
        <label for="weight">وزن (کیلوگرم):</label><br>
        <input type="text" id="weight" name="weight" required><br><br>
        <label for="phone_number">شماره تلفن:</label><br>
        <input type="text" id="phone_number" name="phone_number" required><br><br>
        <label for="message">پیام:</label><br>
        <input type="text" id="message" name="message" required><br><br>
        <button type="submit">ارسال</button>
    </form>
    <a href="/">بازگشت به صفحه اصلی</a>
</body>
</html>
''')

# ایجاد فایل set_report_time.html برای تنظیم زمان گزارش‌دهی
with open('templates/set_report_time.html', 'w', encoding='utf-8') as f:
    f.write(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تنظیم زمان گزارش‌دهی روزانه</title>
</head>
<body>
    <h1>تنظیم زمان گزارش‌دهی روزانه</h1>
    <form method="post">
        <label for="phone_number">شماره تلفن:</label><br>
        <input type="text" id="phone_number" name="phone_number" required><br><br>
        <label for="report_time">زمان گزارش‌دهی (ساعت):</label><br>
        <input type="text" id="report_time" name="report_time" required><br><br>
        <button type="submit">تنظیم زمان گزارش‌دهی</button>
    </form>
    <a href="/">بازگشت به صفحه اصلی</a>
</body>
</html>
''')

# ایجاد فایل send_weight.html برای دریافت وزن روزانه
with open('templates/send_weight.html', 'w', encoding='utf-8') as f:
    f.write(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ارسال وزن روزانه</title>
</head>
<body>
    <h1>ارسال وزن روزانه</h1>
    <form method="post">
        <label for="phone_number">شماره تلفن:</label><br>
        <input type="text" id="phone_number" name="phone_number" required><br><br>
        <label for="weight_value">وزن (کیلوگرم):</label><br>
        <input type="text" id="weight_value" name="weight_value" required><br><br>
        <button type="submit">ارسال وزن</button>
    </form>
    <a href="/">بازگشت به صفحه اصلی</a>
</body>
</html>
''')

# ایجاد فایل manage_users.html برای مدیریت کاربران
with open('templates/manage_users.html', 'w', encoding='utf-8') as f:
    f.write(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت کاربران</title>
    <script>
        function confirmDelete() {
            return confirm('آیا از حذف این کاربر مطمئن هستید؟');
        }
    </script>
</head>
<body>
    <h1>مدیریت کاربران</h1>
    <table border="1">
        <tr>
            <th>شناسه</th>
            <th>شماره تلفن</th>
            <th>زمان گزارش‌دهی</th>
            <th>BMI فعلی</th>
            <th>اولین وزن</th>
            <th>آخرین وزن</th>
            <th>میانگین وزن</th>
            <th>عملیات</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td><a href="/weight_report/{{ user.phone_number }}">{{ user.phone_number }}</a></td>
            <td>{{ user.report_time }}</td>
            <td>{{ user.current_bmi }}</td>
            <td>{{ user.first_weight }}</td>
            <td>{{ user.last_weight }}</td>
            <td>{{ user.avg_weight }}</td>
            <td>
                <a href="/delete_user/{{ user.id }}" onclick="return confirmDelete();">حذف</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    <a href="/">بازگشت به صفحه اصلی</a>
</body>
</html>
''')

# ایجاد فایل weight_report.html برای مشاهده گزارش وزن کاربران
with open('templates/weight_report.html', 'w', encoding='utf-8') as f:
    f.write(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گزارش وزن کاربر</title>
</head>
<body>
    <h1>گزارش وزن کاربر {{ phone_number }}</h1>
    <table border="1">
        <tr>
            <th>تاریخ</th>
            <th>روز هفته</th>
            <th>وزن (کیلوگرم)</th>
            <th>BMI</th>
            <th>تغییرات نسبت به روز گذشته (کیلوگرم)</th>
            <th>تغییرات نسبت به میانگین (کیلوگرم)</th>
            <th>ساعت ارسال</th>
        </tr>
        {% for weight in weights %}
        <tr>
            <td>{{ weight.date }}</td>
            <td>{{ weight.weekday }}</td>
            <td>{{ weight.weight_value }}</td>
            <td>{{ weight.bmi }}</td>
            <td>{{ weight.change_from_previous }}</td>
            <td>{{ weight.change_from_average }}</td>
            <td>{{ weight.time }}</td>
        </tr>
        {% endfor %}
    </table>
    <a href="/manage_users">بازگشت به مدیریت کاربران</a>
</body>
</html>
''')

# ایجاد فایل home.html برای صفحه اصلی
with open('templates/home.html', 'w', encoding='utf-8') as f:
    f.write(r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستم هوشمند کوچینگ وزن</title>
</head>
<body>
    <h1>به سیستم هوشمند کوچینگ وزن خوش آمدید!</h1>
    <a href="/register_phone">ثبت‌نام کاربر</a><br><br>
    <a href="/set_report_time">تنظیم زمان گزارش‌دهی روزانه</a><br><br>
    <a href="/send_weight">ارسال وزن روزانه</a><br><br>
    <a href="/manage_users">مدیریت کاربران</a>
</body>
</html>
''')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# تنظیم پایگاه داده SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coaching.db'  
db = SQLAlchemy(app)

# تعریف مدل User برای ذخیره اطلاعات کاربر
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    report_time = db.Column(db.String(5), nullable=True)

    def __repr__(self):
        return f'<User {self.phone_number}>'

    @property
    def current_bmi(self):
        last_weight_entry = Weight.query.filter_by(user_id=self.id).order_by(Weight.date.desc()).first()
        if last_weight_entry:
            height_m = self.height / 100
            return round(last_weight_entry.weight_value / (height_m ** 2), 2)
        return None

    @property
    def first_weight(self):
        first_weight_entry = Weight.query.filter_by(user_id=self.id).order_by(Weight.date.asc()).first()
        if first_weight_entry:
            return first_weight_entry.weight_value
        return None

    @property
    def last_weight(self):
        last_weight_entry = Weight.query.filter_by(user_id=self.id).order_by(Weight.date.desc()).first()
        if last_weight_entry:
            return last_weight_entry.weight_value
        return None

    @property
    def avg_weight(self):
        weights = Weight.query.filter_by(user_id=self.id).all()
        if weights:
            total_weight = sum([w.weight_value for w in weights])
            return round(total_weight / len(weights), 2)
        return None

# تعریف مدل Weight برای ذخیره وزن روزانه کاربران
class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight_value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f'<Weight {self.weight_value} for User {self.user_id} on {self.date} at {self.time}>'

    @property
    def bmi(self):
        user = User.query.get(self.user_id)
        if user:
            height_m = user.height / 100
            return round(self.weight_value / (height_m ** 2), 2)
        return None

    @property
    def change_from_previous(self):
        previous_weight_entry = Weight.query.filter(Weight.user_id == self.user_id, Weight.date < self.date).order_by(Weight.date.desc()).first()
        if previous_weight_entry:
            return round(self.weight_value - previous_weight_entry.weight_value, 2)
        return None

    @property
    def change_from_average(self):
        user = User.query.get(self.user_id)
        if user and user.avg_weight:
            return round(self.weight_value - user.avg_weight, 2)
        return None

# ایجاد جداول پایگاه داده
with app.app_context():
    db.create_all()

# مسیر صفحه اصلی
@app.route('/')
def home():
    return render_template('home.html')

# مسیر ثبت‌نام کاربر با ارسال عدد "100"
@app.route('/register_phone', methods=['GET', 'POST'])
def register_phone():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        height = float(request.form['height'])
        phone_number = request.form['phone_number']
        weight = float(request.form['weight'])
        message = request.form['message']

        if message == '100':  # کاربر باید عدد 100 را وارد کند تا ثبت‌نام شود
            existing_user = User.query.filter_by(phone_number=phone_number).first()
            if not existing_user:
                # محاسبه BMI
                height_m = height / 100
                bmi = weight / (height_m ** 2)
                bmi_status = ""
                if bmi < 18.5:
                    bmi_status = "کمبود وزن"
                elif 18.5 <= bmi < 24.9:
                    bmi_status = "وزن نرمال"
                elif 25 <= bmi < 29.9:
                    bmi_status = "اضافه وزن"
                else:
                    bmi_status = "چاقی"
                
                new_user = User(name=name, gender=gender, height=height, phone_number=phone_number)
                db.session.add(new_user)
                db.session.commit()
                # ذخیره وزن اولیه
                new_weight = Weight(user_id=new_user.id, weight_value=weight, date=date.today(), time=datetime.now().strftime('%H:%M'))
                db.session.add(new_weight)
                db.session.commit()
                return f"خوش آمدید {name}! شاخص توده بدنی (BMI) شما {bmi:.2f} است و شما در دسته‌بندی '{bmi_status}' قرار دارید. لطفاً زمان گزارش‌دهی روزانه خود را تعیین کنید.<br><a href='/'>بازگشت به صفحه اصلی</a>"

            return "این شماره تلفن قبلاً ثبت شده است.<br><a href='/'>بازگشت به صفحه اصلی</a>"
        else:
            return "پیام نامعتبر. لطفاً عدد '100' را برای ثبت‌نام ارسال کنید.<br><a href='/'>بازگشت به صفحه اصلی</a>"

    return render_template('register_phone.html')

# مسیر تنظیم زمان گزارش‌دهی روزانه
@app.route('/set_report_time', methods=['GET', 'POST'])
def set_report_time():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        report_time = request.form['report_time']

        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            user.report_time = report_time
            db.session.commit()
            return f"زمان گزارش‌دهی برای شماره تلفن {phone_number} به {report_time} تنظیم شد.<br><a href='/'>بازگشت به صفحه اصلی</a>"

        return "شماره تلفن یافت نشد. لطفاً ابتدا ثبت‌نام کنید.<br><a href='/'>بازگشت به صفحه اصلی</a>"

    return render_template('set_report_time.html')

# مسیر دریافت وزن کاربر و ارسال بازخورد
@app.route('/send_weight', methods=['GET', 'POST'])
def send_weight():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        weight_value = request.form['weight_value']

        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            new_weight = Weight(user_id=user.id, weight_value=float(weight_value), date=date.today(), time=datetime.now().strftime('%H:%M'))
            db.session.add(new_weight)
            db.session.commit()
            
            # ارسال بازخورد پس از ثبت وزن
            if float(weight_value) < 70:
                feedback = "آفرین! وزن شما خیلی خوب در حال کاهش است، به همین روال ادامه دهید!"
            else:
                feedback = "خیلی خوبه که وزن خودت رو ثبت کردی! تلاش کن رژیم و تمرینات خودت رو بهبود ببخشی."

            return f"وزن {weight_value} برای شماره تلفن {phone_number} با موفقیت ثبت شد. {feedback}<br><a href='/'>بازگشت به صفحه اصلی</a>"

        return "شماره تلفن یافت نشد. لطفاً ابتدا ثبت‌نام کنید.<br><a href='/'>بازگشت به صفحه اصلی</a>"

    return render_template('send_weight.html')

# مسیر مدیریت کاربران
@app.route('/manage_users', methods=['GET'])
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

# مسیر حذف کاربر
@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        # حذف تمامی سوابق وزن کاربر قبل از حذف خود کاربر
        Weight.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('کاربر با موفقیت حذف شد.', 'success')
        return redirect(url_for('manage_users'))
    return "کاربر یافت نشد."

# مسیر مشاهده گزارش وزن کاربر
@app.route('/weight_report/<phone_number>', methods=['GET'])
def weight_report(phone_number):
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return "شماره تلفن یافت نشد."

    weights = Weight.query.filter_by(user_id=user.id).all()
    weight_data = []
    for weight in weights:
        jalali_date = jdatetime.date.fromgregorian(date=weight.date)
        weekday = jalali_date.strftime('%A')
        weight_data.append({
            'date': jalali_date.strftime('%Y/%m/%d'),
            'weekday': weekday,
            'weight_value': weight.weight_value,
            'bmi': weight.bmi,
            'change_from_previous': weight.change_from_previous,
            'change_from_average': weight.change_from_average,
            'time': weight.time
        })
    return render_template('weight_report.html', phone_number=phone_number, weights=weight_data)

# زمانبندی ارسال پیام روزانه و یادآوری‌ها
def send_daily_messages():
    with app.app_context():
        users = User.query.all()
        current_time = datetime.now().strftime('%H:%M')
        for user in users:
            # ارسال یادآوری ۲ دقیقه قبل از زمان تنظیم شده
            reminder_time = (datetime.now() - timedelta(minutes=2)).strftime('%H:%M')
            if user.report_time == reminder_time:
                print(f"یادآوری: لطفاً وزن روزانه خود را ارسال کنید - شماره تلفن: {user.phone_number}")
            # ارسال پیامک درخواست وزن در زمان تنظیم شده
            if user.report_time == current_time:
                print(f"ارسال پیام روزانه به شماره {user.phone_number}: لطفاً وزن روزانه خود را ارسال کنید.")

# تنظیم برنامه زمانبندی
schedule.every().minute.do(send_daily_messages)  # اینجا هر دقیقه برای تست چک می‌کند، می‌توانید به روزانه تغییر دهید

if __name__ == '__main__':
    # اجرای برنامه Flask
    import threading

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()

    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")