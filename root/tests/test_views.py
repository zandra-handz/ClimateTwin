from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import BadRainbowzUser
from climatevisitor.models import ClimateTwinLocation
from climatevisitor.serializers import ClimateTwinLocationSerializer

class ClimateTwinLocationViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = BadRainbowzUser.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testemail@gmail.com'
        )
        self.other_user = BadRainbowzUser.objects.create_user(
            username='otheruser',
            password='otherpassword',
            email='otheremail@gmail.com'
        )
        self.location = ClimateTwinLocation.objects.create(
            user=self.user,
            name='Test Location',
            direction_degree=90.0,
            direction='East',
            miles_away=10.0,
            location_id='test123',
            latitude=35.123,
            longitude=-120.456,
            tags={'tag1': 'value1', 'tag2': 'value2'},
            wind_compass='NE',
            wind_agreement_score=80,
            street_view_image='https://example.com/image.jpg'
        )
        # Create a location for the other user
        self.other_user_location = ClimateTwinLocation.objects.create(
            user=self.other_user,
            name='Other User Location',
            direction_degree=180.0,
            direction='South',
            miles_away=15.0,
            location_id='other456',
            latitude=40.678,
            longitude=-110.789,
            tags={'tag3': 'value3', 'tag4': 'value4'},
            wind_compass='SW',
            wind_agreement_score=75,
            street_view_image='https://example.com/other_image.jpg'
        )

    def test_retrieve_own_location(self):
        # Log in the first user
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request to retrieve the own location
        url = reverse('visited-location', kwargs={'pk': self.location.pk})
        response = self.client.get(url)

        # Check if the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the returned data matches the serialized location
        expected_data = ClimateTwinLocationSerializer(self.location).data
        self.assertEqual(response.data, expected_data)
        

    def test_retrieve_other_user_location(self):
        # Log in the first user
        self.client.login(username='testuser', password='testpassword')

        # Attempt to make a GET request to retrieve the other user's location
        url = reverse('visited-location', kwargs={'pk': self.other_user_location.pk})
        response = self.client.get(url)

        # Check if the request returns a not found status (HTTP 404 Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
