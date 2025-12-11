"""
Course certificate generation

These methods generate course certificates (they create a new course certificate if it does not yet exist, or update the
existing cert if it does already exist).

These methods should be called from tasks.
"""

import logging
from datetime import datetime
from uuid import uuid4

import requests
from django.conf import settings
from pytz import UTC
from requests.exceptions import ConnectionError, Timeout
from xmodule.modulestore.django import modulestore

from lms.djangoapps.certificates import api as certs_api
from lms.djangoapps.certificates.data import CertificateStatuses
from lms.djangoapps.certificates.models import GeneratedCertificate
from lms.djangoapps.certificates.utils import emit_certificate_event, get_preferred_certificate_name

log = logging.getLogger(__name__)

def generate_course_certificate(user, course_key, status, enrollment_mode, course_grade, generation_mode):
    """
    Generate a course certificate for this user, in this course run. If the certificate has a passing status, also emit
    a certificate event.

    Note that the certificate could be either an allowlist certificate or a "regular" course certificate; the content
    will be the same either way.

    Args:
        user: user for whom to generate a certificate
        course_key: course run key for which to generate a certificate
        status: certificate status (value from the CertificateStatuses model)
        enrollment_mode: user's enrollment mode (ex. verified)
        course_grade: user's course grade
        generation_mode: used when emitting an event. Options are "self" (implying the user generated the cert
            themself) and "batch" for everything else.
    """
    cert = _generate_certificate(user=user, course_key=course_key, status=status, enrollment_mode=enrollment_mode,
                                 course_grade=course_grade)

    if CertificateStatuses.is_passing_status(cert.status):
        # Emit a certificate event
        event_data = {
            'user_id': user.id,
            'course_id': str(course_key),
            'certificate_id': cert.verify_uuid,
            'enrollment_mode': cert.mode,
            'generation_mode': generation_mode
        }
        emit_certificate_event(event_name='created', user=user, course_id=course_key, event_data=event_data)
        
        # Call external API after certificate is successfully generated
        _call_external_certificate_api(user, course_key, cert)

    elif CertificateStatuses.unverified == cert.status:
        cert.mark_unverified(mode=enrollment_mode, source='certificate_generation')

    return cert


def _generate_certificate(user, course_key, status, enrollment_mode, course_grade):
    """
    Generate a certificate for this user, in this course run.

    This method takes things like grade and enrollment mode as parameters because these are used to determine if the
    user is eligible for a certificate, and they're also saved in the cert itself. We want the cert to reflect the
    values that were used when determining if it was eligible for generation.
    """
    # Retrieve the existing certificate for the learner if it exists
    existing_certificate = GeneratedCertificate.certificate_for_student(user, course_key)

    preferred_name = get_preferred_certificate_name(user)

    # Retain the `verify_uuid` from an existing certificate if possible, this will make it possible for the learner to
    # keep the existing URL to their certificate
    if existing_certificate and existing_certificate.verify_uuid:
        uuid = existing_certificate.verify_uuid
    else:
        uuid = uuid4().hex

    cert, created = GeneratedCertificate.objects.update_or_create(
        user=user,
        course_id=course_key,
        defaults={
            'user': user,
            'course_id': course_key,
            'mode': enrollment_mode,
            'name': preferred_name,
            'status': status,
            'grade': course_grade,
            'download_url': '',
            'key': '',
            'verify_uuid': uuid,
            'error_reason': ''
        }
    )

    if created:
        created_msg = 'Certificate was created.'
    else:
        created_msg = 'Certificate already existed and was updated.'
    log.info(f'Generated certificate with status {cert.status}, mode {cert.mode} and grade {cert.grade} for {user.id} '
             f': {course_key}. {created_msg}')
    return cert

#custom_code certifcation integration

def _call_external_certificate_api(user, course_key, cert):
    """
    Call external API services when certificate is successfully generated.
    API call is mandatory if EXTERNAL_CERTIFICATE_API_URL is configured.
    
    Args:
        user: User object
        course_key: Course key
        cert: GeneratedCertificate object
    """
    # Get external API URL from settings
    # Settings are loaded from lms.env.yml via production.py -> devstack.py
    external_api_url = getattr(settings, 'EXTERNAL_CERTIFICATE_API_URL', None)
    external_api_timeout = getattr(settings, 'EXTERNAL_CERTIFICATE_API_TIMEOUT', 10)
    external_api_key = getattr(settings, 'EXTERNAL_CERTIFICATE_API_KEY', None)
    
    # Log all settings values for debugging
    log.info(
        f"[EXTERNAL_CERT_API] Starting external certificate API call - "
        f"URL: {external_api_url}, "
        f"Timeout: {external_api_timeout}s, "
        f"API Key configured: {bool(external_api_key)}, "
        f"API Key length: {len(external_api_key) if external_api_key else 0}, "
        f"User: {user.id} ({user.username}), "
        f"Course: {course_key}, "
        f"Cert UUID: {cert.verify_uuid}"
    )
    
    # Debug: Check if settings module has the attribute
    if not hasattr(settings, 'EXTERNAL_CERTIFICATE_API_URL'):
        log.warning(
            f"[EXTERNAL_CERT_API] EXTERNAL_CERTIFICATE_API_URL not found in settings module. "
            f"Available EXTERNAL_* settings: {[k for k in dir(settings) if k.startswith('EXTERNAL_')]}"
        )
    
    if not external_api_url:
        log.warning(
            f"[EXTERNAL_CERT_API] External certificate API URL is not configured in settings. "
            f"Skipping API call for user {user.id}, course {course_key}, cert_uuid {cert.verify_uuid}"
        )
        return None
    
    try:
        # Get course object
        course = modulestore().get_course(course_key, depth=0)
        
        # Get certificate downloadable status for API payload (for download_url)
        # Use lazy import to avoid circular import (api.py -> generation_handler.py -> tasks.py -> generation.py)
        download_url = ''
        try:
            # Lazy import to break circular dependency
            from lms.djangoapps.certificates.api import certificate_downloadable_status
            certificate_status = certificate_downloadable_status(user, course_key)
            download_url = certificate_status.get('download_url', '') or cert.download_url or ''
        except ImportError as import_error:
            log.warning(
                f"[EXTERNAL_CERT_API] Could not import certificate_downloadable_status (circular import?), "
                f"using cert object directly - Error: {str(import_error)}"
            )
            download_url = cert.download_url or ''
        except Exception as api_error:
            log.warning(
                f"[EXTERNAL_CERT_API] Could not get certificate downloadable status, using cert object directly - "
                f"Error: {str(api_error)}"
            )
            download_url = cert.download_url or ''
        
        # Prepare payload for FastAPI webhook endpoint
        # Format matches FastAPI /webhook/course-completed endpoint
        payload = {
            'username': user.username,
            'email': user.email if user.email else '',
            'courseId': str(course_key),  # FastAPI expects 'courseId' (camelCase)
            'courseName': course.display_name if course else '',
            'courseNumber': course.number if course else '',
            'userId': user.id,
            'certificateUrl': download_url,
            'certificatePdfUrl': download_url,
            'certificateUuid': cert.verify_uuid,
            'completedDate': datetime.now(UTC).isoformat(),
            'grade': cert.grade or '',
            'mode': cert.mode or '',
            'status': cert.status,
        }
        
        log.debug(f"[EXTERNAL_CERT_API] Payload prepared: {payload}")
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
        }
        if external_api_key:
            headers['Authorization'] = f'Bearer {external_api_key}'
            log.debug(f"[EXTERNAL_CERT_API] Using API key authentication (key length: {len(external_api_key)})")
        else:
            log.debug("[EXTERNAL_CERT_API] No API key configured, making unauthenticated request")
        
        # Log the request details before making the call
        log.info(
            f"[EXTERNAL_CERT_API] Making POST request to: {external_api_url}, "
            f"Timeout: {external_api_timeout}s, "
            f"Payload keys: {list(payload.keys())}"
        )
        
        # Call external API
        response = requests.post(
            external_api_url,
            json=payload,
            headers=headers,
            timeout=external_api_timeout
        )
        
        if response.status_code in [200, 201, 202]:
            log.info(
                f"[EXTERNAL_CERT_API] ✅ Successfully called external certificate API - "
                f"URL: {external_api_url}, "
                f"Status: {response.status_code}, "
                f"User: {user.id}, "
                f"Course: {course_key}, "
                f"Cert UUID: {cert.verify_uuid}, "
                f"Response size: {len(response.content)} bytes"
            )
            try:
                response_json = response.json() if response.content else None
                log.debug(f"[EXTERNAL_CERT_API] Response JSON: {response_json}")
            except Exception:
                log.debug(f"[EXTERNAL_CERT_API] Response text: {response.text[:500]}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.content else None
            }
        else:
            log.warning(
                f"[EXTERNAL_CERT_API] ❌ External certificate API returned error - "
                f"URL: {external_api_url}, "
                f"Status: {response.status_code}, "
                f"User: {user.id}, "
                f"Course: {course_key}, "
                f"Cert UUID: {cert.verify_uuid}, "
                f"Response: {response.text[:500]}"
            )
            return {
                'success': False,
                'status_code': response.status_code,
                'error': response.text
            }
            
    except Timeout:
        log.error(
            f"[EXTERNAL_CERT_API] ⏱️ Timeout calling external certificate API - "
            f"URL: {external_api_url}, "
            f"Timeout: {external_api_timeout}s, "
            f"User: {user.id}, "
            f"Course: {course_key}, "
            f"Cert UUID: {cert.verify_uuid}"
        )
        return {'success': False, 'error': 'timeout'}
    except ConnectionError as e:
        log.error(
            f"[EXTERNAL_CERT_API] 🔌 Connection error calling external certificate API - "
            f"URL: {external_api_url}, "
            f"User: {user.id}, "
            f"Course: {course_key}, "
            f"Cert UUID: {cert.verify_uuid}, "
            f"Error: {str(e)}"
        )
        return {'success': False, 'error': 'connection_error'}
    except Exception as e:
        log.error(
            f"[EXTERNAL_CERT_API] ❌ Error calling external certificate API - "
            f"URL: {external_api_url}, "
            f"User: {user.id}, "
            f"Course: {course_key}, "
            f"Cert UUID: {cert.verify_uuid}, "
            f"Error: {str(e)}",
            exc_info=True
        )
        return {'success': False, 'error': str(e)}
