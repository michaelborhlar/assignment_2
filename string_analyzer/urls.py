from django.urls import path
from .views import (
    CreateStringView,
    GetStringView,
    ListStringView,
    DeleteStringView,
    NaturalLanguageFilterView,
)

urlpatterns = [
    path("strings", CreateStringView.as_view(), name="create-string"),
    path("strings", ListStringView.as_view(), name="list-strings"),
    path("strings/<str:string_value>", GetStringView.as_view(), name="get-string"),
    path("strings/<str:string_value>", DeleteStringView.as_view(), name="delete-string"),
    path("strings/filter-by-natural-language", NaturalLanguageFilterView.as_view(), name="nl-filter"),
]
