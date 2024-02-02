from django.contrib.auth.models import Group
from django.db import models

class Menu(models.Model):
     # 選單名稱（不為null，中文支援）
     name = models.CharField(max_length=50, verbose_name="選單名稱")
     # 選單URL（不為null）
     url = models.CharField(max_length=255, verbose_name="選單URL")
     # 分類代號（不為null，中文支援）
     category = models.IntegerField(null=False, verbose_name="分類代號")
     # 項目順序
     order = models.IntegerField(null=False, verbose_name="順序")
     # 權限群組
     group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, verbose_name="權限組")
     # Django原先的項目過於複雜，目前重構直接 連接到auth_group 。group的id 在關連到menu
     # menu 功能每一個權限都會建構一筆，表示menu的總數會是 功能數 * (權限數 +1 ) ;+1是有一個預設模板

     def __str__(self):
         return f'Menu {{ name: {self.name}, url: {self.url}, category: {self.category}, order: {self.order}, group: {self.group} }}'
