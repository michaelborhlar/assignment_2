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
        query = request.GET.get("query", "").lower().strip()
        parsed_filters = {}

        if not query:
            return Response({"error": "Missing 'query' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse natural phrases
        if "palindromic" in query:
            parsed_filters["is_palindrome"] = True
        if "single word" in query or "one word" in query:
            parsed_filters["word_count"] = 1
        if "longer than" in query:
            try:
                num = int(''.join(filter(str.isdigit, query.split("longer than")[1])))
                parsed_filters["min_length"] = num + 1
            except Exception:
                pass
        if "contain" in query or "containing" in query:
            for word in query.split():
                if len(word) == 1 and word.isalpha():
                    parsed_filters["contains_character"] = word
                    break

        if not parsed_filters:
            return Response({"error": "Unable to parse natural language query"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = StringRecord.objects.all()
        if parsed_filters.get("is_palindrome"):
            queryset = queryset.filter(is_palindrome=True)
        if parsed_filters.get("word_count"):
            queryset = queryset.filter(word_count=parsed_filters["word_count"])
        if parsed_filters.get("min_length"):
            queryset = queryset.filter(length__gte=parsed_filters["min_length"])
        if parsed_filters.get("contains_character"):
            queryset = queryset.filter(value__icontains=parsed_filters["contains_character"])

        serializer = StringRecordSerializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed_filters
            }
        }, status=status.HTTP_200_OK)
