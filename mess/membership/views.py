from django.shortcuts import HttpResponse

from membership.models import Member, Account

def members_list(request):
    return HttpResponse("Welcome to the future site of Mess' list of members!")

def member(request, id_num):
    name = Member.objects.get(id=id_num).given
    return HttpResponse('Welcome to the future site of %s\'s  Member Page!'
                        % name)

def accounts_list(request):
    return HttpResponse("Welcome to the future site of Mess' list of accounts!")

def account(request, id_num):
    name = Account.objects.get(id=id_num).name
    return HttpResponse('Welcome to the future site of %s\'s  Account Page!'
                        % name)
