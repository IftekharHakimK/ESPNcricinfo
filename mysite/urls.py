"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
import testapp.views as x
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('DESC', x.DESC,name='DESC'),
    path('', x.home,name='home'),
    path('players', x.players, name='players'),
    url(r'^players/player-detail/(?P<playerid>\w+)/$', x.player_detail, name='player_detail'),
    url(r'^espn/admin/$', x.login, name='login'),
    path('espn/admin/admin_update_home/',x.admin_update_home,name='admin_update_home'),
    path('espn/admin/logout',x.logout,name='logout'),
    url(r'^espn/admin/update/$', x.update, name='update'),
    path('espn/admin/create_tournament/',x.create_tournament,name='create_tournament'),
    path('espn/admin/create_tournament_p2/<int:total_team>/<str:tournament_id>/',x.create_tournament_p2,name='create_tournament_p2'),
    path('espn/admin/add/add_match/<str:tournament_id>/<str:tournament_name>/', x.add_match, name='add_match'),
    path('espn/admin/add/add_match/page2/<str:tournament_id>/<str:first_team>/<str:second_team>/', x.add_match_p2, name='add_match_p2'),
    path('espn/admin/add/add_match/page3/', x.add_match_p3, name='add_match_p3'),
    path('espn/admin/edit_tournament/show_tournaments/',x.show_tournaments,name='show_tournaments'),
    path('espn/admin/edit_tournament/go/<str:tournament_id>/<str:tournament_name>/',x.edit_tournament,name='edit_tournament'),
    path('home/tournaments/go/<str:tournament_id>/<str:tournament_name>/',x.user_view_tournament,name='user_view_tournament'),
    path('espn/admin/create_team/',x.create_team,name='create_team'),
    path('espn/admin/add_manager/',x.add_manager,name='add_manager'),
    path('espn/admin/new_player_contract/',x.new_player_contract,name='new_player_contract'),
    path('espn/admin/new_manager_contract/',x.new_manager_contract,name='new_manager_contract'),
    path('espn/admin/show_matches/<str:tournament_id>/',x.show_matches,name='show_matches'),
    path('espn/admin/edit_match/<str:match_id>/',x.edit_match,name='edit_match'),
    path('espn/view_match/<str:match_id>/',x.view_match,name='view_match'),
    path('espn/admin/update_mott/<str:tournament_id>',x.update_mott,name='update_mott'),
    path('espn/admin/end_tournament/<str:tournament_id>',x.end_tournament,name='end_tournament'),
    path('espn/admin/add_location/',x.add_location,name="add_location"),
    path('espn/admin/add_stadium/',x.add_stadium,name="add_stadium"),
    path('espn/admin/add_news/',x.add_news,name="add_news"),
    path('espn/admin/update_player_image/',x.update_player_image,name="update_player_image"),
    path('espn/home/recent_matches/',x.recent_matches,name="recent_matches"),
    path('espn/home/show_series/',x.show_series,name="show_series"),
    path('espn/home/user_show_matches/<str:tournament_id>/',x.user_show_matches,name="user_show_matches"),
    path('espn/home/user_point_table/<str:tournament_id>/',x.user_point_table,name="user_point_table"),
    path('espn/home/user_tournament_details/<str:tournament_id>/',x.user_tournament_details,name="user_tournament_details"),
    path('espn/top/',x.top,name="top"),
    path('espn/home/view_news/<str:news_id>/',x.view_news,name="view_news"),
    path('espn/home/user_view_teams/',x.user_view_teams,name="user_view_teams"),
    path('espn/home/team_details/<str:team_id>/',x.team_details,name="team_details"),
    path('espn/home/manager/',x.manager,name="manager"),
    path('espn/home/manager_detail/<str:id>/',x.manager_detail,name="manager_detail"),
    path('espn/home/news_list/',x.news_list,name="news_list")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)