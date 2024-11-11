# Dosya: users/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

def validate_phone_number(value):
    """Validate phone number format."""
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Phone number must be entered in the format: "+999999999". '
              'Up to 15 digits allowed.')
        )

def validate_social_media_links(value):
    """Validate social media links structure and format."""
    if not isinstance(value, dict):
        raise ValidationError(_('Social media links must be a dictionary.'))
        
    allowed_platforms = {'facebook', 'twitter', 'linkedin', 'instagram', 'github'}
        
    for platform, url in value.items():
        if platform not in allowed_platforms:
            raise ValidationError(
                _('%(platform)s is not a supported social media platform.'),
                params={'platform': platform},
            )
        if not url.startswith(('http://', 'https://')):
            raise ValidationError(
                _('%(url)s is not a valid URL.'),
                params={'url': url},
            )

def validate_interests(value):
    """Validate interests list format."""
    if not isinstance(value, list):
        raise ValidationError(_('Interests must be a list.'))
        
    if len(value) > 20:
        raise ValidationError(_('Maximum 20 interests are allowed.'))
        
    for interest in value:
        if not isinstance(interest, str):
            raise ValidationError(_('Each interest must be a string.'))
        if len(interest) > 50:
            raise ValidationError(_('Each interest must be less than 50 characters.'))

class StrongPasswordValidator:
    """Validate password strength."""
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _('Password must be at least %(min_length)d characters long.'),
                params={'min_length': self.min_length},
            )
        
        if not re.search('[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.')
            )
            
        if not re.search('[a-z]', password):
            raise ValidationError(
                _('Password must contain at least one lowercase letter.')
            )
            
        if not re.search('[0-9]', password):
            raise ValidationError(
                _('Password must contain at least one number.')
            )
            
        if not re.search('[^A-Za-z0-9]', password):
            raise ValidationError(
                _('Password must contain at least one special character.')
            )

    def get_help_text(self):
        return _("""
        Your password must contain at least:
        * %(min_length)d characters in length
        * One uppercase letter
        * One lowercase letter
        * One number
        * One special character
        """) % {'min_length': self.min_length}