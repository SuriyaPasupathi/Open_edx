"""
Certificates Application Configuration

Signal handlers are connected here.
"""


from django.apps import AppConfig
from django.conf import settings
from edx_proctoring.runtime import set_runtime_service


class CertificatesConfig(AppConfig):
    """
    Application Configuration for Certificates.
    """
    name = 'lms.djangoapps.certificates'

    def ready(self):
        """
        Connect handlers to signals.
        """
        import logging
        log = logging.getLogger(__name__)
        
        # Can't import models at module level in AppConfigs, and models get
        # included from the signal handlers
        from lms.djangoapps.certificates import signals  # pylint: disable=unused-import
        # Import webhook handler to register certificate event receivers
        try:
            log.info("=" * 80)
            log.info("CertificatesConfig.ready() - Importing webhook_handler...")
            from lms.djangoapps.certificates import webhook_handler  # pylint: disable=unused-import
            log.info("webhook_handler imported successfully!")
            
            # Verify signal receivers are registered
            from openedx_events.learning.signals import CERTIFICATE_CREATED, CERTIFICATE_CHANGED
            
            # Count registered receivers
            created_count = len(CERTIFICATE_CREATED._live_receivers())
            changed_count = len(CERTIFICATE_CHANGED._live_receivers())
            
            log.info(f"CERTIFICATE_CREATED signal has {created_count} receiver(s) registered")
            log.info(f"CERTIFICATE_CHANGED signal has {changed_count} receiver(s) registered")
            
            if created_count > 0:
                log.info("✓ Webhook handler is registered and ready to receive CERTIFICATE_CREATED events")
            else:
                log.warning("⚠ No receivers found for CERTIFICATE_CREATED signal!")
            
            if changed_count > 0:
                log.info("✓ Webhook handler is registered and ready to receive CERTIFICATE_CHANGED events")
            else:
                log.warning("⚠ No receivers found for CERTIFICATE_CHANGED signal!")
            
            log.info("=" * 80)
        except ImportError as e:
            log.error(f"Failed to import webhook_handler: {e}", exc_info=True)
        except Exception as e:
            log.error(f"Error registering webhook handlers: {e}", exc_info=True)
        if settings.FEATURES.get('ENABLE_SPECIAL_EXAMS'):
            from lms.djangoapps.certificates.services import CertificateService
            set_runtime_service('certificates', CertificateService())
