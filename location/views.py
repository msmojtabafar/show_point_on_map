from django.conf import settings
from django.shortcuts import render

from rest_framework.views import APIView, Response, status, Http404

from .models import Location
from .serializers import LocationSerializer, LinkSerializer

import folium
import re
from datetime import datetime


def show_map(request):
    return render(request, 'location_map.html')


class LocationAPIView(APIView):

    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationDetailAPIView(APIView):

    def get_location(self, pk):
        try:
            return Location.objects.get(pk=pk)
        except Location.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        location = self.get_location(pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        location = self.get_location(pk)
        serializer = LocationSerializer(instance=location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        location = self.get_location(pk)
        location_name = location.name
        location.delete()
        return Response(
            {"detail": f"location '{location_name}' got deleted successfully."},
            status=status.HTTP_204_NO_CONTENT)


class LocationCallAPIView(APIView):

    def get(self, request):

        time_set = request.query_params.get('between')
        if not time_set:
            data = {'detail': "You should set a query set"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Check if query param format is correct or not
        time_pattern = r"[0-9]{2}:[0-9]{2}:[0-9]{2}-[0-9]{2}:[0-9]{2}:[0-9]{2}$"
        if not re.match(time_pattern, time_set):
            data = {'detail': "query parameter should be in this format: '00:00:00-00:00:00'."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Get the beginning time and the ending time
        beginning_time, ending_time = time_set.split('-')
        beginning_time = datetime.strptime(beginning_time, "%H:%M:%S").time()
        ending_time = datetime.strptime(ending_time, "%H:%M:%S").time()

        # Check if beginning time is set earlier than ending time or not
        if beginning_time >= ending_time:
            data = {'detail': "First time_set, should be set earlier than second time_set."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        locations = Location.objects.filter(time__range=(beginning_time, ending_time))

        if locations.count() == 0:
            data = {'detail': "No location has been set between this time."}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        my_map = folium.Map()

        for location in locations:
            folium.Marker([location.lat, location.long], popup=location.name).add_to(my_map)

        my_map.save(settings.BASE_DIR/"location/templates/location_map.html")

        scheme = request.scheme
        host = request.META['HTTP_HOST']
        data = {'url': f'{scheme}://{host}/show-map/'}
        serializer = LinkSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)

