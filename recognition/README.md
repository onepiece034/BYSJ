# 中药材图像识别系统

这是一个基于深度学习的药材图像识别系统，使用Django框架提供API接口。

## 文件结构

```
recognition/
├── models/                  # 存放训练好的模型文件
├── __init__.py             # 包初始化文件
├── model_utils.py          # 模型加载和预测工具
├── views.py                # API视图函数
├── urls.py                 # URL路由配置
└── class_names.json        # 药材类别映射文件
```

## 功能说明

1. **模型加载**：自动加载预训练的ResNet50模型
2. **图像识别**：支持上传药材图片进行识别
3. **API接口**：
   - GET `/api/model-info`：获取模型信息
   - POST `/api/upload`：上传图片进行识别

## 使用方法

1. **准备模型文件**：
   - 将训练好的模型文件 `最佳_ResNet50模型.pth` 放入 `models/` 目录

2. **安装依赖**：
   ```bash
   pip install torch torchvision pillow django djangorestframework
   ```

3. **启动服务**：
   ```bash
   python manage.py runserver
   ```

4. **调用API**：
   - 上传图片：POST请求到 `/api/upload`
   - 获取模型信息：GET请求到 `/api/model-info`

## 注意事项

- 支持的图片格式：JPG、PNG
- 图片大小限制：5MB
- 确保模型文件和类别映射文件存在且正确 