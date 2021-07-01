# -*- coding: utf-8 -*-
class PriorityList(list):
    '''优先级列表。

    根据应用场景优化：改动较慢，读取较快。
    '''
    def add(self, priority, value):
        index = 0
        for i, (prior, data) in enumerate(self):
            if data == value:
                raise RuntimeError("优先级列表不支持重复添加元素!")
            if prior <= priority:
                index = i
        self.insert(index, (priority, value))

    def remove(self, value):
        for i, (_, data) in enumerate(self):
            if data == value:
                self.pop(i)
                return True
        else:
            return False
