# 单例类装饰器
def singleton(cls):
    """
    单例类装饰器
    :param cls: 类
    :return: 单例类
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls in instances and instances[cls] is not None:
            if not isinstance(instances[cls], cls):
                instances[cls] = cls(*args, **kwargs)
        else:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
