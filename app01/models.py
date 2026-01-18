from django.db import models
from django.db.models.manager import Manager


# Create your models here.

class Users(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)

    def __str__(self):
        return self.username


class Agents(models.Model):
    name = models.CharField(verbose_name='角色名称', max_length=32)
    description = models.CharField(verbose_name='简介', max_length=64)
    user_prompt = models.TextField(verbose_name='用户提示词')
    system_prompt = models.TextField(verbose_name='系统提示词')
    output = models.CharField(verbose_name='输出变量', max_length=32)

    def __str__(self):
        return self.name

class Inputs(models.Model):
    name = models.CharField(verbose_name='输入变量名称', max_length=32)
    agent = models.ForeignKey(Agents, on_delete=models.CASCADE)


class Cases(models.Model):
    product = models.CharField(verbose_name='产品', max_length=128)
    info = models.TextField(verbose_name='产品说明')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    core_job = models.CharField(verbose_name='核心任务', max_length=128, null=True, blank=True)
    job_map = models.CharField(verbose_name='任务地图', max_length=512, null=True, blank=True)
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    delta = models.FloatField(verbose_name='用时（秒）', null=True, blank=True)
    closed = models.BooleanField(verbose_name='完成', default=False)
    pinned = models.BooleanField(verbose_name='置顶', default=False)
    pinned_time = models.DateTimeField(verbose_name='置顶时间', null=True, blank=True)

    def __str__(self):
        return self.product


class Opportunities(models.Model):
    oppo = models.CharField(verbose_name='机会描述', max_length=128)
    type_choices = (
        (1, 'related_job'),
        (2, 'desired_outcome'),
        (3, 'constrain'),
    )
    type = models.SmallIntegerField(verbose_name='机会类型', choices=type_choices)
    customer = models.CharField(verbose_name='目标客户', max_length=128)
    solution = models.CharField(verbose_name='针对性方案', max_length=512)
    slogan = models.CharField(verbose_name='宣传口号', max_length=128)
    case = models.ForeignKey(Cases, on_delete=models.CASCADE)


class Flows(models.Model):
    name = models.CharField(verbose_name='子流程', max_length=32)
    index = models.IntegerField(verbose_name='流程序号')
    description = models.CharField(verbose_name='简介', max_length=128)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               verbose_name='父级',
                               null=True,
                               blank=True,
                               related_name='children')

    def __str__(self):
        return self.name


class Steps(models.Model):
    index = models.IntegerField(verbose_name='步骤序号')
    agent = models.ForeignKey(Agents, to_field='id', on_delete=models.CASCADE)
    flow = models.ForeignKey(Flows, to_field='id', on_delete=models.CASCADE)


class Contexts(models.Model):
    content = models.TextField(verbose_name='上下文')
    flow = models.ForeignKey(Flows, on_delete=models.CASCADE)
    case = models.ForeignKey(Cases, on_delete=models.CASCADE)

class Admin(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)

class StepTimer(models.Model):
    case = models.ForeignKey(Cases, on_delete=models.CASCADE)
    step = models.ForeignKey(Steps, on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    delta = models.FloatField(verbose_name='用时（秒）')
