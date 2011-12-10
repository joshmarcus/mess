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
trans.execute("SELECT t.id, timestamp, account_id, name, purchase_type, purchase_amount, payment_amount, account_balance, member_id, first_name, last_name FROM accounting_transaction t LEFT JOIN membership_account a on t.account_id=a.id LEFT JOIN membership_member m on t.member_id=m.id LEFT JOIN auth_user u on m.user_id=u.id WHERE (t.id>11538 or t.purchase_type is null or t.purchase_type<>'O') ORDER BY t.id;")


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
    if purchase_type == 'O' and member_id:
        print 'Removing member %s %s %s from transaction %s account %s' % (member_id, first_name, last_name, tid, name)
        if forreal == 'for real':
            print 'fixing...'
            fix = conn.cursor()
            fix.execute("UPDATE accounting_transaction SET member_id=NULL WHERE id=%s;" % tid)
            fix.close()
            print '...done'

trans.close()

# Also drop equity_held from all members
drop_held = conn.cursor()
print 'Dropping all member equity_held...'
drop_held.execute("UPDATE membership_member SET equity_held=0;")
drop_held.close()


if forreal=='for real':
    conn.commit()
    conn.close()
    print '...committed.'
