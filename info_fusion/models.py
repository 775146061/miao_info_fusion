from django.db import models

class MiaoModel(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    type = models.IntegerField(verbose_name='苗类型：1-九价 2-四价')
    province = models.CharField(max_length=255, verbose_name='省', null=True)
    city = models.CharField(max_length=255, verbose_name='市', null=True)
    district = models.CharField(max_length=255, verbose_name='区', null=True)
    address = models.CharField(max_length=500, verbose_name='详细地址，用于展示')
    hosptal = models.CharField(max_length=255, verbose_name='医院')
    starttime = models.DateTimeField(verbose_name='开始预约时间')
    endtime = models.DateTimeField(verbose_name='结束预约时间')
    platform = models.IntegerField(verbose_name='平台：1-知苗易约')
    quantity = models.IntegerField(verbose_name='本次放苗数量', null=True)
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)
