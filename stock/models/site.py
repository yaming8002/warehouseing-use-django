from django.db import models
from wcommon.templatetags import constn_state, site_genre
from django.utils import timezone
from wcommon.templatetags import site_genre


class SiteInfo(models.Model):
    code = models.CharField(max_length=10, verbose_name="工地代號")
    owner = models.CharField(max_length=50, verbose_name="業主")
    name = models.CharField(max_length=50, default="", verbose_name="工程名稱" ,null=True)
    crate_date = models.DateField(default=timezone.now, verbose_name="發案日期")
    genre = models.IntegerField(default=2, choices=site_genre)
    """
    site_tag = [(0, "主要"), (1, "工地")]
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

    class Meta:
        unique_together = ("code", "name")
        ordering = ["code"]  # 按照 id 升序排序

    def __str__(self):
        return f"{self.owner},{self.name}" 
