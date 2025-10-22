from django.urls import path
from .views import (
    CreateStringView,
    ListStringView,
    GetStringView,
    DeleteStringView,
    NaturalLanguageFilterView
)

urlpatterns = [
    path('strings', CreateStringView.as_view()),          # POST
    path('strings', ListStringView.as_view()),            # GET (filters)
    path('strings/<str:string_value>', GetStringView.as_view()),   # GET specific
    path('strings/<str:string_value>', DeleteStringView.as_view()), # DELETE
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view()),
]
