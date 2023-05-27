from google_auth_oauthlib.flow import Flow
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework.views import APIView
from googleapiclient.discovery import build


class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
        )
        request.session['state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.get('state', '')
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
            state=state,
        )
        flow.fetch_token(authorization_response=request.get_full_path())

        credentials = flow.credentials
        request.session['credentials'] = credentials_to_dict(credentials)

        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        # Process the events as per your requirements...

        return HttpResponse('Events retrieved successfully! : \n\n' + str(events))


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }

