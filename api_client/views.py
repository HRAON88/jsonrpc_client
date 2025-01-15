import json

from django.views.generic import FormView
from django.conf import settings
from .forms import JsonRpcForm
from jsonrpc.client import JsonRpcClient


class ApiView(FormView):
    template_name = 'api_client/index.html'
    form_class = JsonRpcForm
    success_url = '/'

    def form_valid(self, form):
        client = JsonRpcClient(settings.API_ENDPOINT)
        method = form.cleaned_data['method']

        try:
            params = json.loads(form.cleaned_data['params']) if form.cleaned_data['params'].strip() else {}
        except json.JSONDecodeError:
            form.add_error('params', 'Invalid JSON format')
            return self.form_invalid(form)

        response = client.call_method(method, params)
        self.extra_context = {'response': response}
        return self.render_to_response(self.get_context_data(form=form))