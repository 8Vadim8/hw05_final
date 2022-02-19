from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_locations(self):
        """Проверка доступности адреса /about."""
        url_adress = {
            '/about/author/': 200,
            '/about/tech/': 200
        }
        for address, status in url_adress.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    status,
                    f'Страница {address} не доступна по этому адресу'
                )
