from django.db import models

class ChatMessage(models.Model):
    MODEL_CHOICES = [
        ('deepseek-chat', 'DeepSeek Chat'),
        ('deepseek-reasoner', 'DeepSeek Reasoner'),
    ]
    
    role = models.CharField(max_length=10)  # user 或 assistant
    content = models.TextField()
    reasoning_content = models.TextField(blank=True, null=True)  # 思维链内容，仅用于assistant角色
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES, default='deepseek-chat')  # 标识使用的模型类型
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role} ({self.model_type}): {self.content[:50]}..." 