from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import paginator as p
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

#from mess.accounting import models as a_models
from mess.membership import forms, models
#from mess.profiles import forms as profiles_forms
#from mess.profiles import models as profiles_models

# number of members or accounts to show per page in respective lists
PER_PAGE = 20

@user_passes_test(lambda u: u.is_authenticated())
def members(request):
    context = RequestContext(request)
    if not request.user.is_staff:
        return member(request, request.user.username)
    members = models.Member.objects.all()
    if 'sort_by' in request.GET:
        form = forms.MemberListFilterForm(request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            if search:
                members = members.filter(
                        Q(user__first_name__icontains=search) |
                        Q(user__last_name__icontains=search))
            sort = form.cleaned_data['sort_by']
            if sort == 'alpha':
                members = members.order_by('user__username')
            if sort == 'oldjoin':
                members = members.order_by('date_joined')
            if sort == 'newjoin':
                members = members.order_by('-date_joined')
            if not form.cleaned_data['active']:
                members = members.exclude(status='a')
            if not form.cleaned_data['inactive']:
                members = members.exclude(status='i')
            if not form.cleaned_data['quit']:
                members = members.exclude(status='q')
            if not form.cleaned_data['missing']:
                members = members.exclude(status='m')
            if not form.cleaned_data['leave_of_absence']:
                members = members.exclude(status='L')
    else:
        form = forms.MemberListFilterForm()
    context['form'] = form
    pager = p.Paginator(members, PER_PAGE)
    context['pager'] = pager
    page_number = request.GET.get('p')
    context['page'] = get_current_page(pager, page_number)
    # drop any p= queries from the query string
    context['query_string'] = request.META['QUERY_STRING'].split('&p=', 1)[0]
    template = get_template('membership/members.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def member(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user.is_staff and not (request.user.is_authenticated() 
            and request.user.id == user.id):
        return HttpResponseRedirect(reverse('login'))
    context = RequestContext(request)
    context['member'] = user.get_profile()
    # to get around silly {% url %} limits
    context['address_name'] = 'address'
    context['phone_name'] = 'phone'
    context['email_name'] = 'email'
    # this list should live somewhere else, but I don't know where:
    context['contact_media'] = ['address', 'phone', 'email']
    template = get_template('membership/member.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_staff)
def member_add(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    is_errors = False
    # a fake member (no member should have an id of 0) will return
    # no addresses, phones, or emails
    member = models.Member(id=0)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('member', args=[username]))
        user_form = forms.UserForm(request.POST, prefix='user')
        member_form = forms.MemberForm(request.POST, prefix='member')
        related_accounts_form = forms.RelatedAccountsForm(member, request.POST, 
                prefix='related')
        address_formset = forms.AddressFormSet(request.POST, prefix='address',
                queryset=member.addresses.all())
        email_formset = forms.EmailFormSet(request.POST, prefix='email',
                queryset=member.emails.all())
        phone_formset = forms.PhoneFormSet(request.POST, prefix='phone',
                queryset=member.phones.all())
        if (user_form.is_valid() and member_form.is_valid() and 
                related_accounts_form.is_valid() and address_formset.is_valid()
                and phone_formset.is_valid() and email_formset.is_valid()):
            # need to do password business
            # email member with temp password?
            user = user_form.save()
            member = models.Member(**member_form.cleaned_data)
            member.user = user
            member.save()
            related_accounts = related_accounts_form.cleaned_data['accounts']
            member.accounts = related_accounts
            # have to handle formset-saving manually because of m2m
            member.addresses = fancy_save(address_formset)
            member.phones = fancy_save(phone_formset)
            member.emails = fancy_save(email_formset)
            member.save()
            return HttpResponseRedirect(reverse('member', 
                    args=[member.user.username]))
        else:
            is_errors = True
    else:
        user_form = forms.UserForm(prefix='user')
        member_form = forms.MemberForm(prefix='member')
        related_accounts_form = forms.RelatedAccountsForm(member, 
                prefix='related')
        address_formset = forms.AddressFormSet(prefix='address',
                queryset=member.addresses.all())
        email_formset = forms.EmailFormSet(prefix='email',
                queryset=member.emails.all())
        phone_formset = forms.PhoneFormSet(prefix='phone',
                queryset=member.phones.all())
    context = RequestContext(request)
    context['user_form'] = user_form
    context['member_form'] = member_form
    context['related_accounts_form'] = related_accounts_form
    context['formsets'] = [
        (address_formset, 'Addresses'), 
        (phone_formset, 'Phones'),
        (email_formset, 'Email Addresses'),
    ]
    context['is_errors'] = is_errors
    context['add'] = True
    template = get_template('membership/member_form.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_staff)
def member_edit(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    # a fake profile (no profile should have an id of 0) will return
    # no addresses, phones, or emails
    #profile = profiles_models.UserProfile(id=0)
    member = user.get_profile()
    is_errors = False
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('member', args=[username]))
        user_form = forms.UserForm(request.POST, prefix='user', instance=user)
        member_form = forms.MemberForm(request.POST, prefix='member', 
                instance=member)
        related_accounts_form = forms.RelatedAccountsForm(member, request.POST, 
                prefix='related')
        address_formset = forms.AddressFormSet(request.POST, 
                prefix='address',
                queryset=member.addresses.all())
        phone_formset = forms.PhoneFormSet(request.POST,
                prefix='phone',
                queryset=member.phones.all())
        email_formset = forms.EmailFormSet(request.POST,
                prefix='email',
                queryset=member.emails.all())
        if (user_form.is_valid() and member_form.is_valid() and 
                related_accounts_form.is_valid() and address_formset.is_valid()
                and phone_formset.is_valid() and email_formset.is_valid()):
            user_form.save()
            member_form.save()
            related_accounts = related_accounts_form.cleaned_data['accounts']
            member.accounts = related_accounts
            # have to handle formset-saving manually because of m2m
            member.addresses = fancy_save(address_formset)
            member.phones = fancy_save(phone_formset)
            member.emails = fancy_save(email_formset)
            member.save()
            return HttpResponseRedirect(reverse('member', args=[username]))
        else:
            is_errors = True
    else:
        user_form = forms.UserForm(instance=user, prefix='user')
        member_form = forms.MemberForm(instance=member, prefix='member')
        related_accounts_form = forms.RelatedAccountsForm(member, 
                prefix='related')
        address_formset = forms.AddressFormSet(prefix='address',
                queryset=member.addresses.all())
        phone_formset = forms.PhoneFormSet(prefix='phone',
                queryset=member.phones.all())
        email_formset = forms.EmailFormSet(prefix='email',
                queryset=member.emails.all())
    context = RequestContext(request)
    context['member'] = member
    context['user_form'] = user_form
    context['member_form'] = member_form
    context['related_accounts_form'] = related_accounts_form
    context['formsets'] = [
        (address_formset, 'Addresses'), 
        (phone_formset, 'Phones'),
        (email_formset, 'Email Addresses'),
    ]
    context['is_errors'] = is_errors
    template = get_template('membership/member_form.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def accounts(request):
    context = RequestContext(request)
    if request.user.is_staff:
        account_objs = models.Account.objects.all()
    else:
        member = models.Member.objects.get(user=request.user)
        account_objs = member.accounts.all()
    pager = p.Paginator(account_objs, PER_PAGE)
    context['pager'] = pager
    page_number = request.GET.get('p')
    context['page'] = get_current_page(pager, page_number)
    template = get_template('membership/accounts.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def account(request, id):
    account = get_object_or_404(models.Account, id=id)
    request_member = models.Member.objects.get(user=request.user)
    if not request.user.is_staff and not (request.user.is_authenticated() 
            and request_member in account.members.all()):
        return HttpResponseRedirect(reverse('login'))
    context = RequestContext(request)
    context['account'] = account
    transactions = account.transaction_set.all()
    context['transactions'] = transactions
    template = get_template('membership/account.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_staff)
def account_add(request):
    if request.method == 'POST':
        form = forms.AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            return HttpResponseRedirect(reverse('account', args=[account.id]))
    else:
        form = forms.AccountForm()
    context = RequestContext(request)
    context['form'] = form
    context['add'] = True
    template = get_template('membership/account_form.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_staff)
def account_edit(request, id):
    account = get_object_or_404(models.Account, id=id)
    if request.method == 'POST':
        form = forms.AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('account', args=[account.id]))
    else:
        form = forms.AccountForm(instance=account)
    context = RequestContext(request)
    context['form'] = form
    template = get_template('membership/account_form.html')
    return HttpResponse(template.render(context))

# TODO: split out into add_address, add_email, add_phone for simplicity
@user_passes_test(lambda u: u.is_authenticated())
def add_contact(request, username, medium):
    context = RequestContext(request)
    referer = request.META.get('HTTP_REFERER', '')
    user = get_object_or_404(User, username=username)
    # use 'this_user' because context['user'] overrides logged-in user 
    context['this_user'] = user
    # medium may be 'address', 'phone', or 'email'
    MediumForm = forms.contact_form_map[medium]
    if request.method == 'POST':
        form = MediumForm(request.POST)
        referer = request.POST.get('referer')
        if form.is_valid():
            field_dict = {}
            for key in form.cleaned_data:
                if key not in ('DELETE', 'id'):
                    field_dict[key] = form.cleaned_data[key]
            try:
                match = form._meta.model.objects.get(**field_dict)
            except form._meta.model.DoesNotExist:
                match = None
            if match:
                medium_obj = match
            else:
                medium_obj = form.save()
            member = user.get_profile()
            member_medium_objs = {
                'address': member.addresses,
                'phone': member.phones,
                'email': member.emails
            }[medium]
            member_medium_objs.add(medium_obj)
            if referer:
                return HttpResponseRedirect(referer)
            else:
                return HttpResponseRedirect(reverse('member', args=[username]))
    else:
        form = MediumForm()
    context['add'] = True
    context['form'] = form
    context['medium'] = medium
    context['referer'] = referer
    return render_to_response('membership/contact_form.html', context)

@user_passes_test(lambda u: u.is_authenticated())
def edit_address(request, username, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    address = get_object_or_404(models.Address, id=id)
    # need to strip ID so new address is created instead of m2m
    address_dict = {}
    for key in address.__dict__:
        if key != 'id':
            address_dict[key] = address.__dict__[key]
    if request.method == 'POST':
        form = forms.AddressForm(request.POST, initial=address_dict)
        if form.is_valid():
            new_address = form.save()
            member = user.get_profile()
            member.addresses.remove(address)
            member.addresses.add(new_address)
        return HttpResponseRedirect(reverse('member', args=[username]))
    else:
        form = forms.AddressForm(initial=address_dict)
    context['medium'] = 'address'
    context['form'] = form
    template = get_template('membership/contact_form.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def edit_email(request, username, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    email = get_object_or_404(models.Email, id=id)
    # need to strip ID so new email is created instead of m2m
    email_dict = {}
    for key in email.__dict__:
        if key != 'id':
            email_dict[key] = email.__dict__[key]
    if request.method == 'POST':
        form = forms.EmailForm(request.POST, initial=email_dict)
        if form.is_valid():
            new_email = form.save()
            member = user.get_profile()
            member.emails.remove(email)
            member.emails.add(new_email)
        return HttpResponseRedirect(reverse('member', args=[username]))
    else:
        form = forms.EmailForm(initial=email_dict)
    context['medium'] = 'email'
    context['form'] = form
    template = get_template('membership/contact_form.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def edit_phone(request, username, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    phone = get_object_or_404(models.Phone, id=id)
    # need to strip ID so new phone is created instead of m2m
    phone_dict = {}
    for key in phone.__dict__:
        if key != 'id':
            phone_dict[key] = phone.__dict__[key]
    if request.method == 'POST':
        form = forms.PhoneForm(request.POST, initial=phone_dict)
        if form.is_valid():
            new_phone = form.save()
            member = user.get_profile()
            member.phones.remove(phone)
            member.phones.add(new_phone)
        return HttpResponseRedirect(reverse('member', args=[username]))
    else:
        form = forms.PhoneForm(initial=phone_dict)
    context['medium'] = 'phone'
    context['form'] = form
    template = get_template('membership/contact_form.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def remove_address(request, username, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    address = get_object_or_404(models.Address, id=id)
    context['contact'] = address
    context['medium'] = 'address'
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('member', args=[username]))
        member = user.get_profile()
        member.addresses.remove(address)
        # keep old addresses around for later matching
        return HttpResponseRedirect(reverse('member', args=[username]))
    template = get_template('membership/remove_contact.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def remove_phone(request, username, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    phone = get_object_or_404(models.Phone, id=id)
    context['contact'] = phone
    context['medium'] = 'phone'
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('member', args=[username]))
        member = user.get_profile()
        member.phones.remove(phone)
        # delete phone if it's not attached to anyone
        if not phone.member_set.count():
            phone.delete()
        return HttpResponseRedirect(reverse('member', args=[username]))
    template = get_template('membership/remove_contact.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_authenticated())
def remove_email(request, username, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    email = get_object_or_404(models.Email, id=id)
    context['contact'] = email
    context['medium'] = 'email'
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('member', args=[username]))
        member = user.get_profile()
        member.emails.remove(email)
        # delete email if it's not attached to anyone
        if not email.member_set.count():
            email.delete()
        return HttpResponseRedirect(reverse('member', args=[username]))
    template = get_template('membership/remove_contact.html')
    return HttpResponse(template.render(context))

def remove_contact(request, username, medium, id):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    context['this_user'] = user
    MediumClass = models.__getattribute__(medium.capitalize())
    context['medium'] = medium
    contact = get_object_or_404(MediumClass, id=id)
    context['contact'] = contact
    # syntax to actually remove it is ?medium=phone&target=1234&yes=yes
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse('member', args=[username]))
        member = user.get_profile()
        member_medium_objs = {
            'address': member.addresses,
            'phone': member.phones,
            'email': member.emails
        }[medium]
        listings = member_medium_objs.all()
        target = request.POST.get('target')
        for listing in listings:
            raise Exception
            if listing == contact:
                member_medium_objs.remove(listing)
                if not listing.member_set.count():
                    listing.delete()
        return HttpResponseRedirect(reverse('member', args=[username]))
    # if missing the confirmation &yes=yes:
    return render_to_response('membership/remove_contact.html', context)
    
def contact_formset_form(request, medium):
    context = RequestContext(request)
    MediumForm = forms.contact_form_map[medium]
    index = request.GET.get('index')
    if index:
        form = MediumForm(prefix='%s-%s' % (medium, index))
    else:
        form = MediumForm()
    context['form'] = form
    template = get_template('membership/snippets/contact_formset.html')
    return HttpResponse(template.render(context))


# helper functions below

def fancy_save(formset):
    object_list = []
    for form in formset.forms:
        if form.cleaned_data.get('DELETE') or not form.cleaned_data:
            continue
        field_dict = {}
        for key in form.cleaned_data:
            if key not in ('DELETE', 'id'):
                field_dict[key] = form.cleaned_data[key]
        try:
            match = formset.model.objects.get(**field_dict)
        except formset.model.DoesNotExist:
            match = None
        if match:
            object_list.append(match)
        else:
            instance = formset.model()
            for key in form.cleaned_data:
                if key != 'id':
                    instance.__dict__[key] = form.cleaned_data[key]
            instance.save()
            object_list.append(instance)
    return object_list

def get_current_page(pager, page_number):
    try:
        current_page = pager.page(page_number)
    except (p.PageNotAnInteger, TypeError):
        current_page = pager.page(1)
    return current_page

# This raw_list function outputs raw data for use by ajax and xmlhttprequest.
# Since the data is output raw, it doesn't use any template.
#def raw_list(request):
#	# try.  Catches non-integers, blank field, and missing field
#	try: maxresults = int(request.GET.get('maxresults'))
#	except: maxresults = 30
#
#	# if we're listing accounts, list accounts matching pattern.
#	# don't bother checking the location of *'s, assume account=*pattern*
#	if request.GET.has_key('list') and request.GET.get('list') == 'accounts':
#		account_list = models.Account.objects.all()
#		if request.GET.has_key('account'):
#			pattern = request.GET.get('account').replace('*','')
#			account_list = account_list.filter(name__contains = pattern)
#		account_names = account_list.values_list('name',flat=True)[:maxresults]
#		return HttpResponse('\n'.join(account_names))
#
#	# if we're listing members, list members matching account and/or pattern
#	# note: This part may be SLOW due to [python-iteration] over all db entries
#	if request.GET.has_key('list') and request.GET.get('list') == 'members':
#		if request.GET.has_key('account'):
#			acct = request.GET.get('account')
#			member_list = models.Member.objects.filter(accounts__name = acct)
#		else:
#			member_list = models.Member.objects.all()
#		mnames = [member.user.get_full_name() for member in member_list]
#
#		# if we have a member pattern, filter it case-insensitively
## CAN'T SEEM TO DO A DATABASE FILTER ON member__user__get_full_name__contains
#		if request.GET.has_key('member'):
#			pattern = request.GET.get('member').replace('*','').lower()
#			mnames = [m for m in mnames if m.lower().find(pattern) >= 0]
#
#		mnames = mnames[:maxresults]
#		return HttpResponse('\n'.join(mnames))		
#
#	# if we're not sure what we're listing, fail
#	return HttpResponse('error in request for raw list')
