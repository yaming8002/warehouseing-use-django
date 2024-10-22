
from django.db import models
from stock.models.site_model import SiteInfo

class PDFileModel(models.Model):
    siteinfo = models.ForeignKey(
        SiteInfo,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="工地",
    )
    version = models.IntegerField(default=0,verbose_name='版本號')
    file_path = models.CharField(max_length=255, default="", verbose_name="路徑")

    class Meta:
        unique_together = ["siteinfo", "version"]
