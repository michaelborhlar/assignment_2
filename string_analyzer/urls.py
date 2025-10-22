from django.urls import path
from .views import (
    CreateStringView,
    GetStringView,
    ListStringView,
    DeleteStringView,
    NaturalLanguageFilterView,
)

urlpatterns = [
    # POST /strings
    path('strings', CreateStringView.as_view(), name='create-string'),
    
    # GET /strings
    path('strings/', ListStringView.as_view(), name='get-all-strings'),
    
    # GET /strings/<string_value>
    path('strings/<str:string_value>', GetStringView.as_view(), name='get-string'),
    
    # DELETE /strings/<string_value>
    path('strings/<str:string_value>/delete', DeleteStringView.as_view(), name='delete-string'),
    
    # GET /strings/filter-by-natural-language
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view(), name='filter-natural'),
]
