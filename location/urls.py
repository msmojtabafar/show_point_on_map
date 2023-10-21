from django.urls import path

import location.views as location_view

urlpatterns = [
    path('', location_view.LocationAPIView.as_view()),
    path('<int:pk>/', location_view.LocationDetailAPIView.as_view()),
    path('get-map/', location_view.LocationCallAPIView.as_view()),
    path('show-map/', location_view.show_map),
]
