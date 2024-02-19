from django.db import models


# 物料分類
class MatCat(models.Model):
    cat_id = models.CharField(max_length=12, verbose_name="物料編號")
    name = models.CharField(max_length=100, verbose_name="分類名稱")

    class Meta:
        unique_together = [("cat_id")]

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

    class Meta:
        unique_together = ("mat_code", "category", "specification")

    def __str__(self):
        return self.name