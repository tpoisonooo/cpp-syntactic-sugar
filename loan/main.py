
# def loan_calculator(total_loan, annual_interest_rate, years):
#     if years <= 0 or total_loan <= 0 or annual_interest_rate < 0:
#         return []
#     # 计算总月数
#     total_months = years * 12
    
#     # 年利率转换为月利率
#     monthly_interest_rate = annual_interest_rate / 12 / 100

#     # 初始化结果列表
#     result = []

#     # 计算每月应付本金
#     principal_per_month = total_loan / total_months

#     for month in range(total_months):
#         # 计算每月应付利息
#         interest_per_month = (total_loan - month * principal_per_month) * monthly_interest_rate
        
#         # 计算每月应还金额（本金+利息）
#         payment_per_month = principal_per_month + interest_per_month

#         # 计算剩余本金
#         remaining_principal = total_loan - ((month + 1) * principal_per_month)

#         # 将每月应还款金额和剩余本金添加到结果列表
#         result.append((payment_per_month, remaining_principal, interest_per_month))

#     return result


def loan_calculator(principal, annual_rate, years):
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


def test_loan_caculator():
    result = loan_calculator(133000.0, 4.5, 1)
    for month, item in enumerate(result, start=1):
        print(f"Month {month}: Payment = {item[0]:.2f}, Remaining Principal = {item[1]:.2f}")


# def base(busi_loan = 2660000, busi_year = 20, busi_interest = 4.65,
#          fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 48,
#          shanghai_ceil = 36549, month_income = 5000, income_fund_rate = 12):
#     print('\n正常贷款还款，每个月扣掉公积金真实支出：')

#     fund_ceil = shanghai_ceil * income_fund_rate / 100 * 2 # 每月公积金缴存

#     year =  0

#     while year < max(busi_year, fund_year):
#         busi_per_month = loan_calculator(busi_loan, busi_interest, busi_year - year)
#         fund_per_month = loan_calculator(fund_loan, fund_interest, fund_year - year)

#         busi_month_12 = [0 for i in range(12)]
#         if len(busi_per_month) >= 12:
#             x = busi_per_month[0:12]
#             busi_month_12 = [item[0] for item in x]
#             busi_loan = busi_per_month[11][1]

#         fund_month_12 = [0 for i in range(12)]
#         if len(fund_per_month) >= 12:
#             x = fund_per_month[0:12]
#             fund_month_12 = [item[0] for item in x]
#             fund_loan = fund_per_month[11][1]
        
#         pay_month_12 = []
#         for x,y in zip(busi_month_12, fund_month_12):
#             pay = max(0, int(x+y-fund_ceil))
#             pay_month_12.append(pay)

#         year += 1

#         print('第{}年'.format(year), pay_month_12, busi_loan, fund_loan)

# def use_fund_left(busi_loan = 2660000, busi_year = 20, busi_interest = 4.65,
#          fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 480000,
#          shanghai_ceil = 36549, month_income = 5000, income_fund_rate = 12):
#     print('\n正常贷款还款，每个月扣掉公积金真实支出，考虑公积金余额：')
    
#     fund_ceil = shanghai_ceil * income_fund_rate / 100 * 2 # 每月公积金缴存

#     year =  0

#     while year < max(busi_year, fund_year):
#         busi_per_month = loan_calculator(busi_loan, busi_interest, busi_year - year)
#         fund_per_month = loan_calculator(fund_loan, fund_interest, fund_year - year)

#         busi_month_12 = [0 for i in range(12)]
#         if len(busi_per_month) >= 12:
#             x = busi_per_month[0:12]
#             busi_month_12 = [item[0] for item in x]
#             busi_loan = busi_per_month[11][1]

#         fund_month_12 = [0 for i in range(12)]
#         if len(fund_per_month) >= 12:
#             x = fund_per_month[0:12]
#             fund_month_12 = [item[0] for item in x]
#             fund_loan = fund_per_month[11][1]
        
#         pay_month_12 = []
#         for x,y in zip(busi_month_12, fund_month_12):
#             pay = x+y-fund_ceil
#             if fund_left > pay:
#                 fund_left -= pay
#                 pay_month_12.append(0)
#             else:
#                 pay = pay - fund_left
#                 fund_left = 0
#                 pay_month_12.append(int(pay))

#         year += 1

#         print('第{}年'.format(year), pay_month_12, busi_loan, fund_loan)

def print_head():
    print('-'*80, '剩余商贷','剩余公积金贷','本年支付利息')

# def use_fund_left_prepay(busi_loan = 2660000, busi_year = 20, busi_interest = 4.65,
#          fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 480000,
#          shanghai_ceil = 36549, month_left = 5000, income_fund_rate = 12):
#     print('\n月冲，每个月扣掉公积金真实支出，考虑公积金余额，每月攒{}每年提前还款一次：'.format(month_left))

#     fund_ceil = shanghai_ceil * income_fund_rate / 100 * 2 # 每月公积金缴存

#     year =  0
#     print_head()
#     while year < max(busi_year, fund_year):
#         busi_per_month = loan_calculator(busi_loan, busi_interest, busi_year - year)
#         fund_per_month = loan_calculator(fund_loan, fund_interest, fund_year - year)

#         busi_month_12 = [0 for i in range(12)]
#         if len(busi_per_month) >= 12:
#             x = busi_per_month[0:12]
#             busi_month_12 = [item[0] for item in x]
#             busi_loan = busi_per_month[11][1]

#         fund_month_12 = [0 for i in range(12)]
#         if len(fund_per_month) >= 12:
#             x = fund_per_month[0:12]
#             fund_month_12 = [item[0] for item in x]
#             fund_loan = fund_per_month[11][1]
        
#         pay_month_12 = []
#         for x,y in zip(busi_month_12, fund_month_12):
#             pay = x+y-fund_ceil
#             if fund_left > pay:
#                 fund_left -= pay
#                 pay_month_12.append(0)
#             else:
#                 pay = pay - fund_left
#                 fund_left = 0
#                 pay_month_12.append(int(pay))

#         year += 1

#         if busi_loan > 0:
#             busi_loan -= month_left * 12
#             if busi_loan < 0:
#                 fund_loan += busi_loan
#                 busi_loan = 0
#                 if fund_loan < 0:
#                     fund_loan = 0
#         else:
#             if fund_loan > 0:
#                 fund_loan -= month_left * 12
#                 fund_loan = max(0, fund_loan)

#         print('第{}年'.format(year), pay_month_12, busi_loan, fund_loan)

def use_fund_left_prepay_interest(busi_loan = 2660000, busi_year = 20, busi_interest = 4.65,
         fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 480000,
         shanghai_ceil = 36549, month_left = 5000, income_fund_rate = 12):
    print('\n月冲，每月扣掉公积金后真实支出，考虑公积金余额，每月攒{}每年提前还款一次。考虑利息：'.format(month_left))

    fund_ceil = shanghai_ceil * income_fund_rate / 100 * 2 # 每月公积金缴存

    year =  0
    print_head()
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
            pay = x+y-fund_ceil
            if fund_left > 0 and fund_left > pay:
                fund_left -= pay
                pay_month_12.append(0)
            else:
                pay = pay - fund_left
                fund_left = 0
                pay_month_12.append(int(pay))

        year += 1

        if busi_loan > 0:
            busi_loan -= month_left * 12
            if busi_loan < 0:
                fund_loan += busi_loan
                busi_loan = 0
                if fund_loan < 0:
                    fund_loan = 0
        else:
            if fund_loan > 0:
                fund_loan -= month_left * 12
                fund_loan = max(0, fund_loan)

        interest = sum(interest_list)
        interest_sum += interest
        print('第{}年'.format(year), pay_month_12, int(busi_loan), int(fund_loan), int(interest))

    print('累计支付利息：{}'.format(int(interest_sum)))


def use_fund_left_prepay_interest_year_pay(busi_loan = 2660000, busi_year = 20, busi_interest = 4.65,
         fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 480000,
         shanghai_ceil = 36549, month_left = 5000, income_fund_rate = 12):
    print('\n年冲先还公积金，每月扣掉公积金后真实支出，考虑公积金余额，每月攒{}每年提前还款一次。考虑利息：'.format(month_left))

    fund_ceil = shanghai_ceil * income_fund_rate / 100 * 2 # 每月公积金缴存

    if fund_loan > fund_left:
        fund_loan -= fund_left
        fund_left = 0
    else:
        fund_left -= fund_loan
        fund_loan = 0

    year =  0
    print_head()
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
            pay = x+y-fund_ceil
            if fund_left > 0 and fund_left > pay:
                fund_left -= pay
                pay_month_12.append(0)
            else:
                pay = pay - fund_left
                fund_left = 0
                pay_month_12.append(int(pay))

        year += 1

        if busi_loan > 0:
            busi_loan -= month_left * 12
            if busi_loan < 0:
                fund_loan += busi_loan
                busi_loan = 0
                if fund_loan < 0:
                    fund_loan = 0
        else:
            if fund_loan > 0:
                fund_loan -= month_left * 12
                fund_loan = max(0, fund_loan)

        interest = sum(interest_list)
        interest_sum += interest
        print('第{}年'.format(year), pay_month_12, int(busi_loan), int(fund_loan), int(interest))

    print('累计支付利息：{}'.format(int(interest_sum)))

def use_fund_left_prepay_interest_month_income(busi_loan = 2660000, busi_year = 20, busi_interest = 4.1,
         fund_loan = 600000, fund_year = 30, fund_interest = 3.1, fund_left = 480000,
         shanghai_ceil = 36549, month_income = 40000, income_fund_rate = 12):
    print('\n月冲，每月扣掉公积金后真实支出，考虑公积金余额，每月固定掏{}处理房贷，剩下的攒起来提前还贷。每年提前还款一次。考虑利息：'.format(month_income))

    fund_ceil = (shanghai_ceil * income_fund_rate / 100 * 2) + 1000# 每月公积金缴存
    print(fund_ceil)
    year =  0
    print_head()
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

                pay_month_12.append(0)
            else:
                pay = pay - fund_left
                fund_left = 0
                pay_month_12.append(int(pay))

        print(pay_month_12)

        year += 1
        income_month_12 = [ month_income for i in range(12)]
        year_left = 0
        for x,y in zip(income_month_12, pay_month_12):
            year_left += (x - y)


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
        print('第{}年公积金盖不住的数值'.format(year), pay_month_12, int(busi_loan), int(fund_loan), int(interest), int(year_left))

        if busi_loan < 1 and fund_loan < 1:
            break
    print('累计支付利息：{}'.format(int(interest_sum)))


use_fund_left_prepay_interest_month_income()
