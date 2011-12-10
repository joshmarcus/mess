import psycopg2
import sys

database = raw_input('Database?:')
password = raw_input('Password?:')
forreal = raw_input('Debug or for real? (if real, type "for real")')

conn = psycopg2.connect(database=database,user='mess',password=password,host='localhost')

balances = {}
account_equities = {}
member_equities = {}

trans = conn.cursor()
trans.execute("SELECT t.id, timestamp, account_id, name, purchase_type, purchase_amount, payment_amount, account_balance, member_id, first_name, last_name FROM accounting_transaction t LEFT JOIN membership_account a on t.account_id=a.id LEFT JOIN membership_member m on t.member_id=m.id LEFT JOIN auth_user u on m.user_id=u.id ORDER BY t.id;")


if False:   #debug to see the stupid query
    while 1:
        x = trans.fetchone()
        if x:
            print repr(x)
        else:
            sys.exit()


while 1:
    try:
        (tid, timestamp, account_id, name, purchase_type, purchase_amount, payment_amount, account_balance, member_id, first_name, last_name) = trans.fetchone()
    except:
        break
    if tid % 10000 == 0:
        print 'checking transaction %s' % (tid)

    if purchase_type == 'O':   # equity
        if member_id:
            if member_id not in member_equities:
                member_equities[member_id] = 0
            member_equities[member_id] += purchase_amount
        else:
            if account_id not in account_equities:
                account_equities[account_id] = 0
            account_equities[account_id] += purchase_amount
    if tid < 11538 and purchase_type == 'O':   # equity transactions during migration script don't affect account balance
        continue

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
            fix = conn.cursor()
            fix.execute("UPDATE accounting_transaction SET account_balance=%s WHERE id=%s;" % (expected_balance, tid))
            fix.close()
            print '...done'
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
            fix = conn.cursor()
            fix.execute("UPDATE membership_account SET balance=%s WHERE id=%s;" % (balances[aid], aid))
            fix.close()
            print '...done'
    if aid in balances:
        del balances[aid]
acct.close()

accteq = conn.cursor()
accteq.execute("SELECT id, name, deposit FROM membership_account;")
while 1:
    try:
        (aid, name, eq) = accteq.fetchone()
    except:
        break
    if aid in account_equities and account_equities[aid] != eq:
        print 'Wrong equity for account %s %s: %s should be %s' % (aid, repr(name), eq, account_equities[aid])
        if forreal == 'for real':
            print 'fixing...'
            fix = conn.cursor()
            fix.execute("UPDATE membership_account SET deposit=%s WHERE id=%s;" % (account_equities[aid], aid))
            fix.close()
            print '...done'
    if aid in account_equities:
        del account_equities[aid]
accteq.close()

memeq = conn.cursor()
memeq.execute("SELECT m.id, first_name, last_name, equity_held FROM membership_member m LEFT JOIN auth_user u ON m.user_id=u.id;")
while 1:
    try:
        (mid, first_name, last_name, eq) = memeq.fetchone()
    except:
        break
    if mid in member_equities and member_equities[mid] != eq:
        print 'Wrong equity for member %s %s: %s should be %s' % (mid, repr(first_name + ' ' + last_name), eq, member_equities[mid])
        if forreal == 'for real':
            print 'fixing...'
            fix = conn.cursor()
            fix.execute("UPDATE membership_member SET equity_held=%s WHERE id=%s;" % (member_equities[mid], mid))
            fix.close()
            print '...done'
    if mid in member_equities:
        del member_equities[mid]
memeq.close()
print 'Unmatched account balances: '+repr(balances)
print 'Unmatched account equities: '+repr(account_equities)
print 'Unmatched member equities: '+repr(member_equities)

if forreal=='for real':
    conn.commit()
    conn.close()
    print '...committed.'
