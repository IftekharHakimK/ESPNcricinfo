from django.shortcuts import render
import cx_Oracle
# Create your views here.

from django.http import HttpResponse


def index(request):
    dsn_tns  = cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
    conn = cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
    c = conn.cursor()
    print(c)
    print('Success') 
    c.execute("SELECT * from PLAYER")   
    out = ''
    print(c)
    for row in c : 
        out +=str(row) + ' \n '
    conn.close()
    return HttpResponse(out,content_type="text/plain")
