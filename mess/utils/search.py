from django.db.models import Q

from mess.people.models import Person
from mess.membership.models import Member, Account
from mess.contact.models import Address, Email, Phone

def create_dictionary(list):
    """Create a dictionary from a given list.
    
    dict = {'primary_key': 'account_name'}
    """
    dict = {}
    for i in list:
        # Should we use str(i) here?
        dict[i.id] = unicode(i)
    return dict

def account_members_dict(id):
    """ Return a dictionary of Members in an Account given
    a primary key.
    
    dict = {'primary_key': 'name'}
    """
    list = Account.objects.get(id=id).members.all()
    return create_dictionary(list)

def search_for_accounts(string):
    """ Return a dictionary of Accounts with names matching a string.
    
    dict = {'primary_key': 'name'}
    """
    list = Account.objects.filter(name__icontains=string)
    return create_dictionary(list)

def search_for_address(string):
    """ Return a dictionary of Addresses with the first address line
    matching a string.
    
    dict = {'primary_key': 'name'}
    """
    list = Address.objects.filter(address_1__icontains=string)
    return create_dictionary(list)

def search_for_email(string):
    """ Return a dictionary of Email matching a string.
    
    dict = {'primary_key': 'name'}
    """
    list = Email.objects.filter(email__icontains=string)
    return create_dictionary(list)

def search_for_phone(string):
    """ Return a dictionary of Phones matching a string.
    
    dict = {'primary_key': 'name'}
    """
    # ext is an interger.  How can I search it as a string?
    #list = Phone.objects.filter(number__contains=string, ext__contains=string)
    list = Phone.objects.filter(number__contains=string)
    return create_dictionary(list)

def search_for_people(string):
    """ Return a dictionary of People with names matching a string.
    
    dict = {'primary_key': 'name'}
    """
    list = Member.objects.filter(Q(user__first_name__icontains=string)
                                | Q(user__last_name__icontains=string))
    return create_dictionary(list)

def search_for_members(string):
    """ Return a dictionary of Members with names matching a string.
    
    dict = {'primary_key': 'name'}
    """
    list = Member.objects.filter(Q(user__first_name__icontains=string)
                                | Q(user__last_name__icontains=string))
    return create_dictionary(list)

def search_for_string(search, string):
    """Search for a string in the given model"""
    SEARCH_TYPES = {
        'people': search_for_people,
        'members': search_for_members,
        'accounts': search_for_accounts,
        'address': search_for_address,
        'email': search_for_email,
        'phone': search_for_phone,
    }
    dict = SEARCH_TYPES[search](string)
    return dict
