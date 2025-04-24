from django.db import models

class Herb(models.Model):
    name = models.CharField(verbose_name='药名', max_length=100, primary_key=True, db_column='药名')
    alias = models.TextField(verbose_name='别名', null=True, blank=True, db_column='别名')
    taste = models.CharField(verbose_name='性味', max_length=100, null=True, blank=True, db_column='性味')
    meridian = models.CharField(verbose_name='归经', max_length=100, null=True, blank=True, db_column='归经')
    effect = models.TextField(verbose_name='功效', null=True, blank=True, db_column='功效')
    indication = models.TextField(verbose_name='主治', null=True, blank=True, db_column='主治')
    usage = models.TextField(verbose_name='用法用量', null=True, blank=True, db_column='用法用量')
    contraindication = models.TextField(verbose_name='用药禁忌', null=True, blank=True, db_column='用药禁忌')
    effect_class = models.CharField(verbose_name='功效分类', max_length=100, null=True, blank=True, db_column='功效分类')
    pharmacology = models.TextField(verbose_name='药理作用', null=True, blank=True, db_column='药理作用')
    chemistry = models.TextField(verbose_name='中药化学成分', null=True, blank=True, db_column='中药化学成分')
    prescription = models.TextField(verbose_name='选方', null=True, blank=True, db_column='选方')
    theory = models.TextField(verbose_name='各家论述', null=True, blank=True, db_column='各家论述')
    research = models.TextField(verbose_name='考证', null=True, blank=True, db_column='考证')
    taxonomy = models.CharField(verbose_name='科属分类', max_length=100, null=True, blank=True, db_column='科属分类')
    collection = models.TextField(verbose_name='采收和储藏', null=True, blank=True, db_column='采收和储藏')
    distribution = models.TextField(verbose_name='资源分布', null=True, blank=True, db_column='资源分布')
    morphology = models.TextField(verbose_name='动植物形态', null=True, blank=True, db_column='动植物形态')
    identification = models.TextField(verbose_name='生药材鉴定', null=True, blank=True, db_column='生药材鉴定')
    cultivation = models.TextField(verbose_name='药用植物栽培', null=True, blank=True, db_column='药用植物栽培')
    source = models.TextField(verbose_name='药材基源', null=True, blank=True, db_column='药材基源')
    environment = models.TextField(verbose_name='生态环境', null=True, blank=True, db_column='生态环境')

    class Meta:
        managed = False
        db_table = '中药数据库'
        verbose_name = '中药'
        verbose_name_plural = '中药'

    def __str__(self):
        return self.name 