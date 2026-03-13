from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from models import db, User, Cash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'key'

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    print(Cash.query.get(current_user.id))
    cash_accounting = Cash.query.filter_by(login=current_user.login).first().operations
    print(cash_accounting)
    # json.loads()
    if cash_accounting != "There haven't been operations yet":
        cash_accounting = json.loads(cash_accounting)

    return render_template('index.html', cash_accounting=cash_accounting)


@app.route('/add_new_accounting', methods=['GET', 'POST'])
@login_required
def add_new_accounting():
    if request.method == 'POST':
        accounting_name = request.form.get('accounting_name')
        cash_amount = request.form.get('cash_amount')
        currency = request.form.get('currency')

        cash = Cash.query.filter_by(login=current_user.login).first()
        cash_accounting = cash.operations
        if cash_accounting == "There haven't been operations yet":
            cash_accounting = []
        else:
            cash_accounting = json.loads(cash_accounting)

        cash_accounting.append({'accounting_name': accounting_name, 'cash_amount': cash_amount, 'currency': currency,
                                'operations': []})

        cash_accounting = json.dumps(cash_accounting)
        cash.operations = cash_accounting
        db.session.add(cash)
        db.session.commit()
        return redirect('/')
    return render_template('add_new_accounting.html')


@app.route('/edit_accounting/<int:accounting_id>', methods=['GET', 'POST'])
@login_required
def edit_accounting(accounting_id):
    cash = Cash.query.filter_by(login=current_user.login).first()
    all_cash_accounting = json.loads(cash.operations)
    cash_accounting = all_cash_accounting[accounting_id]
    print(cash_accounting)
    if request.method == 'POST':
        accounting_name = request.form.get('accounting_name')
        cash_amount = request.form.get('cash_amount')
        currency = request.form.get('currency')
        if accounting_name != '':
            cash_accounting['accounting_name'] = accounting_name
        if cash_amount != '':
            cash_accounting['cash_amount'] = cash_amount
        cash_accounting['currency'] = currency
        all_cash_accounting[accounting_id] = cash_accounting
        cash.operations = json.dumps(all_cash_accounting)

        db.session.add(cash)
        db.session.commit()

        return redirect(f'/operations/{accounting_id}')
    return render_template('edit_accounting.html', cash_accounting=cash_accounting)


@app.route('/delete_accounting/<int:accounting_id>', methods=['GET', 'POST'])
@login_required
def delete_accounting(accounting_id):
    cash = Cash.query.filter_by(login=current_user.login).first()
    all_cash_accounting = json.loads(cash.operations)
    all_cash_accounting.remove(all_cash_accounting[accounting_id])
    cash.operations = json.dumps(all_cash_accounting)

    db.session.add(cash)
    db.session.commit()

    return redirect('/')


@app.route('/operations/<int:accounting_id>')
@login_required
def operations(accounting_id):
    all_cash_accounting = json.loads(Cash.query.filter_by(login=current_user.login).first().operations)
    cash_profit = 0
    print(all_cash_accounting)
    cash_accounting = all_cash_accounting[accounting_id]
    starter_cash = int(cash_accounting['cash_amount'])
    print('CASH ACCOUNTING ', cash_accounting)
    cash_operations = cash_accounting['operations']
    if cash_operations:
        for cash_operation in cash_operations:
            if cash_operation['operation_type'] == 'profit':
                cash_profit += int(cash_operation['cash_amount'])
            else:
                cash_profit -= int(cash_operation['cash_amount'])
    print(cash_operations)
    # json.loads()

    return render_template('operations.html', cash_operations=cash_operations,
                           accounting_id=accounting_id, cash_accounting=cash_accounting, cash_profit=cash_profit,
                           starter_cash=starter_cash)


@app.route('/add_operation/<int:accounting_id>', methods=['GET', 'POST'])
@login_required
def add_operation(accounting_id):
    if request.method == 'POST':
        operation_name = request.form.get('operation_name')
        operation_type = request.form.get('operation_type')
        cash_amount = request.form.get('cash_amount')
        print(operation_name, operation_type, cash_amount)

        cash = Cash.query.filter_by(login=current_user.login).first()
        all_cash_accounting = json.loads(cash.operations)
        cash_accounting = all_cash_accounting[accounting_id]
        print(cash_accounting)

        if not cash_accounting['operations']:
            cash_operations = []
        else:
            cash_operations = cash_accounting['operations']
        cash_operations.append({'operation_name': operation_name, 'operation_type': operation_type,
                                'cash_amount': cash_amount})
        cash_accounting['operations'] = cash_operations
        all_cash_accounting[accounting_id] = cash_accounting
        all_cash_accounting = json.dumps(all_cash_accounting)
        cash.operations = all_cash_accounting
        db.session.add(cash)
        db.session.commit()
        return redirect(f'/operations/{accounting_id}')
    return render_template('add_operation.html')


@app.route('/edit_operation/<int:accounting_id>/<int:operation_id>', methods=['GET', 'POST'])
@login_required
def edit_operation(accounting_id, operation_id):
    cash_data_from_db = Cash.query.filter_by(login=current_user.login).first()
    all_cash_accounting = json.loads(cash_data_from_db.operations)
    cash_accounting = all_cash_accounting[accounting_id]
    cash_operations = cash_accounting['operations']
    print(cash_accounting)
    if request.method == 'POST':

        operation_name = request.form.get('operation_name')
        operation_type = request.form.get('operation_type')
        cash_amount = request.form.get('cash_amount')

        print(cash_operations[operation_id])
        if operation_name != '':
            cash_operations[operation_id]['operation_name'] = operation_name
        if operation_type != '':
            cash_operations[operation_id]['operation_type'] = operation_type
        if cash_amount != '':
            cash_operations[operation_id]['cash_amount'] = cash_amount

        all_cash_accounting[accounting_id]['operations'] = cash_operations
        cash_data_from_db.operations = json.dumps(all_cash_accounting)

        db.session.add(cash_data_from_db)
        db.session.commit()
        return redirect(f'/operations/{accounting_id}')
    return render_template('edit_operation.html', cash_operation=cash_operations[operation_id])


@app.route('/delete/<int:accounting_id>/<int:operation_id>', methods=['GET', 'POST'])
@login_required
def delete(accounting_id, operation_id):
    cash_data_from_db = Cash.query.filter_by(login=current_user.login).first()
    all_cash_accounting = json.loads(cash_data_from_db.operations)
    cash_operations = all_cash_accounting[accounting_id]['operations']
    cash_operations.remove(cash_operations[operation_id])

    all_cash_accounting[accounting_id]['operations'] = cash_operations
    cash_data_from_db.operations = json.dumps(all_cash_accounting)

    db.session.add(cash_data_from_db)
    db.session.commit()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        email = request.form.get('email')

        new_user = User(login=login, password=password, email=email)

        new_cash_user = Cash(login=login, operations="There haven't been operations yet")

        db.session.add(new_user)
        db.session.add(new_cash_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect('/')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(login=login).first()
        if user and user.password == password:
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
