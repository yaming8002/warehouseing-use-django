
import math
from django.db import models
from django.db.models import Q



ng_spec_name =['鋼軌','中H300','中H350','中H400']

# 物料分類
class MatCat(models.Model):
    cat_id = models.CharField(max_length=12, verbose_name="物料編號")
    name = models.CharField(max_length=100, verbose_name="分類名稱")

    class Meta:
        unique_together = ["cat_id"]

    def __str__(self):
        return self.name


# 物料規格
class MatSpec(models.Model):
    name = models.CharField(max_length=100, verbose_name="規格名稱")

    def __str__(self):
        return self.name


# 物料清單
class Materials(models.Model):
    mat_code = models.CharField(max_length=12, verbose_name="物料編號")
    mat_code2 = models.CharField(max_length=12, verbose_name="入料編號", null=True)
    mat_code3 = models.CharField(max_length=12, verbose_name="出料編號" , null=True)
    name = models.CharField(max_length=100, verbose_name="料名")
    category = models.ForeignKey(MatCat, on_delete=models.CASCADE, verbose_name="分類")
    specification = models.ForeignKey(
        MatSpec, on_delete=models.CASCADE, verbose_name="規格", null=True
    )
    is_consumable = models.BooleanField(default=False, verbose_name="是否為耗材")
    is_divisible = models.BooleanField(default=False, verbose_name="是否可拆分")
    unit_of_division = models.CharField(
        max_length=5, blank=True, verbose_name="拆分單位"
    )

    @classmethod
    def get_item_by_code(cls,code:str,remark:str,unit):

        quest =(   Q(mat_code=code)
                        | Q(mat_code2=code)
                        | Q(mat_code3=code)
        )

        if code=='999' :
            if remark is None or "出售" in remark or remark not in ng_spec_name or remark=='廢鐵' :
                remark = "無"
            spec = MatSpec.objects.get(name=remark)
            quest &= Q(specification=spec)
        elif unit is None and cls.objects.filter(quest).count() >1  :
            spec = MatSpec.objects.get(id=23)
            quest &= Q(specification=spec)
        elif unit :
            spec = MatSpec.objects.get(id=math.ceil(unit))
            quest &= Q(specification=spec)

        return cls.objects.get(quest)

    class Meta:
        unique_together = ["mat_code", "category", "specification","name"]

    def __str__(self):
        return self.name
