from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_messages')
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(_('Admin Notes'), blank=True)
    admin_response = models.TextField(_('Admin Response'), blank=True)
    responded_at = models.DateTimeField(_('Responded At'), null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
    
    def __str__(self):
        return f"{self.subject} - {self.user.email}"
