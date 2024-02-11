from djoser import email
from djoser import utils
from djoser.conf import settings
from django.contrib.auth.tokens import default_token_generator

class BadRainbowzActivationEmail(email.ActivationEmail):
    template_name = 'users/ActivationEmail.html'

    def get_context_data(self):
        context = super().get_context_data()

        user = context['user']
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        return context

class ConfirmationEmail(email.ConfirmationEmail):
    template_name = 'users/ConfirmationEmail.html'

class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'users/PasswordReset.html'

#class PasswordResetConfirmationEmail(email.PasswordResetConfirmationEmail):
   # template_name = 'users/PasswordResetConfirmationEmail.html'

class UsernameResetEmail(email.UsernameResetEmail):
    template_name = 'users/UsernameResetEmail.html'

#class UsernameResetConfirmationEmail(email.UsernameChangedConfirmationEmail):
  #  template_name = 'users/UsernameResetConfirmationEmail.html'



