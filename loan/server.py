from flask import Flask, request
from flask import Flask, request, render_template

app = Flask(__name__)

def loan_calculator(principal, annual_rate, years):
    if years <= 0:
        return []
    monthly_rate = annual_rate / 12 / 100  # Assume the input rate is in percentage
    total_months = years * 12

    # Calculate the monthly principal payment
    monthly_principal_payment = principal / total_months

    payments = []
    for month in range(1, total_months + 1):
        # Calculate the interest for the current month
        monthly_interest = (principal - (month - 1) * monthly_principal_payment) * monthly_rate
        # The total monthly payment is the sum of the principal and interest payments
        total_monthly_payment = monthly_principal_payment + monthly_interest
        # The remaining principal is the original amount minus what has been paid so far
        remaining_principal = principal - month * monthly_principal_payment
        # Each element in the list is a tuple (total monthly payment, remaining principal, monthly interest)
        payments.append((total_monthly_payment, remaining_principal, monthly_interest))

    return payments

def use_fund_left_prepay_interest_month_income(busi_loan = 2660000, busi_year = 20, busi_interest = 4.1,
         fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 480000, month_income = 40000, fund_ceil = 9000):
    print('\n月冲，每月扣掉公积金后真实支出，考虑公积金余额，每月固定掏{}处理房贷，剩下的攒起来提前还贷。每年提前还款一次。考虑利息：'.format(month_income))

    ret = []
    print(fund_ceil)
    year =  0
    interest_sum = 0
    while year < max(busi_year, fund_year):
        busi_per_month = loan_calculator(busi_loan, busi_interest, busi_year - year)
        fund_per_month = loan_calculator(fund_loan, fund_interest, fund_year - year)
        interest_list = []
        busi_month_12 = [0 for i in range(12)]
        if len(busi_per_month) >= 12:
            x = busi_per_month[0:12]
            busi_month_12 = [item[0] for item in x]
            busi_loan = busi_per_month[11][1]
            interest_list.extend([item[2] for item in x])

        fund_month_12 = [0 for i in range(12)]
        if len(fund_per_month) >= 12:
            x = fund_per_month[0:12]
            fund_month_12 = [item[0] for item in x]
            fund_loan = fund_per_month[11][1]
            interest_list.extend([item[2] for item in x])
        
        pay_month_12 = []
        for x,y in zip(busi_month_12, fund_month_12):
            fund_left += fund_ceil
            pay = max(x+y,0)

            if fund_left > 0 and fund_left > pay:
                fund_left -= pay
                print('pay {} 公积金余额 {}'.format(pay, fund_left))

                pay_month_12.append(month_income)
            else:
                pay = pay - fund_left
                fund_left = 0
                pay_month_12.append(int(pay)+month_income)

        print(pay_month_12)

        year += 1
        year_left = month_income * 12

        if busi_loan > 0:
            busi_loan -= year_left
            if busi_loan < 0:
                fund_loan += busi_loan
                busi_loan = 0
                if fund_loan < 0:
                    fund_loan = 0
        else:
            if fund_loan > 0:
                fund_loan -= year_left
                fund_loan = max(0, fund_loan)


        interest = sum(interest_list)
        interest_sum += interest

        content = '''
<fieldset>
    <legend>第{}年</legend>
    <div>每月准备现金：{}</div>
    <div>年底公积金余额：{:.0f}</div>
    <div>年底剩余商贷：{:.0f}，剩余公积金贷：{:.0f}, 本年度支付利息 {:.0f}</div>
</fieldset>
'''.format(year, pay_month_12, fund_left, busi_loan, fund_loan, interest)
        ret.append(content)

        if busi_loan < 1 and fund_loan < 1:
            break
    years = len(ret)
    return ''.join(ret), int(interest_sum), years, fund_left


def get_interest(total, rate, years):
    loan_monthly = loan_calculator(total, rate, int(years))
    loan_interest = 0
    for item in loan_monthly:
        loan_interest += item[2]
    return round(loan_interest)


@app.route('/get', methods=['GET'])
def load():
    # 使用 request.args.get() 来获取GET请求的参数
    total_loan = int(request.args.get('total_loan'))
    loan_rate = float(request.args.get('loan_rate'))
    loan_bp = float(request.args.get('loan_bp'))
    loan_years = int(request.args.get('loan_years'))
    fund_loan = int(request.args.get('fund_loan'))
    fund_loan_rate = float(request.args.get('fund_loan_rate'))
    fund_loan_years = int(request.args.get('fund_loan_years'))
    fund_balance = int(request.args.get('fund_balance'))
    monthly_deposit_total = int(request.args.get('monthly_deposit_total'))
    monthly_payment_amount = int(request.args.get('monthly_payment_amount'))

    total_loan *= 10000
    loan_rate += loan_bp / 100.0
    fund_loan *= 10000
    fund_balance *= 10000

    # 基本信息
    interest_a = get_interest(total_loan, loan_rate, loan_years)
    interest_b = get_interest(fund_loan, fund_loan_rate, fund_loan_years)
    style='''
<style>
    .red-bold-text {
        color: red;
        font-weight: bold;
    }
    .blue-text {
        color: blue;
        font-weight: bold;
    }
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    img {
        width: 50vw;
        height: auto;
    }
</style>    
    '''
    user_part = '''
<h3>基本信息</h3>
<div>商贷：{}，利率 {:.2f}，{} 年，正常还款利息 {}</div>
<div>公积金贷：{}，利率 {:.2f}，{} 年，正常还款利息 {}，公积金{}，公积金(单位+贷款人)月缴存{}</div>
    '''.format(total_loan, loan_rate, loan_years, interest_a, fund_loan, fund_loan_rate, fund_loan_years,  interest_b, fund_balance, monthly_deposit_total)

    # 提前还款
    content, new_interest, years, fund_left = use_fund_left_prepay_interest_month_income(busi_loan=total_loan, busi_year=loan_years, busi_interest=loan_rate, fund_loan=fund_loan, fund_year=fund_loan_years, fund_interest=fund_loan_rate, fund_left=fund_balance,
        month_income=monthly_payment_amount, fund_ceil=monthly_deposit_total)

    save_interest = interest_a + interest_b - new_interest
    loan_part = '<h3>提前还款计划</h3>'
    loan_part += '<div>累计还贷 {} 年，付了 {} 利息 </div>'.format(years, new_interest)
    loan_part += '<div>因每年底提前还款 1 次 {}，<label class="red-bold-text">节约利息 {}</label>。分成每年 2 次 {} 还能节约更多！ </div>'.format(12 * monthly_payment_amount, save_interest, 6 * monthly_payment_amount)
    loan_part += '<div>贷款结束后，<label class="blue-text">可提取剩余公积金 {:.0f}</label> </div>'.format(fund_left)
    loan_part += '</div></br>'

    author_part = '''
<h3>支持作者，解锁更多城市</h3>
<div class="container">
    <img src="https://deploee.oss-cn-shanghai.aliyuncs.com/zanshang.jpg" alt="赞赏码">
</div>
'''
    return style + user_part + loan_part + content + author_part


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
