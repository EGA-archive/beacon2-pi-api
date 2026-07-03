from adminbackend.forms.models import ModelsForm
import yaml
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

#@login_required
#@permission_required('adminclient.can_see_view', raise_exception=True)
def models_enabled(request):
    form =ModelsForm()
    context = {'form': form}
    if request.method == 'POST':
        form = ModelsForm(request.POST)
        if form.is_valid():
            with open("/home/app/web/beacon/conf/models/models_conf.yml") as f:
                models_conf=yaml.safe_load(f)
            for k, enabled in form.cleaned_data.items():
                models_conf[k]={'model_enabled':enabled}



            with open('/home/app/web/beacon/conf/models/models_conf.yml', 'w') as outfile:
                yaml.dump(models_conf, outfile)

        
            return redirect("adminclient:models")
        else:
            context = {'form': form}
            
    template = "general_configuration/models.html"
    return render(request, template, context)