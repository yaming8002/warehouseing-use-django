
from django.views.generic.edit import FormView
from django.db import models
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import models

class SaveControlView(FormView):
    name = ''
    model= models.Model 

    def get(self,request, *args, **kwargs):
        id = request.GET.get('id')
        if id:  # 如果是编辑操作
            modeldata = get_object_or_404(self.model, pk=id)
            form = self.form_class(instance=modeldata)
            title = '編輯' +self.name
            action_id = f"?id={id}"
        else:  # 如果是新增操作
            form = self.form_class()
            title = '新增' +self.name
            action_id = ""

        context = {
            'title': title,
            'action':request.path +action_id ,  # 设置 action 为当前 URL
            'form': form
        }
        return render(request, 'base/model_edit.html', context)

    def form_is_valid(self ,form):
        pass

        
    def post(self, request, *args, **kwargs):
        id = request.GET.get('id')
        if id:  # 如果是编辑操作
            modeldata = get_object_or_404(self.model, pk=id)
            form = self.form_class(request.POST, instance=modeldata)
        else:  # 如果是新增操作
            form = self.form_class(request.POST)
        
        if form.is_valid():
            self.form_is_valid(form)
            form.save()
            # 处理保存后的逻辑，例如重定向到列表页面
            return JsonResponse({"success": True, "msg": "成功"})
        
        errors = form.errors
        return JsonResponse({"success": False, "msg": f"{errors}"})
