from django.test import TestCase
from users.models import BadRainbowzUser
from climatevisitor.models import ClimateTwinLocation

class ClimateTwinLocationTest(TestCase):

    def test_get_item(self) -> None:
        user = BadRainbowzUser.objects.create(username='testuser')
        item = ClimateTwinLocation.objects.create(user=user)
        self.assertIsNotNone(item)
        self.assertEqual(item.user, user)