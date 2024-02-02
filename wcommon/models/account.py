from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class Muser(AbstractUser):
    username_zh = models.CharField(max_length=30, default="", verbose_name="姓名")

    # 所屬單位（中文支持，可為null）
    unit = models.CharField(max_length=30, null=True, verbose_name="所屬單位")

    # group = models.ForeignKey(
    #     Group, on_delete=models.SET_NULL, null=True, verbose_name="權限組"
    # )
    group = models.IntegerField( null=True, verbose_name="權限組"  )
    # Django原先的項目過於複雜，目前重構直接 連接到auth_group 。group的id 在關連到menu
    # menu 功能每一個權限都會建構一筆，表示menu的總數會是 功能數 * (權限數 +1 ) ;+1是有一個預設模板
    email = models.EmailField(null=True, blank=True)

    # 覆盖不需要的字段

    # is_superuser = None
    first_name = None
    last_name = None
    # 如果还有其他字段不需要，也可以在这里设置为 None

    def __str__(self):
        return f"Muser [ account:{self.username } Chinese Name: {self.username_zh}, Unit: {self.unit}, {super().__str__()}]"

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
