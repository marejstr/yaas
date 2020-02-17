from django.contrib import auth
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation


class ReqTest(TestCase):
    # the application must store the language preference permanently for registered users

    fixtures = [
        'testfixtures.json',
    ]

    def test_req(self):

        test_user = User.objects.create_user(username='tester',
                                             password='tester')
        test_user.save()

        response = self.client.post(
            reverse('signin'),
            {
                'username': 'tester',
                'password': 'tester'
            },
        )

        user = auth.get_user(self.client)

        default_lang = user.userlanguage.language
        self.assertEqual(default_lang, "en")

        session_lang = self.client.session[translation.LANGUAGE_SESSION_KEY]
        self.assertEqual(session_lang, "en")

        response = self.client.get('/changeLanguage/sv/')

        user = auth.get_user(self.client)
        changed_lang = user.userlanguage.language
        self.assertEqual(changed_lang, "sv")

        self.client.logout()

        response = self.client.post(
            reverse('signin'),
            {
                'username': 'tester',
                'password': 'tester'
            },
        )

        final_lang = self.client.session[translation.LANGUAGE_SESSION_KEY]
        self.assertEqual(final_lang, "sv")
