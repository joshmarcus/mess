import psycopg2
import sys

database = raw_input('Database?:')
password = raw_input('Password?:')
forreal = raw_input('Debug or for real? (if real, type "for real")')

conn = psycopg2.connect(database=database,user='mess',password=password,host='localhost')

balances = {}

trans = conn.cursor()
trans.execute("SELECT t.id, timestamp, account_id, name, purchase_amount, payment_amount, account_balance FROM accounting_transaction t LEFT JOIN membership_account a on t.account_id=a.id WHERE (t.id>11538 or t.purchase_type is null or t.purchase_type<>'O') ORDER BY t.id;")


if False:   #debug to see the stupid query
    while 1:
        x = trans.fetchone()
        if x:
            print repr(x)
        else:
            sys.exit()

if forreal == 'for real':
    fix = conn.cursor()

while 1:
    try:
        (tid, timestamp, account_id, name, purchase_amount, payment_amount, account_balance) = trans.fetchone()
    except:
        break
    if tid % 10000 == 0:
        print 'checking transaction %s' % (tid)
    if account_id not in balances:
        balances[account_id] = 0
    expected_balance = balances[account_id] + purchase_amount - payment_amount
    if account_balance != expected_balance:
        print 'Error on transaction %s account %s %s' % (tid, account_id, repr(name))
        print 'Old balance: %s' % balances[account_id]
        print 'Purchase: %s' % purchase_amount
        print 'Payment: %s' % payment_amount
        print 'New balance: %s' % account_balance
        print 'But new balance should be: %s' % expected_balance
        if forreal == 'for real':
            print 'fixing...'
            fix.execute("UPDATE accounting_transaction SET account_balance=%s WHERE id=%s;" % (expected_balance, tid))
    balances[account_id] = expected_balance
trans.close()


acct = conn.cursor()
acct.execute("SELECT id, name, balance FROM membership_account;")
while 1:
    try:
        (aid, name, balance) = acct.fetchone()
    except:
        break
    if aid in balances and balances[aid] != balance:
        print 'Wrong balance for account %s %s' % (aid, repr(name))
        if forreal == 'for real':
            print 'fixing...'
            fix.execute("UPDATE membership_account SET balance=%s WHERE id=%s;" % (balances[aid], aid))
acct.close()

if forreal == 'for real':
    print 'committing all changes...'
    fix.close()
    conn.commit()
    conn.close()
    print '...done'
