from django.urls import path
from .views import (
    CreateStringView,
    GetStringView,
    GetAllStringsView,
    DeleteStringView,
    NaturalLanguageFilterView
)

urlpatterns = [
    path('strings', CreateStringView.as_view()),
    path('strings/<str:string_value>', GetStringView.as_view()),
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view()),
    path('strings/', GetAllStringsView.as_view()),  # trailing slash version
    path('strings/<str:string_value>/', DeleteStringView.as_view()),
]

