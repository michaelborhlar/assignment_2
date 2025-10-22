from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import StoredString
from .serializers import StoredStringSerializer
from .utils import analyze_string
import re


# POST /strings
class CreateStringView(APIView):
    def post(self, request):
        value = request.data.get("value")

        if not value:
            return Response({"error": "Missing 'value' field"}, status=400)

        if not isinstance(value, str):
            return Response({"error": "'value' must be a string"}, status=422)

        analyzed = analyze_string(value)
        sha_hash = analyzed["sha256_hash"]

        # Avoid duplicates
        if StoredString.objects.filter(id=sha_hash).exists():
            return Response({"error": "String already exists"}, status=409)

        stored = StoredString.objects.create(
            id=sha_hash,
            value=value,
            properties=analyzed,
            created_at=timezone.now()
        )
        serializer = StoredStringSerializer(stored)
        return Response(serializer.data, status=201)


# GET /strings (with filters)
class ListStringView(APIView):
    def get(self, request):
        queryset = StoredString.objects.all()
        params = request.query_params

        is_palindrome = params.get("is_palindrome")
        min_length = params.get("min_length")
        max_length = params.get("max_length")
        contains = params.get("contains")

        if is_palindrome is not None:
            queryset = queryset.filter(properties__is_palindrome=(is_palindrome.lower() == "true"))

        if min_length:
            queryset = queryset.filter(properties__length__gte=int(min_length))

        if max_length:
            queryset = queryset.filter(properties__length__lte=int(max_length))

        if contains:
            queryset = queryset.filter(value__icontains=contains)

        serializer = StoredStringSerializer(queryset, many=True)
        return Response(serializer.data, status=200)


# GET /strings/{string_value}
class GetStringView(APIView):
    def get(self, request, string_value):
        analyzed = analyze_string(string_value)
        sha_hash = analyzed["sha256_hash"]

        try:
            stored = StoredString.objects.get(id=sha_hash)
        except StoredString.DoesNotExist:
            return Response({"error": "String not found"}, status=404)

        serializer = StoredStringSerializer(stored)
        return Response(serializer.data, status=200)


# DELETE /strings/{string_value}
class DeleteStringView(APIView):
    def delete(self, request, string_value):
        analyzed = analyze_string(string_value)
        sha_hash = analyzed["sha256_hash"]

        try:
            stored = StoredString.objects.get(id=sha_hash)
            stored.delete()
            return Response(status=204)
        except StoredString.DoesNotExist:
            return Response({"error": "String not found"}, status=404)


# GET /strings/filter-by-natural-language?query=...
class NaturalLanguageFilterView(APIView):
    def get(self, request):
        query = request.query_params.get("query", "").lower()
        queryset = StoredString.objects.all()

        # Detect keywords
        if "palindrome" in query:
            queryset = queryset.filter(properties__is_palindrome=True)

        longer_match = re.search(r"longer than (\d+)", query)
        shorter_match = re.search(r"shorter than (\d+)", query)
        contains_match = re.search(r"contain(?:s|ing)? (\w+)", query)

        if longer_match:
            queryset = queryset.filter(properties__length__gt=int(longer_match.group(1)))
        if shorter_match:
            queryset = queryset.filter(properties__length__lt=int(shorter_match.group(1)))
        if contains_match:
            queryset = queryset.filter(value__icontains=contains_match.group(1))

        serializer = StoredStringSerializer(queryset, many=True)
        return Response(serializer.data, status=200)
