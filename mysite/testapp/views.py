from django.shortcuts import render,redirect
#from .models import Job
from django.db import connection
from django.contrib.sessions.models import Session
from django.contrib import messages
import cx_Oracle
from django.core.files.base import ContentFile
import base64
# Create your views here.

from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
# Create your views here.
def get_cursor():
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	return cursor
def  list_a (request):
	# cursor = connection.cursor()
	# sql = "INSERT INTO JOBS VALUES(%s,%s,%s,%s)"
	# cursor.execute(sql,['NEW_JOB','Something New',4000,8000])
	# connection.commit()
	# cursor.close()
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor = connection.cursor()
	sql = "SELECT * FROM PLAYER"
	cursor.execute(sql)
	result = cursor.fetchall()
	
	# cursor = connection.cursor()
	# sql = "SELECT * FROM JOBS WHERE MIN_SALARY=%s"
	# cursor.execute(sql,[4000])
	# result = cursor.fetchall()
	
	
	
	cursor.close()
	dict_result = []
	
	for r in result:
		First_name = r[1]
		Role = r[3]
		Nationality = r[7]
		row = {'First_name': First_name, 'Role':Role, 'Nationality':Nationality}
		dict_result.append(row)
	
	#return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
	return render(request,'list_a.html',{'players' : dict_result})

def home(request):
	cursor=get_cursor()
	sql="select * from news order by news_date desc"
	cursor.execute(sql)
	result=cursor.fetchall()
	newses=[]
	for r in result:
		image=r[1]
		if image!=None:
			image=base64.b64encode(image.read()).decode()
		newses.append({'news_id':r[0],'title':r[3],'news_date':r[2],'image':image})
	return render(request,'home.html',{'newses':newses})

def players(request):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor = connection.cursor()
	sql = "SELECT first_name||' '||last_name name, nationality, trim(player_id) FROM PLAYER ORDER BY name "
	cursor.execute(sql)
	result = cursor.fetchall()
	cursor.close()
	players = []
	for r in result:
		row={'f1':r[0],'f2':r[1],'f3':r[2],'image':get_image(r[2])}
		players.append(row)
	return render(request,'player_table.html',{'players':players})

def matches(request):
	return render(request,'matches.html');

def get_image(player_id):
	cursor=get_cursor()
	sql="select image from player where trim(player_id)=trim(:player_id)"
	cursor.execute(sql,{'player_id':player_id})
	result=cursor.fetchone()
	image=result[0]
	if image!=None:
			image=base64.b64encode(image.read()).decode()
	return image
def player_detail(request,playerid):
	if request.method=='GET':
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)

		connection.commit()
		cursor=connection.cursor()

		sql="select initcap(first_name), initcap(last_name), role, to_char(dob,'DD-Mon-YYYY'), nvl(batting_style,'-'), nvl(bowling_style,'-') , nationality, floor((sysdate-dob)/365) year, mod(floor(sysdate-dob),365) day, image from player where trim(player_id)= trim(:playerid)"

		cursor.execute(sql,{'playerid':playerid})
		result=cursor.fetchall()
		cursor.close()
		cursor=connection.cursor()
		sql2= "SELECT SUM(PLAYED.RUN_SCORED), SUM(PLAYED.BALL_FACED),SUM(PLAYED.EXTRAS),SUM(PLAYED.FOURS),SUM(PLAYED.SIXES), SUM(PLAYED.WICKETS), SUM(PLAYED.MAIDENS), SUM(PLAYED.OVERS), SUM(PLAYED.RUN_CONCEDED) FROM PLAYED,(SELECT SQUAD_ID FROM SQUAD,MATCH,TOURNAMENT WHERE SQUAD.MATCH_ID=MATCH.MATCH_ID AND MATCH.TOURNAMENT_ID = TOURNAMENT.TOURNAMENT_ID AND TOURNAMENT.FORMAT='ODI') TAB WHERE PLAYED.SQUAD_ID=TAB.SQUAD_ID AND trim(PLAYED.PLAYER_ID)= trim(:playerid)"
		cursor.execute(sql2,{'playerid':playerid})
		res2= cursor.fetchall()
		cursor.close()
		cursor=connection.cursor()
		sql="SELECT SUM(PLAYED.RUN_SCORED), SUM(PLAYED.BALL_FACED),SUM(PLAYED.EXTRAS),SUM(PLAYED.FOURS),SUM(PLAYED.SIXES), SUM(PLAYED.WICKETS), SUM(PLAYED.MAIDENS), SUM(PLAYED.OVERS), SUM(PLAYED.RUN_CONCEDED) FROM PLAYED,(SELECT SQUAD_ID FROM SQUAD,MATCH,TOURNAMENT WHERE SQUAD.MATCH_ID=MATCH.MATCH_ID AND MATCH.TOURNAMENT_ID = TOURNAMENT.TOURNAMENT_ID AND TOURNAMENT.FORMAT='T20') TAB WHERE PLAYED.SQUAD_ID=TAB.SQUAD_ID AND trim(PLAYED.PLAYER_ID)= trim(:playerid)"
		cursor.execute(sql,{'playerid':playerid})
		res3=cursor.fetchall()
		cursor.close()
		cursor=connection.cursor()
		sql="SELECT COUNT(DISTINCT(TAB.SQUAD_ID)) FROM (SELECT SQUAD_ID FROM SQUAD,MATCH,TOURNAMENT WHERE SQUAD.MATCH_ID=MATCH.MATCH_ID AND MATCH.TOURNAMENT_ID = TOURNAMENT.TOURNAMENT_ID AND TOURNAMENT.FORMAT='ODI') TAB, PLAYED WHERE TAB.SQUAD_ID=PLAYED.SQUAD_ID AND trim(PLAYED.PLAYER_ID)=trim(:playerid)"
		cursor.execute(sql,{'playerid':playerid})
		res4=cursor.fetchone()[0]
		cursor.close()
		cursor=connection.cursor()
		sql="SELECT COUNT(DISTINCT(TAB.SQUAD_ID)) FROM (SELECT SQUAD_ID FROM SQUAD,MATCH,TOURNAMENT WHERE SQUAD.MATCH_ID=MATCH.MATCH_ID AND MATCH.TOURNAMENT_ID = TOURNAMENT.TOURNAMENT_ID AND TOURNAMENT.FORMAT='T20') TAB, PLAYED WHERE TAB.SQUAD_ID=PLAYED.SQUAD_ID AND trim(PLAYED.PLAYER_ID)= trim(:playerid)"
		cursor.execute(sql,{'playerid':playerid})
		res5=cursor.fetchone()[0]
		cursor.close()
		cursor = connection.cursor()
		bowled=cursor.var(cx_Oracle.NUMBER)
		caught = cursor.var(cx_Oracle.NUMBER)
		runout=cursor.var(cx_Oracle.NUMBER)
		cursor.callproc('FIELDING',[playerid,'ODI',bowled,caught,runout])
		cursor.close()
		identity=[]
		row=result[0]
		identity={'first_name':row[0],'last_name':row[1],'role':row[2],'dob':row[3],'batting_style':row[4],'bowling_style':row[5],'nationality':row[6],
		'full_name': row[0]+' '+row[1],'year':row[7],'day':row[8]}
		r=res2[0]
		odidata={'total_match':res4, 'run':r[0], 'balls':r[1], 'extras':r[2],'fours':r[3], 'six':r[4],'wicket':r[5],'maiden':r[6],'overs':r[7],'run_given':r[8],'bowled':int(bowled.getvalue()),'caught':int(caught.getvalue()), 'runout':int(runout.getvalue())}
		cursor=connection.cursor()
		bowled=cursor.var(cx_Oracle.NUMBER)
		caught = cursor.var(cx_Oracle.NUMBER)
		runout=cursor.var(cx_Oracle.NUMBER)
		cursor.callproc('FIELDING',[playerid,'T20',bowled,caught,runout])
		r=res3[0]
		t20data={'total_match':res5, 'run':r[0], 'balls':r[1], 'extras':r[2],'fours':r[3], 'six':r[4],'wicket':r[5],'maiden':r[6],'overs':r[7],'run_given':r[8],'bowled':int(bowled.getvalue()),'caught':int(caught.getvalue()), 'runout':int(runout.getvalue())}
		image=row[9]
		if image!=None:
			image=base64.b64encode(image.read()).decode()
		
		cursor=connection.cursor()

		sql="select team_name, trim(team_type) from team, plays_for where team.team_id=plays_for.team_id and trim(player_id)= trim(:playerid)"
		cursor.execute(sql,{'playerid':playerid})
		result=cursor.fetchall()
		cursor.close()

		teams=[]
		print(playerid)
		for r in result:
			x=r[1]
			if r[1]=="FRANCHISE":
				x="Club"
			row={'team_name':r[0], 'team_type':x}
			teams.append(row)
			print(r[0]+' '+r[1]+' '+'1')


		#row={'first_name':r[0][0], 'last_name':r[0][1],'role':r[0][2],'dob':r[0][3], 'batting_style':r[0][4] }
		#player.append(row)

	return render(request,'player-detail.html',{'identity':identity,'teams':teams,'image':image, 'odi':odidata, 't20':t20data})

def update_player_image(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		player_id=request.POST['player_id']
		image=request.FILES['image']
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="update player set image=:image where trim(player_id)=trim(:player_id)"
		cursor.execute(sql,{'player_id':player_id,'image':image.read()})
		cursor.close()
		connection.commit()
	players=[]
	cursor=get_cursor()
	sql="select first_name||' '||last_name, player_id from player"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	for r in result:
		players.append({'player_id':r[1],'player_name':r[0]})
	return render(request,'update_player_image.html',{'players':players})

def login(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']==True:
			return redirect(admin_update_home)

	
	if request.method=='POST':
		print('POSTED1')
		email=request.POST.get('email','dummy@dummy.co')
		password=request.POST.get('password','dummy')
		
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="SELECT trim(USERNAME) FROM ADMINS WHERE EMAIL_ID=:email AND HASHED_PASSWORD=ORA_HASH(:password)"
		cursor.execute(sql,{'email':email,'password':password})
		result=[]
		result=cursor.fetchall()
		cursor.close()

		if len(result)==1:
			request.session['username']=result[0][0]
			request.session['admin_logged']=True
			request.method=0
			messages.success(request,'Welcome '+str(result[0][0])+'!')
			return redirect(admin_update_home)
		else:
			messages.error(request,'Invalid login')
			return redirect('login')
	return render(request,'show_login.html')

def total_player():
	cursor=get_cursor()
	sql="select * from player"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def update(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		
		player_id=total_player()+1
		first_name=request.POST['first_name']
		last_name=request.POST['last_name']
		role=request.POST['role']
		dob=request.POST['dob']
		batting_style=request.POST['batting_style']
		bowling_style=request.POST['bowling_style']
		nationality=request.POST['nationality']

		image=request.FILES['image']
		print('..................................',type(image))
		#path = default_storage.save('tmp/somename', ContentFile(image.read()))
		#tmp_file = os.path.join(settings.MEDIA_ROOT, path)
		#image=tmp_file

		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		print(dob)

		sql="INSERT INTO PLAYER VALUES (:playerid, :first_name, :last_name, :role, to_date(:dob,'YYYY-MM-DD'), :batting_style, :bowling_style, :nationality,:image)"
		cursor.execute(sql,{'playerid':player_id,'first_name':first_name,'last_name':last_name,'role':role,'dob':dob, 'batting_style':batting_style,'bowling_style':bowling_style,'nationality':nationality,'image':image.read()})
		
		cursor.close()
		connection.commit()
		messages.success(request,"Done!")

		return render(request,'update.html')
	print('line3')
	return render(request,'update.html')

def get_all_teams():
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select team_id, team_name from team"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	dict_result=[]
	for r in result:
		row={'team_name': r[1], 'team_id': r[0]}
		dict_result.append(row)
	return dict_result;

def get_all_stadiums():
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select stadium_id, stadium_name from stadium"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	dict_result=[]
	for r in result:
		row={'stadium_name': r[1], 'stadium_id': r[0]}
		dict_result.append(row)
	return dict_result;

def get_teams_in_tournament(tournament_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	print('sdasd '+tournament_id)
	sql="select trim(team_id) from teams_and_tournament where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchall()
	cursor.close()
	print("hhhh "+str(len(result)))
	dict_result=[]
	for r in result:
		print(r[0])
		cursor=connection.cursor()
		sql="select team_name from team where trim(team_id)=:team_id"
		cursor.execute(sql,{'team_id':r[0]})
		name=cursor.fetchone()
		print(name[0])
		row={'team_id':r[0],'team_name':name[0]}
		dict_result.append(row)
		cursor.close()
	return dict_result


	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select team_name from team where trim(team_id)=trim(:team_id)"
	cursor.execute(sql,{'team_id':team_id})
	result=cursor.fetchone()
	cursor.close()
	return result[0].strip()

def total_match():
	cursor=get_cursor()
	sql="select * from match"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)


def add_match(request,tournament_id,tournament_name):
	
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	
	
	if request.method=='POST':
		first_team=request.POST.get("first_team",None)
		second_team=request.POST.get("second_team",None)
		match_id=total_match()+1
		stage=request.POST.get("stage")
		toss_won=request.POST.get("toss_won")
		choice=request.POST.get("choice")
		award_money=request.POST.get("award_money")
		match_date=request.POST.get("match_date")
		stadium_id=request.POST.get("stadium_id")

		
		if toss_won=="team_1" and choice=="fielding":
			first_team,second_team=second_team,first_team
		elif toss_won=="team_2" and choice=="batting":
			first_team,second_team=second_team,first_team

		print('first_team......................'+first_team)
		print('second_team......................'+second_team)



		request.session['match_id']=match_id
		request.session['first_team']=first_team
		request.session['second_team']=second_team
		request.session['match_id']=match_id
		request.session['toss_won']=toss_won
		request.session['choice']=choice


		batting_first=0
		bowling_first=0

		print(first_team)
		print(second_team)
		print(toss_won+".")
		print(choice+".")

		batting_first=find_team_name(first_team)
		bowling_first=find_team_name(second_team)

		request.session['batting_first']=batting_first
		request.session['bowling_first']=bowling_first



		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="select count(*) from match where trim(match_id)=:match_id"
		cursor.execute(sql,{'match_id':match_id})
		result=cursor.fetchone()
		cursor.close()
		print(result[0])

		if first_team==second_team:
			messages.error(request,"Both are same teams!")
		elif result[0]!=0:
			messages.error(request,"Match ID is not unique.")
		else:
			if True:
				dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
				connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
				cursor=connection.cursor()
				print('date '+match_date)
				if toss_won=='team_1':
					toss_won=first_team
				else:
					toss_won=second_team 
				
				sql="insert into match values(:match_id,:stage,0,NULL,:award_money,:tournament_id,to_date(:match_date,'YYYY-MM-DD'),:stadium_id,:toss_won,:choice,0)"
				cursor.execute(sql,{'match_id':match_id,'stage':stage,'award_money':award_money,'tournament_id':tournament_id,'match_date':match_date,'stadium_id':stadium_id,'toss_won':toss_won,'choice':choice})
				connection.commit()
				cursor.close()

				request.method=0
				context={}
				context['tournament_id']=tournament_id
				context['tournament_name']=tournament_name

				context['first_team']=first_team
				context['second_team']=second_team
				first_team_players=[]
				second_team_players=[]
				cursor=connection.cursor()
				sql1="select distinct player_id, (select first_name||' '||last_name from player where player.player_id=plays_for.player_id ) from plays_for where trim(team_id)= :first_team"
				sql2="select distinct player_id, (select first_name||' '||last_name from player where player.player_id=plays_for.player_id ) from plays_for where trim(team_id)= :second_team"
				cursor.execute(sql1,{'first_team':first_team})
				result1=cursor.fetchall()
				cursor.execute(sql2,{'second_team':second_team})
				result2=cursor.fetchall()
				cursor.close()

				
				
				px=0
				for r in result1:
					first_team_players.append({'player_id':r[0],'player_name':r[1].strip()})
					context['x'+str(px)]=r[1].strip()
					px+=1

				context['first_team_players']=first_team_players
				

				px=0
				for r in result2:
					second_team_players.append({'player_id':r[0],'player_name':r[1].strip()})
					context['y'+str(px)]=r[1].strip()
					px+=1

				context['second_team_players']=second_team_players
				
				request.session['con1']=context
				return render(request,'add_match_p2.html',context)
			else:
				messages.error(request,"Failed process...")

	print('re-got')
	dict_result=get_teams_in_tournament(tournament_id)
	return render(request,'add_match.html',{'teams':dict_result,'tournament_id':tournament_id,'tournament_name':tournament_name,'stadiums':get_all_stadiums()})

def add_to_squad(squad,squad_id,match_id,team_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="insert into squad values(:squad_id,:match_id,:team_id)"
	cursor.execute(sql,{'squad_id':squad_id,'match_id':match_id,'team_id':team_id})
	connection.commit()
	for player_id in squad:
		print(player_id+' '+'100')
		sql="insert into played (squad_id,player_id) values (:squad_id,:player_id)"
		cursor.execute(sql,{'squad_id':squad_id,'player_id':player_id})
		connection.commit()
	cursor.close()
	return

def find_player_name(player_id):
	if player_id==None:
		return player_id
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select first_name||' '||last_name from player where trim(player_id)=trim(:player_id)"
	cursor.execute(sql,{'player_id':player_id})
	result=cursor.fetchone()
	cursor.close()
	return result[0]

def total_squad():
	cursor=get_cursor()
	sql="select * from squad"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def hasAllDistinct(lst):
	st=set(lst)
	return len(st)==len(lst)



def add_match_p2(request,tournament_id,first_team="",second_team=""):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		print('ok')
		squad1_id=total_squad()+1
		squad2_id=squad1_id+1



		squad1=[]
		squad2=[]
		name1=[]
		name2=[]

		for i in range(0,11):
			player=request.POST.get("f"+ str(i))
			print(player)
			print(player+' '+find_player_name(player))
			name1.append({'player_id':player,'player_name':find_player_name(player)})
			squad1.append(player)

		for i in range(0,11):
			player=request.POST.get("s"+ str(i))
			print(player)
			name2.append({'player_id':player,'player_name':find_player_name(player)})
			squad2.append(player)

		match_id=request.session['match_id']
		if hasAllDistinct(squad1) and hasAllDistinct(squad2):
			add_to_squad(squad1,squad1_id,match_id,first_team)
			add_to_squad(squad2,squad2_id,match_id,second_team)
			print(match_id)
			request.session['squad1_id']=squad1_id
			request.session['squad2_id']=squad2_id
			request.session['squad1']=squad1
			request.session['squad2']=squad2
			request.session['name1']=name1
			request.session['name2']=name2
			
			context={}
			context['batting_first']=request.session['batting_first']
			context['bowling_first']=request.session['bowling_first']
			context['first_team']=request.session['first_team']
			context['second_team']=request.session['second_team']
			context['name1']=request.session['name1']
			context['name2']=request.session['name2']

			return render(request,'add_match_p3.html',context)
		else:
			print('failed')
			messages.error(request,"Failed, duplicate players!")
			return render(request,'add_match_p2.html',request.session['con1'])

	return render(request,'home.html')

def update_player_score(squad_id,player_id,runs,ball_faced,fours,sixes,balls,run_conceded,wickets,maidens,extra,bowled_by,runout_by,cought_by):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="update played set run_scored=:runs, ball_faced=:ball_faced, fours=:fours,sixes=:sixes,overs=:balls,run_conceded=:run_conceded,wickets=:wickets,maidens=:maidens,extras=:extra,bowled_player_id=:bowled_by,run_out_player_id=:runout_by,cought_player_id=:cought_by where trim(squad_id)=trim(:squad_id) and trim(player_id)=trim(:player_id)"
	cursor.execute(sql,{'squad_id':squad_id,'player_id':player_id,'runs':runs,'ball_faced':ball_faced,'fours':fours,'sixes':sixes,'balls':balls,'run_conceded':run_conceded,'wickets':wickets,'maidens':maidens,'extra':extra,'bowled_by':bowled_by,'runout_by':runout_by,'cought_by':cought_by})
	connection.commit()
	cursor.close()
	return
def set_washed_out(match_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="update match set is_nr=1 where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id})
	connection.commit()
	cursor.close()
def set_ended(match_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="update match set ended=1 where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id})
	connection.commit()
	cursor.close()
def set_motm(match_id,motm):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="update match set motm=:motm where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id,'motm':motm})
	connection.commit()
	cursor.close()


def add_match_p3(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		name1=request.session['name1']
		name2=request.session['name2']
		squad1_id=request.session['squad1_id']
		squad2_id=request.session['squad2_id']
		squad1=request.session['squad1']
		squad2=request.session['squad2']
		match_id=request.session['match_id']


		for player in squad1:
			runs=request.POST.get(player+'_runs')
			ball_faced=request.POST.get(player+'_ball_faced')
			fours=request.POST.get(player+'_4s')
			sixes=request.POST.get(player+'_6s')
			balls=request.POST.get(player+'_balls')
			wickets=request.POST.get(player+'_wickets')
			maidens=request.POST.get(player+'_maidens')
			run_conceded=request.POST.get(player+'_run_conceded')
			extra=request.POST.get(player+'_extra')
			bowled_by=request.POST.get(player+'_bowled_by')
			cought_by=request.POST.get(player+'_cought_by')
			runout_by=request.POST.get(player+'_runout_by')
			update_player_score(squad1_id,player,runs,ball_faced,fours,sixes,balls,run_conceded,wickets,maidens,extra,bowled_by,runout_by,cought_by)

		for player in squad2:
			runs=request.POST.get(player+'_runs')
			ball_faced=request.POST.get(player+'_ball_faced')
			fours=request.POST.get(player+'_4s')
			sixes=request.POST.get(player+'_6s')
			balls=request.POST.get(player+'_balls')
			wickets=request.POST.get(player+'_wickets')
			maidens=request.POST.get(player+'_maidens')
			run_conceded=request.POST.get(player+'_run_conceded')
			extra=request.POST.get(player+'_extra')
			bowled_by=request.POST.get(player+'_bowled_by')
			cought_by=request.POST.get(player+'_cought_by')
			runout_by=request.POST.get(player+'_runout_by')
			update_player_score(squad2_id,player,runs,ball_faced,fours,sixes,balls,run_conceded,wickets,maidens,extra,bowled_by,runout_by,cought_by)
		
		motm=request.POST.get('motm')
		washed_out=request.POST.get('washed_out')
		ended=request.POST.get('ended')
		
		if washed_out=='yes':
			set_washed_out(match_id)
		if ended=='yes':
			set_ended(match_id)
		set_motm(match_id,motm)
		return redirect('admin_update_home')

	return render(request,'home.html')
def admin_update_home(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	return render(request,'admin_update_home.html')

def logout(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	request.session['admin_logged']=False
	return render(request,'show_login.html')
def total_tournament():
	print("here")
	cursor=get_cursor()
	sql="select * from tournament"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)
def total_news():
	print("here")
	cursor=get_cursor()
	sql="select * from news"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def create_tournament(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		print('got')
		try:
			print("...............")
			tournament_id=total_tournament()+1
			print('tournament_id....'+str(tournament_id))
			tournament_name=request.POST.get("tournament_name")
			formatt=request.POST.get("format")
			system=request.POST.get("system")
			prize_money=request.POST.get("prize_money")
			point_w=request.POST.get("point_w")
			point_nr=request.POST.get("point_nr")
			award_money=request.POST.get("award_money")
			total_team=request.POST.get("total_team")
			dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
			connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
			cursor=connection.cursor()
			sql="insert into tournament values (:tournament_id,:tournament_name,:formatt,:system,:prize_money,:point_w,:point_nr,'',:award_money,:total_team,0)"
			cursor.execute(sql,{'tournament_id':tournament_id,'tournament_name':tournament_name,'formatt':formatt,'system':system,'prize_money':prize_money,'point_w':point_w,'point_nr':point_nr,'award_money':award_money,'total_team':total_team})
			cursor.close()
			connection.commit()
			context={}
			total_team=int(total_team)
			context['total_team']=total_team
			context['tournament_id']=tournament_id
			lst=[]
			for i in range(1,total_team+1):
				lst.append(str(i))
			context['lst']=lst;
			context['teams']=get_all_teams()
			print("yess")
			return render(request,'create_tournament_p2.html',context)
		except:
			messages.error(request,"Failed to create tournament.")

	return render(request,'create_tournament.html')

def add_to_TAT(cursor,tournament_id,team_id):
	try:
		sql="insert into teams_and_tournament values(:team_id,:tournament_id)"
		cursor.execute(sql,{'team_id':team_id,'tournament_id':tournament_id})
	except:
		raise exception()
	return

def create_tournament_p2(request,total_team,tournament_id):
	
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		try:
			dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
			connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
			cursor=connection.cursor()
			total_team=int(total_team)
			for i in range(1,total_team+1):
				team_id=request.POST.get(str(i))
				add_to_TAT(cursor,tournament_id,team_id)
			messages.success(request,'Successfully created tournament!')
			connection.commit()
			return redirect('admin_update_home')
		except:
			messages.error(request,"Failed process...")
			return redirect('admin_update_home')
	return redirect('create_tournament')



def edit_tournament(request,tournament_id,tournament_name):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	context={}
	context['tournament_id']=tournament_id
	context['tournament_name']=tournament_name
	request.session['tournament_id']=tournament_id
	request.session['tournament_name']=tournament_name
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select ended from tournament where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchone()
	shesh=False 
	if result[0]==1:
		shesh=True
	context['ended']=shesh
	return render(request,'edit_tournament.html',context)

def show_tournaments(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select tournament_id,tournament_name,format,ended from tournament order by tournament_name"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	tournaments=[]
	for r in result:
		shesh=False
		if r[3]==1:
			shesh=True
		tournaments.append({'tournament_id':r[0],'tournament_name':r[1],'format':r[2],'ended':shesh})

	return render(request,'show_tournaments.html',{'tournaments':tournaments})

def total_team():
	cursor=get_cursor()
	sql="select * from team"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def create_team(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':
		if True:
			team_id=total_team()+1
			team_name=request.POST.get('team_name')
			team_type=request.POST.get('team_type')
			dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
			connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
			sql="INSERT INTO TEAM VALUES (:team_id,:team_name,:team_type)"
			cursor=connection.cursor()
			cursor.execute(sql,{'team_id':team_id,'team_name':team_name,'team_type':team_type})
			cursor.close()
			connection.commit()
			messages.success(request,'Created new team!')
			return render(request,'admin_update_home.html')
		else:
			messages.error(request,'Failed')
			print('failed')
	return render(request,'create_team.html')
def total_manager():
	cursor=get_cursor()
	sql="select * from manager"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def add_manager(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	if request.method=='POST':

		manager_id=total_manager()+1
		first_name=request.POST.get('first_name')
		last_name=request.POST.get('last_name')
		dob=request.POST.get('dob')
		nationality=request.POST.get('nationality')

		print(manager_id)
		print(first_name)
		print(last_name)
		print(dob)
		print(nationality)

		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		sql="INSERT INTO MANAGER VALUES (:manager_id,:first_name,:last_name,to_date(:dob,'YYYY-MM-DD'),:nationality)"
		cursor=connection.cursor()
		cursor.execute(sql,{'manager_id':manager_id,'first_name':first_name,'last_name':last_name,'dob':dob,'nationality':nationality})
		cursor.close()
		connection.commit()
		messages.success(request,'Added new manager!')
		return render(request,'admin_update_home.html')
		#
	return render(request,'add_manager.html')

def total_contract():
	cursor=get_cursor()
	sql="select * from contract"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def new_player_contract(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	

	if request.method=='POST':
		if True:
			contract_id=total_contract()+1
			contract_length=request.POST.get('contract_length')
			salary=request.POST.get('salary')
			player_id=request.POST.get('player_id')
			team_id=request.POST.get('team_id')
			signing_date=request.POST.get('signing_date')
				
			sql="INSERT INTO CONTRACT VALUES (:contract_id,:contract_length,:salary) "
			cursor=connection.cursor()
			cursor.execute(sql,{'contract_id':contract_id,'contract_length':contract_length,'salary':salary})
			cursor.close()
			connection.commit()
			print(signing_date)

			sql="INSERT INTO plays_for VALUES (:contract_id,:team_id,:player_id,to_date(:signing_date,'YYYY-MM-DD'))"
			cursor=connection.cursor()
			cursor.execute(sql,{'contract_id':contract_id,'team_id':team_id,'player_id':player_id,'signing_date':signing_date})
			cursor.close()
			connection.commit()
			messages.success(request,"Successfully added contract!")
			return redirect(new_player_contract)
		else:
			messages.error(request,'Failed to create contract.')
			return render(request,'new_player_contract.html')


	sql="select first_name||' '||last_name, player_id from player"
	cursor=connection.cursor()
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	players=[]
	for r in result:
		players.append({'player_name':r[0],'player_id':r[1]})

	sql="select team_name, team_id from team"
	cursor=connection.cursor()
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	teams=[]
	for r in result:
		teams.append({'team_name':r[0],'team_id':r[1]})

	return render(request,'new_player_contract.html',{'players':players,'teams':teams})

def new_manager_contract(request):

	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)

	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	

	if request.method=='POST':
		if True:
			contract_id=total_contract()+1
			contract_length=request.POST.get('contract_length')
			salary=request.POST.get('salary')
			manager_id=request.POST.get('manager_id')
			team_id=request.POST.get('team_id')
			signing_date=request.POST.get('signing_date')
				
			sql="INSERT INTO CONTRACT VALUES (:contract_id,:contract_length,:salary) "
			cursor=connection.cursor()
			cursor.execute(sql,{'contract_id':contract_id,'contract_length':contract_length,'salary':salary})
			cursor.close()
			connection.commit()
			print(signing_date)
			print('....................'+manager_id)

			sql="INSERT INTO manages VALUES (:contract_id,:team_id,:manager_id,to_date(:signing_date,'YYYY-MM-DD'))"
			cursor=connection.cursor()
			cursor.execute(sql,{'contract_id':contract_id,'team_id':team_id,'manager_id':manager_id,'signing_date':signing_date})
			cursor.close()
			connection.commit()
			messages.success(request,"Successfully added contract!")
			return redirect(new_manager_contract)
		else:
			messages.error(request,'Failed to create contract.')
			return render(request,'new_manager_contract.html')


	sql="select first_name||' '||last_name, manager_id from manager"
	cursor=connection.cursor()
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	managers=[]
	for r in result:
		managers.append({'manager_name':r[0],'manager_id':r[1]})
		print('ID '+ r[1])

	sql="select team_name, team_id from team"
	cursor=connection.cursor()
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	teams=[]
	for r in result:
		teams.append({'team_name':r[0],'team_id':r[1]})

	return render(request,'new_manager_contract.html',{'managers':managers,'teams':teams})

def teams_from_match(match_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select squad_id from squad where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id})
	result=cursor.fetchall()
	teams=[]
	for r in result:
		team_id=cursor.var(cx_Oracle.STRING)
		team_name=cursor.var(cx_Oracle.STRING)
		cursor.callproc('team_from_squad',[r[0],team_id,team_name])
		teams.append({'team_id':team_id.getvalue().strip(),'team_name':team_name.getvalue().strip()})
	cursor.close()
	return teams
def find_match_date(match_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select to_char(match_date,'DD-MM-YYYY') from match where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id})
	result=cursor.fetchone()
	cursor.close()
	return result[0]

def show_matches(request,tournament_id):
	print('Get it here...................................................................')
	print(tournament_id)
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select * from match where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchall()
	cursor.close()
	matches=[]
	print("tournament: "+tournament_id)
	for r in result:
		print('..................')
		teams=teams_from_match(r[0])
		print(str(len(teams)))
		shesh=False
		if r[10]==1:
			shesh=True
		print(shesh)
		date=find_match_date(r[0])
		matches.append({'match_id':r[0],'stage':r[1],'washed_out':r[2],'ended':shesh,'first_team':teams[0].get('team_id').strip(), 'first_team_name':teams[0].get('team_name').strip(), 'second_team':teams[1].get('team_id').strip(),'second_team_name':teams[1].get('team_name').strip(),'date':date })
	context={}
	context['matches']=matches
	request.session['tournament_id']=tournament_id
	return render(request,'show_matches.html',context)


def find_tournament_name(tournament_id):
	cursor=get_cursor()
	sql="select tournament_name from tournament where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchone()
	return result[0].strip()
def find_tournament_format(tournament_id):
	cursor=get_cursor()
	sql="select format from tournament where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchone()
	return result[0].strip()
def find_stadium_name(stadium_id):
	cursor=get_cursor()
	sql="select stadium_name from stadium where trim(stadium_id)=trim(:stadium_id)"
	cursor.execute(sql,{'stadium_id':stadium_id})
	result=cursor.fetchone()
	return result[0].strip()


def get_all_info_from_match(match_id):
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()

	#getting squad_ids
	sql="select squad_id from squad where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id})
	result=cursor.fetchall()
	squad1_id=result[0][0]
	squad2_id=result[1][0]
	#getting match infos
	sql="select * from match where trim(match_id)=trim(:match_id)"
	cursor.execute(sql,{'match_id':match_id})
	r=cursor.fetchone()

	#returning
	shesh=False
	if r[10]==1:
		shesh=True
	print(shesh)

	match={'stage':r[1],'washed_out':r[2],'motm':r[3],'award_money':r[4],'tournament_id':r[5],'tournament_name':find_tournament_name(r[5]),'match_date':r[6],'stadium_id':r[7],'stadium_name':find_stadium_name(r[7]),'toss_won':r[8],'choice':r[9],'ended':shesh,'squad1_id':squad1_id,'squad2_id':squad2_id}
	return match

def not_out(a,b,c):
	return a==None and b==None and c==None

def get_squad(squad_id):
	cursor=get_cursor()
	sql="select * from played where trim(squad_id)=trim(:squad_id)"
	cursor.execute(sql,{'squad_id':squad_id})
	result=cursor.fetchall()
	name=[]
	for r in result:
		name.append({'player_id':r[1].strip(),'player_name':find_player_name(r[1]),'run_scored':r[2],'ball_faced':r[3],'fours':r[4],'sixes':r[5],'overs':int(r[6]),'run_conceded':r[7],'wickets':r[8],'maidens':r[9],'extra':r[10],'bowled_by':find_player_name(r[11]),'cought_by':find_player_name(r[12]),'runout_by':find_player_name(r[13]),'not_out':not_out(r[11],r[12],r[13])})
	return name


def edit_match(request,match_id):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	match=get_all_info_from_match(match_id)
	squad1_id=match.get('squad1_id')
	squad2_id=match.get('squad2_id')
	name1=get_squad(squad1_id)
	name2=get_squad(squad2_id)
	squad1=[]
	squad2=[]
	for player in name1:
		squad1.append(player.get('player_id'))
	for player in name2:
		squad2.append(player.get('player_id'))
	
	teams=teams_from_match(match_id)
	
	context={}
	context['toss_won']=match.get('toss_won').strip()
	context['choice']=match.get('choice').strip()
	if context['toss_won']==teams[0].get('team_id'):
		if context['choice']=='batting':
			batting_first=teams[0].get('team_name')
			bowling_first=teams[1].get('team_name')
		else:
			bowling_first=teams[0].get('team_name')
			batting_first=teams[1].get('team_name')
	else:
		if context['choice']=='batting':
			bowling_first=teams[0].get('team_name')
			batting_first=teams[1].get('team_name')
		else:
			batting_first=teams[0].get('team_name')
			bowling_first=teams[1].get('team_name')
	batting_first=batting_first.strip()
	bowling_first=bowling_first.strip()

	if batting_first != find_team_name(whose_squad(squad1_id)):
		squad1_id,squad2_id=squad2_id,squad1_id
		name1,name2=name2,name1
		squad1,squad2=squad2,squad1
	
	print('toss.................')
	print(batting_first)
	print(bowling_first)
	context['batting_first']=batting_first
	context['bowling_first']=bowling_first

	request.session['match_id']=match_id
	request.session['name1']=name1
	request.session['name2']=name2
	request.session['squad1_id']=squad1_id
	request.session['squad2_id']=squad2_id
	request.session['squad1']=squad1
	request.session['squad2']=squad2

	
	context['match_id']=match_id
	context['name1']=name1
	context['name2']=name2
	context['squad1_id']=squad1_id
	context['squad2_id']=squad2_id
	context['squad1']=squad1
	context['squad2']=squad2
	context['stage']=match.get('stage')
	context['first_team']=teams[0].get('team_id')
	context['second_team']=teams[1].get('team_id')
	

	if request.method=='POST':
		
		name1=request.session['name1']
		name2=request.session['name2']
		squad1_id=request.session['squad1_id']
		squad2_id=request.session['squad2_id']
		squad1=request.session['squad1']
		squad2=request.session['squad2']
		match_id=request.session['match_id']

		print('came here......................................')
		print(match_id)
		for p in name1:
			print(p)
			print(type(p))
			print(p.get('player_name'))
			print(p.get('player_id'))


		for p in name1:
			player=p.get('player_id')
			player=player.strip()
			runs=request.POST.get(player+'_runs')
			runs2=request.POST.get(player+' _runs')
			print(player+' runs '+str(runs)+' '+str(runs2))
			ball_faced=request.POST.get(player+'_ball_faced')
			fours=request.POST.get(player+'_4s')
			sixes=request.POST.get(player+'_6s')
			balls=request.POST.get(player+'_balls')
			wickets=request.POST.get(player+'_wickets')
			maidens=request.POST.get(player+'_maidens')
			run_conceded=request.POST.get(player+'_run_conceded')
			extra=request.POST.get(player+'_extra')
			bowled_by=request.POST.get(player+'_bowled_by')
			cought_by=request.POST.get(player+'_cought_by')
			runout_by=request.POST.get(player+'_runout_by')
			update_player_score(squad1_id,player,runs,ball_faced,fours,sixes,balls,run_conceded,wickets,maidens,extra,bowled_by,runout_by,cought_by)

		for p in name2:
			player=p.get('player_id')
			player=player.strip()
			runs=request.POST.get(player+'_runs')
			runs2=request.POST.get(player+' _runs')
			print(player+' runs '+str(runs)+' '+str(runs2))
			ball_faced=request.POST.get(player+'_ball_faced')
			fours=request.POST.get(player+'_4s')
			sixes=request.POST.get(player+'_6s')
			balls=request.POST.get(player+'_balls')
			wickets=request.POST.get(player+'_wickets')
			maidens=request.POST.get(player+'_maidens')
			run_conceded=request.POST.get(player+'_run_conceded')
			extra=request.POST.get(player+'_extra')
			bowled_by=request.POST.get(player+'_bowled_by')
			cought_by=request.POST.get(player+'_cought_by')
			runout_by=request.POST.get(player+'_runout_by')
			update_player_score(squad2_id,player,runs,ball_faced,fours,sixes,balls,run_conceded,wickets,maidens,extra,bowled_by,runout_by,cought_by)
		
		motm=request.POST.get('motm')
		washed_out=request.POST.get('washed_out')
		ended=request.POST.get('ended')
		print(ended)
		if washed_out=='yes':
			set_washed_out(match_id)
			set_ended(match_id)
		if ended=='yes':
			set_ended(match_id)
			print('in......')
		set_motm(match_id,motm)

		tournament_id=request.session['tournament_id']

		return show_matches(request,tournament_id)

	return render(request,'edit_match.html',context)
def whose_squad(squad_id):
	cursor=get_cursor()
	team_id=cursor.var(cx_Oracle.STRING)
	team_name=cursor.var(cx_Oracle.STRING)
	cursor.callproc('team_from_squad',[squad_id,team_id,team_name])
	cursor.close()
	return team_id.getvalue()
def get_squad_score(squad_id):
	cursor=get_cursor()
	total_run=cursor.var(cx_Oracle.NUMBER)
	total_wicket=cursor.var(cx_Oracle.NUMBER)
	total_ball=cursor.var(cx_Oracle.NUMBER)
	total_four=cursor.var(cx_Oracle.NUMBER)
	total_six=cursor.var(cx_Oracle.NUMBER)
	total_extra=cursor.var(cx_Oracle.NUMBER)
	cursor.callproc('get_squad_score',[squad_id,total_run,total_wicket,total_ball,total_four,total_six,total_extra])
	return {'total_run':int(total_run.getvalue()),'total_wicket':int(total_wicket.getvalue()),'total_ball':int(total_ball.getvalue()),'total_four':int(total_four.getvalue()),'total_six':int(total_six.getvalue()),'total_extra':int(total_extra.getvalue())}

def view_match(request,match_id):
	match=get_all_info_from_match(match_id)
	squad1_id=match.get('squad1_id')
	squad2_id=match.get('squad2_id')
	name1=get_squad(squad1_id)
	name2=get_squad(squad2_id)
	squad1=[]
	squad2=[]
	for player in name1:
		squad1.append(player.get('player_id'))
	for player in name2:
		squad2.append(player.get('player_id'))

	context={}
	
	teams=teams_from_match(match_id)
	context['toss_won']=match.get('toss_won').strip()
	context['choice']=match.get('choice').strip()
	ts=0;
	ts=find_team_name(context['toss_won'])

	if context['toss_won']==teams[0].get('team_id'):
		if context['choice']=='batting':
			batting_first=teams[0].get('team_name')
			bowling_first=teams[1].get('team_name')
		else:
			bowling_first=teams[0].get('team_name')
			batting_first=teams[1].get('team_name')
	else:
		if context['choice']=='batting':
			bowling_first=teams[0].get('team_name')
			batting_first=teams[1].get('team_name')
		else:
			batting_first=teams[0].get('team_name')
			bowling_first=teams[1].get('team_name')

	batting_first=batting_first.strip()
	bowling_first=bowling_first.strip()
	print('...................................................................X')
	print(batting_first)
	print(bowling_first)
	print(context['toss_won']+'X')
	print(context['choice']+'X')

	if batting_first != find_team_name(whose_squad(squad1_id)):
		squad1_id,squad2_id=squad2_id,squad1_id
		name1,name2=name2,name1
		squad1,squad2=squad2,squad1
	squad1_score=get_squad_score(squad1_id)
	squad2_score=get_squad_score(squad2_id)
	context['match_id']=match_id
	context['name1']=name1
	context['name2']=name2
	context['squad1_id']=squad1_id
	context['squad2_id']=squad2_id
	context['squad1']=squad1
	context['squad2']=squad2
	context['stage']=match.get('stage')
	context['toss_won']=match.get('toss_won')
	context['choice']=match.get('choice')
	context['batting_first']=batting_first
	context['bowling_first']=bowling_first
	context['first_team']=teams[0].get('team_id')
	context['second_team']=teams[1].get('team_id')
	context['washed_out']=match.get('washed_out')
	context['ended']=match.get('ended')
	context['motm']=find_player_name(match.get('motm'))
	context['squad1_score']=squad1_score
	context['squad2_score']=squad2_score
	context['stadium_name']=match.get('stadium_name')
	context['tournament_name']=match.get('tournament_name')
	context['match_date']=find_match_date(match_id)
	context['format']=find_tournament_format(match.get('tournament_id'))

	if match.get('ended')==1:
		if squad1_score.get('total_run')>squad2_score.get('total_run'):
			result=find_team_name(whose_squad(squad1_id))+" won"
		elif squad1_score.get('total_run')<squad2_score.get('total_run'):
			result=find_team_name(whose_squad(squad2_id))+" won"
		else:
			result="Match tied"
	else:
		result="Match still running"
		context['motm']='-'
	context['result']=result
	context['ts']=ts;


	return render(request,'view_match.html',context)
def players_in_tournament(tournament_id):
	cursor=get_cursor()
	sql="select distinct player_id, (select first_name||' '||last_name from player where trim(player.player_id)=trim(plays_for.player_id)) from plays_for where team_id in (select team_id from teams_and_tournament where trim(tournament_id)=trim(:tournament_id))"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchall()
	name=[]
	for r in result:
		name.append({'player_id':r[0],'player_name':r[1]})
	cursor.close()
	return name
def update_mott(request,tournament_id):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	if request.method=='POST':
		mott=request.POST['mott']
		print('mott '+mott+'................................................')
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="update tournament set mott=:mott where trim(tournament_id)=trim(:tournament_id)"
		cursor.execute(sql,{'mott':mott,'tournament_id':tournament_id})
		connection.commit()
		cursor.close()
		messages.success(request,"Updated Man of the tournament!")
		return redirect('admin_update_home')
	name=players_in_tournament(tournament_id)
	print('..................................'+tournament_id)
	for r in name:
		print(r.get('player_name'))
	return render(request,'update_mott.html',{'name':name,'tournament_id':tournament_id})

def end_tournament(request,tournament_id):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	cursor=get_cursor()
	can_be_ended=cursor.callfunc("can_be_ended",int,[tournament_id])
	if can_be_ended==1:
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="update tournament set ended=1 where trim(tournament_id)=trim(:tournament_id)"
		cursor.execute(sql,{'tournament_id':tournament_id})
		connection.commit()
		cursor.close()
		messages.success(request,"Marked ended!")
		return redirect('admin_update_home')
	else:
		messages.error(request,"Tournament cannot be ended now")
		return edit_tournament(request,request.session['tournament_id'],request.session['tournament_name'])
def total_location():
	print("here")
	cursor=get_cursor()
	sql="select * from location"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)

def add_location(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	if request.method=='POST':
		location_id=total_location()+1
		country=request.POST['country']
		city=request.POST['city']
		road=request.POST['road']
		avenue=request.POST['avenue']
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="insert into location values(:location_id,:country,:city,:road,:avenue)"
		cursor.execute(sql,{'location_id':location_id,'country':country,'city':city,'road':road,'avenue':avenue})
		connection.commit()
		cursor.close()
		messages.success(request,"Successfully added location!")
	return render(request,'add_location.html')
def total_stadium():
	cursor=get_cursor()
	sql="select * from stadium"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	return len(result)
def add_stadium(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	if request.method=='POST':
		
		stadium_id=total_stadium()+1
		stadium_name=request.POST['stadium_name']
		capacity=request.POST['capacity']
		location_id=request.POST['location_id']

		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		sql="insert into stadium values(:stadium_id,:stadium_name,:capacity,:location_id)"
		cursor.execute(sql,{'stadium_id':stadium_id,'stadium_name':stadium_name,'capacity':capacity,'location_id':location_id,})
		connection.commit()
		cursor.close()
		messages.success(request,"Successfully added stadium!")
	
	
	cursor=get_cursor()
	sql="select avenue||', '||road_no||', '||city||', '||country , location_id from location"
	cursor.execute(sql)
	result=cursor.fetchall()
	locations=[]
	for r in result:
		locations.append({'place':r[0],'location_id':r[1]})

	return render(request,'add_stadium.html',{'locations':locations})

def recent_matches(request):

	cursor=get_cursor()
	sql="select match_id, tournament_id, ended, to_char(match_date,'DD-Mon-YYYY'), (select tournament_name from tournament t where t.tournament_id=a.tournament_id) from match a order by match_date desc"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	matches=[]
	for r in result:
		shesh=False
		if r[2]==1:
			shesh=True
		teams=teams_from_match(r[0])
		matches.append({'match_id':r[0],'tournament_id':r[1],'ended':shesh,'date':r[3],'first_team':teams[0].get('team_id').strip,
			'second_team':teams[1].get('team_id').strip, 'first_team_name':teams[0].get('team_name').strip(),
			'second_team_name':teams[1].get('team_name').strip(),'tournament_name':r[4]})

	return render(request,'recent_matches.html',{'matches':matches})

def show_series(request):

	cursor=get_cursor()
	sql="select * from tournament order by tournament_id desc"
	cursor.execute(sql)
	result=cursor.fetchall()
	cursor.close()
	tournaments=[]
	for r in result:
		shesh=False
		if r[10]==1:
			shesh=True
		tournaments.append({'tournament_id':r[0],'tournament_name':r[1],'format':r[2],'ended':shesh})


	return render(request,'show_series.html',{'tournaments':tournaments})
def user_view_tournament(request,tournament_id,tournament_name):
	context={}
	context['tournament_id']=tournament_id
	context['tournament_name']=tournament_name
	request.session['tournament_id']=tournament_id
	request.session['tournament_name']=tournament_name
	return render(request,'user_view_tournament.html',context)
def user_show_matches(request,tournament_id):
	print('Get it here...................................................................')
	print(tournament_id)
	dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
	connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
	cursor=connection.cursor()
	sql="select * from match where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchall()
	cursor.close()
	matches=[]
	for r in result:
		print('..................'+r[0])
		teams=teams_from_match(r[0])
		shesh=False
		if r[10]==1:
			shesh=True
		print(shesh)
		date=find_match_date(r[0])
		matches.append({'match_id':r[0],'stage':r[1],'washed_out':r[2],'ended':shesh,'first_team':teams[0].get('team_id').strip(), 'first_team_name':teams[0].get('team_name').strip(), 'second_team':teams[1].get('team_id').strip(),'second_team_name':teams[1].get('team_name').strip(),'date':date })
	context={}
	context['matches']=matches
	return render(request,'user_show_matches.html',context)
def matches_in_tournament(tournament_id):
	cursor=get_cursor()
	sql="select match_id from match where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchall()
	matches=[]
	for r in result:
		matches.append(r[0].strip())
	return matches

def user_point_table(request,tournament_id):
	cursor=get_cursor()
	sql="select point_w, point_nr from tournament where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	result=cursor.fetchone()
	point_w=int(result[0])
	point_nr=int(result[1])
	teams=get_teams_in_tournament(tournament_id)
	point_table={}
	win={}
	lose={}
	draw={}
	points={}

	for team in teams:
		name=team.get('team_name')
		print('Alllxxxxxxxxx'+name)
		point_table[name]=0
		win[name]=0
		lose[name]=0
		draw[name]=0
		points[name]=0

	matches=matches_in_tournament(tournament_id)
	for match_id in matches:
		match=get_all_info_from_match(match_id)
		squad1_id=match.get('squad1_id')
		squad2_id=match.get('squad2_id')
		name1=get_squad(squad1_id)
		name2=get_squad(squad2_id)
		squad1=[]
		squad2=[]
		for player in name1:
			squad1.append(player.get('player_id'))
		for player in name2:
			squad2.append(player.get('player_id'))
		
		teams=teams_from_match(match_id)
		context={}
		context['toss_won']=match.get('toss_won').strip()
		context['choice']=match.get('choice').strip()
		ts=0;
		ts=find_team_name(context['toss_won'])

		if context['toss_won']==teams[0].get('team_id'):
			if context['choice']=='batting':
				batting_first=teams[0].get('team_name')
				bowling_first=teams[1].get('team_name')
			else:
				bowling_first=teams[0].get('team_name')
				batting_first=teams[1].get('team_name')
		else:
			if context['choice']=='batting':
				bowling_first=teams[0].get('team_name')
				batting_first=teams[1].get('team_name')
			else:
				batting_first=teams[0].get('team_name')
				bowling_first=teams[1].get('team_name')

		batting_first=batting_first.strip()
		bowling_first=bowling_first.strip()

		if batting_first != find_team_name(whose_squad(squad1_id)):
			squad1_id,squad2_id=squad2_id,squad1_id
			name1,name2=name2,name1
			squad1,squad2=squad2,squad1
		squad1_score=get_squad_score(squad1_id)
		squad2_score=get_squad_score(squad2_id)
		if match.get('ended')==1:
			if squad1_score.get('total_run')>squad2_score.get('total_run'):
				win[find_team_name(whose_squad(squad1_id))]+=1
				lose[find_team_name(whose_squad(squad2_id))]+=1
			elif squad1_score.get('total_run')<squad2_score.get('total_run'):
				lose[find_team_name(whose_squad(squad1_id))]+=1
				win[find_team_name(whose_squad(squad2_id))]+=1
			else:
				draw[find_team_name(whose_squad(squad1_id))]+=1
				draw[find_team_name(whose_squad(squad2_id))]+=1
		else:
			result="Match still running"

	full=[]
	for team in teams:
		name=team.get('team_name')
		print('team_name=........'+name)
		point_table[name]+=point_w*win[name]
		point_table[name]+=point_nr*draw[name]
		points[name]=point_table[name]

	point_table=sorted(point_table.items(), key=lambda x: x[1], reverse=True)

	for team in point_table:
		name=team[0]
		print(name+'........')
		print(points[name])
		full.append({'team_name':name,'win':win[name],'lose':lose[name],'draw':draw[name],'played':win[name]+lose[name]+draw[name],'points':points[name]})

	return render(request,'user_point_table.html',{'full':full})

def top_scorers(tournament_id):
	cursor=get_cursor()
	teams=get_teams_in_tournament(tournament_id)

	runs={}
	wickets={}
	boundaries={}


	matches=matches_in_tournament(tournament_id)


	for match_id in matches:
		match=get_all_info_from_match(match_id)
		squad1_id=match.get('squad1_id')
		squad2_id=match.get('squad2_id')
		sql="select * from played where trim(squad_id)=trim(:squad1_id) or trim(squad_id)=trim(:squad2_id)"
		cursor.execute(sql,{'squad1_id':squad1_id,'squad2_id':squad2_id})
		result=cursor.fetchall()
		for r in result:
			if r[1].strip() not in runs:
				runs[r[1].strip()]=0
			if r[1].strip() not in wickets:
				wickets[r[1].strip()]=0
			if r[1].strip() not in boundaries:
				boundaries[r[1].strip()]=0
			runs[r[1].strip()]+=r[2]
			wickets[r[1].strip()]+=r[8]
			boundaries[r[1].strip()]+=r[4]+r[5]
		
	full_r=[]
	full_w=[]
	full_b=[]

	runs=sorted(runs.items(), key=lambda x: x[1], reverse=True)
	wickets=sorted(wickets.items(), key=lambda x: x[1], reverse=True)
	boundaries=sorted(boundaries.items(), key=lambda x: x[1], reverse=True)

	p=0
	for r in runs:
		if p<5 and r[1]>0:
			name=r[0]
			full_r.append({'name':find_player_name(name),'runs':r[1]})
			p+=1
	p=0
	for r in wickets:
		if p<5 and r[1]>0:
			name=r[0]
			print('got -> '+r[0]+' '+str(r[1]))
			full_w.append({'name':find_player_name(name),'wickets':r[1]})
			p+=1
	p=0
	for r in boundaries:
		if p<5 and r[1]>0:
			name=r[0]
			full_b.append({'name':find_player_name(name),'boundaries':r[1]})
			p+=1
	return full_r,full_w,full_b

	
def user_tournament_details(request,tournament_id):
	cursor=get_cursor()
	sql="select * from tournament where trim(tournament_id)=trim(:tournament_id)"
	cursor.execute(sql,{'tournament_id':tournament_id})
	r=cursor.fetchone()
	name=r[1]
	format_=r[2]
	prize_money=r[4]
	mott=r[7]
	award_money=r[8]
	teams=get_teams_in_tournament(tournament_id)
	ended=r[10]

	if ended==1:
		ended=True
	else:
		ended=False
	if mott:
		mott=find_player_name(mott)

	full_r,full_w,full_b=top_scorers(tournament_id)

	for r in full_w:
		print(r.get('name')+' '+str(r.get('wickets'))+' '+'x')

	return render(request,'user_tournament_details.html',locals())

def add_news(request):
	if 'admin_logged' in request.session:
		if request.session['admin_logged']!=True:
			return redirect(login)
	else:
		return redirect(login)
	if request.method=='POST':
		date=request.POST.get('date')
		time=request.POST.get('time')
		title=request.POST.get('title')
		details=request.POST.get('details')
		image=request.FILES['image']
		date=date+' '+time
		print(date)
		print(time)
		print(title)
		print(details)
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)
		cursor=connection.cursor()
		news_id=total_news()+1
		sql="insert into news values(:news_id,:image,to_date(:news_date,'YYYY-MM-DD HH24:MI'),:title,:details)"
		cursor.execute(sql,{'news_id':news_id,'title':title,'image':image.read(),'details':details,'news_date':date})
		connection.commit()
		messages.success(request,'Added News Successfully!')
	return render(request,'add_news.html')
def top(request):
	return render(request,'top.html')
def view_news(request,news_id):
	print('gooot')
	cursor=get_cursor()
	sql="select * from news where trim(news_id)=trim(:news_id)"
	cursor.execute(sql,{'news_id':news_id})
	result=cursor.fetchone()
	news_id=result[0]
	image=result[1]
	news_date=result[2]
	title=result[3]
	details=result[4]
	if image!=None:
		image=base64.b64encode(image.read()).decode()
	return render(request,'view_news.html',locals())

def user_view_teams(request):
	cursor=get_cursor()
	sql="select * from team"
	cursor.execute(sql)
	result=cursor.fetchall()
	teams=[]
	for r in result:
		teams.append({'team_id':r[0],'team_name':r[1],'team_type':r[2]})
	return render(request,'user_view_teams.html',{'teams':teams})

def find_team_name(team_id):
	cursor=get_cursor()
	sql="select trim(team_name) from team where trim(team_id)=trim(:team_id)"
	cursor.execute(sql,{'team_id':team_id})
	result=cursor.fetchone()[0]
	return result

def odi_info(team_id):
	cursor=get_cursor()
	t_name=find_team_name(team_id)
	print('..............................')
	print('..............................')
	print('team_name= '+t_name)
	win={}
	lose={}
	draw={}
	teams=get_all_teams()
	for team in teams:
		name=team.get('team_name')
		print('Alllxxxxxxxxx'+name)
		win[name]=0
		lose[name]=0
		draw[name]=0

	sql="select trim(match_id) from match where (select trim(format) from tournament where match.tournament_id=tournament.tournament_id)='ODI'"
	cursor.execute(sql)
	result=cursor.fetchall()
	matches=[]
	for r in result:
		matches.append(r[0])

	print('done')

	for match_id in matches:
		match=get_all_info_from_match(match_id)
		if match.get('ended')==1:
			print('start')
			squad1_id=match.get('squad1_id')
			squad2_id=match.get('squad2_id')
			name1=get_squad(squad1_id)
			name2=get_squad(squad2_id)
			squad1=[]
			squad2=[]
			for player in name1:
				squad1.append(player.get('player_id'))
			for player in name2:
				squad2.append(player.get('player_id'))
			
			teams=teams_from_match(match_id)
			context={}
			context['toss_won']=match.get('toss_won').strip()
			context['choice']=match.get('choice').strip()
			ts=0;
			ts=find_team_name(context['toss_won'])

			if context['toss_won']==teams[0].get('team_id'):
				if context['choice']=='batting':
					batting_first=teams[0].get('team_name')
					bowling_first=teams[1].get('team_name')
				else:
					bowling_first=teams[0].get('team_name')
					batting_first=teams[1].get('team_name')
			else:
				if context['choice']=='batting':
					bowling_first=teams[0].get('team_name')
					batting_first=teams[1].get('team_name')
				else:
					batting_first=teams[0].get('team_name')
					bowling_first=teams[1].get('team_name')

			batting_first=batting_first.strip()
			bowling_first=bowling_first.strip()

			print(batting_first+' vs '+bowling_first)

			if batting_first != find_team_name(whose_squad(squad1_id)):
				squad1_id,squad2_id=squad2_id,squad1_id
				name1,name2=name2,name1
				squad1,squad2=squad2,squad1
			squad1_score=get_squad_score(squad1_id)
			squad2_score=get_squad_score(squad2_id)
			if match.get('ended')==1:
				if squad1_score.get('total_run')>squad2_score.get('total_run'):
					win[find_team_name(whose_squad(squad1_id))]+=1
					lose[find_team_name(whose_squad(squad2_id))]+=1
					print('won = '+find_team_name(whose_squad(squad1_id))+' '+t_name+' '+str(win[t_name]))
				elif squad1_score.get('total_run')<squad2_score.get('total_run'):
					lose[find_team_name(whose_squad(squad1_id))]+=1
					win[find_team_name(whose_squad(squad2_id))]+=1
					print('won = '+find_team_name(whose_squad(squad2_id))+' '+t_name+' '+str(win[t_name]))
				else:
					draw[find_team_name(whose_squad(squad1_id))]+=1
					draw[find_team_name(whose_squad(squad2_id))]+=1
			else:
				result="Match still running"

	return win[t_name], lose[t_name], draw[t_name]

def t20_info(team_id):
	cursor=get_cursor()
	t_name=find_team_name(team_id)
	print('..............................')
	print('..............................')
	print('team_name= '+t_name)
	win={}
	lose={}
	draw={}
	teams=get_all_teams()
	for team in teams:
		name=team.get('team_name')
		print('Alllxxxxxxxxx'+name)
		win[name]=0
		lose[name]=0
		draw[name]=0

	sql="select trim(match_id) from match where (select trim(format) from tournament where match.tournament_id=tournament.tournament_id)='T20'"
	cursor.execute(sql)
	result=cursor.fetchall()
	matches=[]
	for r in result:
		matches.append(r[0])

	print('done')

	for match_id in matches:
		match=get_all_info_from_match(match_id)
		if match.get('ended')==1:
			print('start')
			squad1_id=match.get('squad1_id')
			squad2_id=match.get('squad2_id')
			name1=get_squad(squad1_id)
			name2=get_squad(squad2_id)
			squad1=[]
			squad2=[]
			for player in name1:
				squad1.append(player.get('player_id'))
			for player in name2:
				squad2.append(player.get('player_id'))
			
			teams=teams_from_match(match_id)
			context={}
			context['toss_won']=match.get('toss_won').strip()
			context['choice']=match.get('choice').strip()
			ts=0;
			ts=find_team_name(context['toss_won'])

			if context['toss_won']==teams[0].get('team_id'):
				if context['choice']=='batting':
					batting_first=teams[0].get('team_name')
					bowling_first=teams[1].get('team_name')
				else:
					bowling_first=teams[0].get('team_name')
					batting_first=teams[1].get('team_name')
			else:
				if context['choice']=='batting':
					bowling_first=teams[0].get('team_name')
					batting_first=teams[1].get('team_name')
				else:
					batting_first=teams[0].get('team_name')
					bowling_first=teams[1].get('team_name')

			batting_first=batting_first.strip()
			bowling_first=bowling_first.strip()

			print(batting_first+' vs '+bowling_first)

			if batting_first != find_team_name(whose_squad(squad1_id)):
				squad1_id,squad2_id=squad2_id,squad1_id
				name1,name2=name2,name1
				squad1,squad2=squad2,squad1
			squad1_score=get_squad_score(squad1_id)
			squad2_score=get_squad_score(squad2_id)
			if match.get('ended')==1:
				if squad1_score.get('total_run')>squad2_score.get('total_run'):
					win[find_team_name(whose_squad(squad1_id))]+=1
					lose[find_team_name(whose_squad(squad2_id))]+=1
					print('won = '+find_team_name(whose_squad(squad1_id))+' '+t_name+' '+str(win[t_name]))
				elif squad1_score.get('total_run')<squad2_score.get('total_run'):
					lose[find_team_name(whose_squad(squad1_id))]+=1
					win[find_team_name(whose_squad(squad2_id))]+=1
					print('won = '+find_team_name(whose_squad(squad2_id))+' '+t_name+' '+str(win[t_name]))
				else:
					draw[find_team_name(whose_squad(squad1_id))]+=1
					draw[find_team_name(whose_squad(squad2_id))]+=1
			else:
				result="Match still running"

	return win[t_name], lose[t_name], draw[t_name]


def team_details(request,team_id):
	cursor=get_cursor()
	sql="select * from team where trim(team_id)=trim(:team_id)"
	cursor.execute(sql,{'team_id':team_id})
	result=cursor.fetchone()
	name=result[1]
	type=result[2]

	odi_win,odi_lose,odi_draw=odi_info(team_id)
	odi_played=odi_win+odi_lose+odi_draw

	t20_win,t20_lose,t20_draw=t20_info(team_id)
	t20_played=t20_win+t20_lose+t20_draw


	print('final.........'+str(odi_win)+' '+str(odi_lose))
	return render(request,'team_details.html',locals())

def manager(request):
	dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
	connection = cx_Oracle.connect(user='ESPN', password='espn', dsn=dsn_tns)
	cursor= connection.cursor()
	sql="SELECT FIRST_NAME || ' ' || LAST_NAME ,MANAGER_ID FROM MANAGER"
	cursor.execute(sql)
	res=cursor.fetchall()
	cursor.close()
	managers=[]
	for r in res:
		row={'name':r[0], 'id':r[1]}
		managers.append(row)
	return render(request, 'manager.html', {'managers':managers})

def manager_detail(request, id):
	if request.method=='GET':
		dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
		connection=cx_Oracle.connect(user='ESPN',password='espn',dsn=dsn_tns)

		connection.commit()
		cursor=connection.cursor()
	sql="SELECT FIRST_NAME||' '|| LAST_NAME AS NAME, TO_CHAR(DOB,'DD-MON-YYYY'), FLOOR((SYSDATE-DOB)/365) ,MOD(FLOOR(SYSDATE-DOB),365) ,NATIONALITY FROM MANAGER WHERE TRIM(MANAGER_ID)= trim(:id)"
	cursor.execute(sql,{'id':id})
	res1= cursor.fetchone()
	cursor.close()

	info={'name': res1[0], 'dob':res1[1], 'year':res1[2], 'days':res1[3], 'nationality':res1[4] }
	
	cursor=connection.cursor()
	sql="select team_id, to_char(signing_date,'DD-Mon-YYYY'), (select contract_length from contract where contract.contract_id=manages.contract_id), (select salary from contract where contract.contract_id=manages.contract_id) from manages where trim(manager_id)=trim(:id)"
	
	cursor.execute(sql,{'id':id})
	res2=cursor.fetchall()
	cursor.close()
	cur_job=[]
	for r in res2:
		cur_job.append({'team':find_team_name(r[0]), 'salary':r[3],'sign_date':r[1], 'con_len':r[2]})

	return render(request, 'manager_detail.html' ,{'info': info , 'curjob': cur_job})

def news_list(request):
	cursor=get_cursor()
	sql="select news_id,news_date, title from news order by news_date desc"
	cursor.execute(sql)
	result=cursor.fetchall()
	all_news=[]
	for r in result:

		tit=str(r[2])
		if len(tit)>=60:
			tit=tit[:50]
			tit=tit+'...'

		all_news.append({'news_id':r[0],'news_date':r[1],'title':tit})
	return render(request,'news_list.html',locals())
def DESC(request):
	return render(request,'DESC.html')