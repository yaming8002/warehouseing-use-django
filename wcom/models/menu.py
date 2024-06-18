from django.db import models
from .user_group import UserGroup


class Menu(models.Model):
    # 選單名稱（不為null，中文支援）
    name = models.CharField(max_length=50, verbose_name="選單名稱")
    # 選單URL（不為null）
    url = models.CharField(max_length=255, verbose_name="選單URL")
    # 分類代號（不為null，中文支援）
    category = models.IntegerField( verbose_name="分類代號")
    # 項目順序
    order = models.IntegerField( verbose_name="順序")
    # 權限群組
    group = models.ForeignKey(
        UserGroup, on_delete=models.SET_NULL, null=True, verbose_name="權限組"
    )
    # Django原先的項目過於複雜，目前重構直接 連接到auth_group 。group的id 在關連到menu
    # menu 功能每一個權限都會建構一筆，表示menu的總數會是 功能數 * (權限數 +1 ) ;+1是有一個預設模板

    def __str__(self):
        return f"Menu {{ name: {self.name}, url: {self.url}, category: {self.category}, order: {self.order}, group: {self.group} }}"



class SysInfo(models.Model):
    code = models.CharField(max_length=6, verbose_name="代號")
    name = models.CharField(max_length=50, verbose_name="參數名稱")
    value = models.CharField(max_length=50, verbose_name="系統數值")

    @classmethod
    def get_value(cls,code=None,name=None):
        obj = cls.objects
        if code:
            obj.filter(code=code)
        if name:
            obj.filter(name=name)
        item = obj.first()
        return item.value
    
    @classmethod
    def get_value_by_code(cls,code):
        item = cls.objects.get(code=code)
        return item.value
    
    @classmethod
    def get_value_by_name(cls,name):
        item = cls.objects.get(name=name)
        return item.value

    class Meta:
        unique_together = [
            "code",
            "name"
        ]


class UserPermissions(models.Model):
    permission_map={
        0:"不啟用",
        1:"查詢",
        2:"新增修改",
        3:"新增修改移除"
    }

    group = models.ForeignKey(
        UserGroup, on_delete=models.SET_NULL, null=True, verbose_name="群組組"
    )
    permission=models.IntegerField(
        default=0 , choices=permission_map, verbose_name="權限代號"
    )
    menu = models.ForeignKey(
        Menu, on_delete=models.SET_NULL, null=True, verbose_name="清單"
    )

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name = "group"