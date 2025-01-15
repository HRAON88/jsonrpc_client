from django import forms

class JsonRpcForm(forms.Form):
    method = forms.CharField(
        initial='auth.check',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    params = forms.CharField(
        required=False,
        initial='{}',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )