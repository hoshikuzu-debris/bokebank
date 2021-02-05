from django.urls import path

from . import views

app_name = 'bokebank'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('main/', views.main, name='main'),
    path('answer/', views.AnswerCreate.as_view(), name='answer'),
    path('check/', views.CheckList.as_view(), name='check_list'),
    path('check/<int:pk>/', views.Check.as_view(), name='check'),
    path('check/<int:pk>/evaluated/', views.evaluate, name='evaluate'),
    path('gallery/', views.Gallery.as_view(), name='gallery'),
    path('gallery/<int:pk>/', views.Detail.as_view(), name='detail'),
    path('user/<str:username>/', views.userpage, name='userpage'),
]