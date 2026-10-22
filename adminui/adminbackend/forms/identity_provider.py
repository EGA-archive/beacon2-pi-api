from django import forms

class IDPForm(forms.Form):
    IdentityProvider = forms.CharField(help_text='Identity Provider')
    Issuer = forms.CharField(required=True,help_text='Issuer')
    ClientID = forms.CharField(required=True,help_text='Client ID')
    WellKnown = forms.CharField(required=True,help_text='Well Known Endpoint')
    BeaconInAudience = forms.BooleanField(required=False,help_text="Must include beacon's URL in audience")
    