"""
Webhook handler for certificate generation events.
Sends certificate completion events to external ICG API via FastAPI service.
"""
import logging
import os
import requests
from django.conf import settings
from openedx_events.learning.signals import CERTIFICATE_CREATED, CERTIFICATE_CHANGED
from django.dispatch import receiver

log = logging.getLogger(__name__)

# Configuration from environment variables
ICG_WEBHOOK_URL = os.getenv('ICG_WEBHOOK_URL', 'http://localhost:8000/webhook/course-completed')
ICG_WEBHOOK_ENABLED = os.getenv('ICG_WEBHOOK_ENABLED', 'true').lower() == 'true'

# Log initialization
log.info("=" * 80)
log.info("ICG Webhook Handler Initializing...")
log.info(f"ICG_WEBHOOK_ENABLED: {ICG_WEBHOOK_ENABLED}")
log.info(f"ICG_WEBHOOK_URL: {ICG_WEBHOOK_URL}")
log.info("=" * 80)



@receiver(CERTIFICATE_CREATED, dispatch_uid="icg_certificate_created_webhook")
def handle_certificate_created(sender, signal, **kwargs):
    """
    Handle certificate creation event and send webhook to ICG API.
    """
    log.info("=" * 80)
    log.info("CERTIFICATE_CREATED signal received!")
    log.info(f"Sender: {sender}")
    log.info(f"Signal: {signal}")
    log.info(f"Kwargs keys: {list(kwargs.keys())}")
    log.info(f"ICG_WEBHOOK_ENABLED: {ICG_WEBHOOK_ENABLED}")
    log.info("=" * 80)
    
    if not ICG_WEBHOOK_ENABLED:
        log.warning("ICG webhook is DISABLED, skipping certificate created event")
        return

    try:
        log.info(f"Processing CERTIFICATE_CREATED signal with kwargs: {kwargs}")
        certificate_data = kwargs.get('certificate')
        log.info(f"Certificate data type: {type(certificate_data)}")
        log.info(f"Certificate data attributes: {dir(certificate_data) if certificate_data else 'None'}")
        
        if not certificate_data:
            log.error("ERROR: Certificate data not found in CERTIFICATE_CREATED signal")
            log.error(f"Available kwargs: {list(kwargs.keys())}")
            return

        # Extract certificate information from CertificateData structure
        # CertificateData has: user (UserData), course (CourseData), mode, grade, current_status, download_url, name
        user_data = certificate_data.user
        course_data = certificate_data.course
        
        # Extract user info from UserData.pii
        username = user_data.pii.username if hasattr(user_data, 'pii') and user_data.pii else getattr(user_data, 'username', '')
        email = user_data.pii.email if hasattr(user_data, 'pii') and user_data.pii else getattr(user_data, 'email', '')
        
        # Extract course info from CourseData
        course_key = course_data.course_key if hasattr(course_data, 'course_key') else ''
        
        # Extract certificate details
        certificate_name = getattr(certificate_data, 'name', '')
        download_url = getattr(certificate_data, 'download_url', '') or ''
        grade = getattr(certificate_data, 'grade', '')
        mode = getattr(certificate_data, 'mode', '')
        status = getattr(certificate_data, 'current_status', '')
        
        # Get time from kwargs if available
        time_data = kwargs.get('time')
        completed_date = ''
        if time_data:
            try:
                completed_date = time_data.isoformat() if hasattr(time_data, 'isoformat') else str(time_data)
            except Exception as e:
                log.warning(f"Error formatting date: {e}")
        
        log.info(f"Extracted data - username: {username}, email: {email}, course_key: {course_key}")

        # Prepare webhook payload
        payload = {
            'username': username,
            'email': email,
            'courseId': str(course_key),
            'courseName': certificate_name,
            'certificateUrl': download_url,
            'certificatePdfUrl': download_url,
            'certificateUuid': '',  # Not available in CertificateData
            'completedDate': completed_date,
            'grade': grade,
            'mode': mode,
            'status': status,
        }
        
        log.info(f"Prepared payload: {payload}")

        log.info(f"Sending certificate created webhook for user {username}, course {course_key}")

        # Send webhook to FastAPI service
        response = requests.post(
            ICG_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code in [200, 201, 204]:
            log.info(f"Successfully sent certificate webhook for user {username}, course {course_key}")
        else:
            log.warning(
                f"Failed to send certificate webhook for user {username}, course {course_key}. "
                f"Status: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        log.error(f"Error sending certificate created webhook: {str(e)}", exc_info=True)


@receiver(CERTIFICATE_CHANGED, dispatch_uid="icg_certificate_changed_webhook")
def handle_certificate_changed(sender, signal, **kwargs):
    """
    Handle certificate changed event and send webhook to ICG API.
    Only sends if certificate status changed to downloadable.
    """
    log.info("=" * 80)
    log.info("CERTIFICATE_CHANGED signal received!")
    log.info(f"Sender: {sender}")
    log.info(f"Signal: {signal}")
    log.info(f"Kwargs keys: {list(kwargs.keys())}")
    log.info(f"ICG_WEBHOOK_ENABLED: {ICG_WEBHOOK_ENABLED}")
    log.info("=" * 80)
    
    if not ICG_WEBHOOK_ENABLED:
        log.warning("ICG webhook is DISABLED, skipping certificate changed event")
        return

    try:
        log.info(f"Processing CERTIFICATE_CHANGED signal with kwargs: {kwargs}")
        certificate_data = kwargs.get('certificate')
        log.info(f"Certificate data type: {type(certificate_data)}")
        log.info(f"Certificate data attributes: {dir(certificate_data) if certificate_data else 'None'}")
        
        if not certificate_data:
            log.error("ERROR: Certificate data not found in CERTIFICATE_CHANGED signal")
            log.error(f"Available kwargs: {list(kwargs.keys())}")
            return

        # Extract certificate information from CertificateData structure
        user_data = certificate_data.user
        course_data = certificate_data.course
        
        # Extract user info from UserData.pii
        username = user_data.pii.username if hasattr(user_data, 'pii') and user_data.pii else getattr(user_data, 'username', '')
        email = user_data.pii.email if hasattr(user_data, 'pii') and user_data.pii else getattr(user_data, 'email', '')
        
        # Extract course info from CourseData
        course_key = course_data.course_key if hasattr(course_data, 'course_key') else ''
        
        # Extract certificate details
        certificate_name = getattr(certificate_data, 'name', '')
        download_url = getattr(certificate_data, 'download_url', '') or ''
        grade = getattr(certificate_data, 'grade', '')
        mode = getattr(certificate_data, 'mode', '')
        status = getattr(certificate_data, 'current_status', '')
        
        # Only send webhook if certificate is now downloadable
        if status != 'downloadable':
            log.info(f"Certificate status is '{status}', not 'downloadable' - skipping webhook")
            return

        # Get time from kwargs if available
        time_data = kwargs.get('time')
        completed_date = ''
        if time_data:
            try:
                completed_date = time_data.isoformat() if hasattr(time_data, 'isoformat') else str(time_data)
            except Exception as e:
                log.warning(f"Error formatting date: {e}")
        
        log.info(f"Extracted data - username: {username}, email: {email}, course_key: {course_key}, status: {status}")

        # Prepare webhook payload
        payload = {
            'username': username,
            'email': email,
            'courseId': str(course_key),
            'courseName': certificate_name,
            'certificateUrl': download_url,
            'certificatePdfUrl': download_url,
            'certificateUuid': '',  # Not available in CertificateData
            'completedDate': completed_date,
            'grade': grade,
            'mode': mode,
            'status': status,
        }
        
        log.info(f"Prepared payload: {payload}")

        log.info(f"Sending certificate changed webhook for user {username}, course {course_key}")

        # Send webhook to FastAPI service
        response = requests.post(
            ICG_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code in [200, 201, 204]:
            log.info(f"Successfully sent certificate changed webhook for user {username}, course {course_key}")
        else:
            log.warning(
                f"Failed to send certificate changed webhook for user {username}, course {course_key}. "
                f"Status: {response.status_code}, Response: {response.text}"
            )

    except Exception as e:
        log.error(f"Error sending certificate changed webhook: {str(e)}", exc_info=True)



