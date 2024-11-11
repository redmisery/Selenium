from base import Driver

# a = Driver().instance.sessionManger
# b = Driver.instance.sessionManger
# print(a)
# print(b)

a = Driver()
if hasattr(a, 'path'):
    print('a has path')
