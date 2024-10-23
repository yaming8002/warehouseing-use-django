from django.db import models
from django.forms import ValidationError
from wcom.templatetags import constn_state, site_genre
from django.utils import timezone
from django.db.models import Q


class SiteInfo(models.Model):
    code = models.CharField(max_length=10, verbose_name="工地代號")
    owner = models.CharField(max_length=50, verbose_name="業主")
    name = models.CharField(max_length=50, default="", verbose_name="工程名稱" ,null=True)
    crate_date = models.DateField(default=timezone.now, verbose_name="發案日期")
    genre = models.IntegerField(default=2, choices=site_genre)
    """
    site_genre = [(0, "內部倉"), (1, "工地"),(2,"租料倉"),(3,"加工廠"),(4,"維修廠"),(5,"供應商"),(6,"其他")]
    """
    state = models.IntegerField(default=2, choices=constn_state)
    """
    constn_state = [(0, "結案"), (1, "運作中"), (2, "尚未動工"), (3, "取消")]
    """

    member = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="現場人員"
    )
    counter = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="會計人員"
    )
    done_date = models.DateField(null=True, verbose_name="結案日期")
    remark = models.TextField(null=True, verbose_name="備註")
    is_rail_done = models.BooleanField(default=False, verbose_name="鋼軌結案")
    is_steel_done = models.BooleanField(default=False, verbose_name="鋼樁結案")

    @classmethod
    def get_warehouse(cls):
        return cls.objects.get(code='0001')

    @classmethod
    def get_site_by_code(cls, code: str):

        try:
            # 获取所有匹配 code 的对象
            queryset = cls.objects.filter(code=code)
            count = queryset.count()

            if count > 1:
                # 如果有多条匹配记录，抛出重复的错误
                raise ValidationError(_(f'工地代码 "{code}" 重複，無法使用'))
            elif count == 0:
                # 如果没有匹配记录，抛出不存在的错误
                raise ValidationError(_(f'工地代码 "{code}" 不存在，请检查输入。'))
            else:
                # 返回单个匹配的记录
                return queryset.first()
        except ValidationError as e:
            # 捕获 ValidationError，直接抛出
            raise e
        except Exception as e:
            # 捕获其他任何异常并抛出带有具体错误信息的 ValidationError
            raise ValidationError(_(f'工地代码 "{code}" 数据有误: {str(e)}'))

    @classmethod
    def get_obj_by_value(cls, code=None, owner=None, name=None,genre=None):
        query = Q()
        if genre:
            query &= Q(genre=genre)
        if code:
            query &= Q(code=code)
        if owner:
            query &= Q(owner=owner)
        if name:
            query &= Q(name=name)

        return cls.objects.filter(query)


    class Meta:
        unique_together = ("code", "name")
        ordering = ["code"]  # 按照 id 升序排序

    def __str__(self):
        return f"{self.owner},{self.name}"
