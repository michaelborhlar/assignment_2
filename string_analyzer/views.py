from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from .models import StoredString
from .serializers import StoredStringSerializer
from .utils import analyze_string

class CreateStringView(APIView):
    def post(self, request):
        value = request.data.get("value")

        if not value:
            return Response({"error": "Missing 'value' field"}, status=400)

        if not isinstance(value, str):
            return Response({"error": "'value' must be a string"}, status=422)

        analyzed = analyze_string(value)
        sha_hash = analyzed["sha256_hash"]

        # Check if it already exists
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


class GetStringView(APIView):
    def get(self, request, string_value):
        from .utils import analyze_string
        sha_hash = analyze_string(string_value)["sha256_hash"]

        try:
            stored = StoredString.objects.get(id=sha_hash)
        except StoredString.DoesNotExist:
            return Response({"error": "String not found"}, status=404)

        serializer = StoredStringSerializer(stored)
        return Response(serializer.data, status=200)


class GetAllStringsView(APIView):
    def get(self, request):
        strings = StoredString.objects.all()

        # Filters
        is_palindrome = request.GET.get("is_palindrome")
        min_length = request.GET.get("min_length")
        max_length = request.GET.get("max_length")
        word_count = request.GET.get("word_count")
        contains_character = request.GET.get("contains_character")

        filters_applied = {}

        if is_palindrome is not None:
            val = is_palindrome.lower() == 'true'
            strings = [s for s in strings if s.properties.get('is_palindrome') == val]
            filters_applied["is_palindrome"] = val

        if min_length:
            strings = [s for s in strings if s.properties.get('length', 0) >= int(min_length)]
            filters_applied["min_length"] = int(min_length)

        if max_length:
            strings = [s for s in strings if s.properties.get('length', 0) <= int(max_length)]
            filters_applied["max_length"] = int(max_length)

        if word_count:
            strings = [s for s in strings if s.properties.get('word_count', 0) == int(word_count)]
            filters_applied["word_count"] = int(word_count)

        if contains_character:
            strings = [s for s in strings if contains_character in s.value]
            filters_applied["contains_character"] = contains_character

        serializer = StoredStringSerializer(strings, many=True)
        return Response({
            "data": serializer.data,
            "count": len(serializer.data),
            "filters_applied": filters_applied
        }, status=200)

class NaturalLanguageFilterView(APIView):
    """
    Basic version of Natural Language Filter endpoint.
    Supports a few simple keyword-based queries.
    """

    def get(self, request):
        query = request.query_params.get("query", "")
        if not query:
            return Response(
                {"error": "Missing 'query' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        query = query.lower()
        filters = {}

        # Simple keyword detection
        if "palindrome" in query:
            filters["is_palindrome"] = True
        if "single word" in query:
            filters["word_count"] = 1
        if "longer than" in query:
            # extract number from text e.g. "longer than 10 characters"
            import re
            match = re.search(r"longer than (\d+)", query)
            if match:
                filters["min_length"] = int(match.group(1)) + 1
        if "containing the letter" in query:
            import re
            match = re.search(r"containing the letter (\w)", query)
            if match:
                filters["contains_character"] = match.group(1)

        # Apply filters to queryset
        qs = AnalyzedString.objects.all()

        if "is_palindrome" in filters:
            qs = qs.filter(is_palindrome=filters["is_palindrome"])
        if "word_count" in filters:
            qs = qs.filter(word_count=filters["word_count"])
        if "min_length" in filters:
            qs = qs.filter(length__gte=filters["min_length"])
        if "contains_character" in filters:
            qs = qs.filter(value__icontains=filters["contains_character"])

        serializer = AnalyzedStringSerializer(qs, many=True)

        return Response({
            "data": serializer.data,
            "count": qs.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": filters
            }
        }, status=status.HTTP_200_OK)
                
class DeleteStringView(APIView):
    def delete(self, request, string_value):
        from .utils import analyze_string
        sha_hash = analyze_string(string_value)["sha256_hash"]

        try:
            StoredString.objects.get(id=sha_hash).delete()
            return Response(status=204)
        except StoredString.DoesNotExist:
            return Response({"error": "String not found"}, status=404)
