from dotenv import load_dotenv

from common import LogUtils
from common.config_loader import Config
from collections import defaultdict, deque

def build_dependency_graph(dependencies):
    """构建依赖图"""
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    name_to_fullpath = {}
    fullpath_to_name = {}

    # 收集所有测试用例的全路径和名称
    all_fullpaths = set()
    for module, classes in dependencies.items():
        for class_name, tests in classes.items():
            for test_name, test_info in tests.items():
                fullpath = f"{module}::{class_name}::{test_name}"
                name = test_info.get('name') or fullpath
                name_to_fullpath[name] = fullpath
                fullpath_to_name[fullpath] = name
                all_fullpaths.add(fullpath)

    # 建立依赖关系
    for module, classes in dependencies.items():
        for class_name, tests in classes.items():
            for test_name, test_info in tests.items():
                fullpath = f"{module}::{class_name}::{test_name}"
                name = test_info.get('name') or fullpath
                depends = test_info.get('depends', []) or []
                for dep in depends:
                    dep_name = fullpath_to_name.get(dep, dep)
                    graph[dep_name].append(name)
                    in_degree[name] += 1

    # 确保所有节点都在入度表中
    for node in graph:
        if node not in in_degree:
            in_degree[node] = 0

    return graph, in_degree, name_to_fullpath, all_fullpaths

def detect_cycle(graph):
    """检测依赖图中是否存在环，并返回环的路径"""
    visited = set()
    recursion_stack = set()
    cycle_path = []

    def dfs(node):
        nonlocal cycle_path
        if node in recursion_stack:
            cycle_path = list(recursion_stack) + [node]
            return True
        if node in visited:
            return False

        visited.add(node)
        recursion_stack.add(node)

        for neighbor in graph[node]:
            if dfs(neighbor):
                return True

        recursion_stack.remove(node)
        return False

    for node in list(graph.keys()):
        if node not in visited:
            if dfs(node):
                return cycle_path

    return None

def topological_sort(graph, in_degree):
    """拓扑排序，同时检测环"""
    queue = deque([node for node, degree in in_degree.items() if degree == 0])
    sorted_order = []

    while queue:
        node = queue.popleft()
        sorted_order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_order) != len(graph):
        error_log = ValueError("依赖关系中存在未处理的节点")
        LogUtils().errors(error_log)
        raise error_log

    return sorted_order

def generate_execution_order():
    """生成执行顺序"""
    dependencies = Config.dependency_config()

    graph, in_degree, name_to_fullpath, all_fullpaths = build_dependency_graph(dependencies)

    cycle = detect_cycle(graph)
    if cycle:
        cycle_names = ' -> '.join(cycle)
        cycle_fullpaths = ' -> '.join([name_to_fullpath[name] for name in cycle])
        error_log = ValueError(f"依赖关系中存在环: {cycle_names} (全路径: {cycle_fullpaths})")
        LogUtils().errors(error_log)
        raise error_log

    sorted_names = topological_sort(graph, in_degree)

    # 分配数字顺序
    execution_order = {}
    # 有依赖的测试用例分配1到N
    for idx, name in enumerate(sorted_names, start=1):
        try:
            fullpath = name_to_fullpath[name]
            execution_order.update({fullpath: idx})
        except KeyError:
            error_log = KeyError(f"未找到测试用例: {name}")
            LogUtils().errors(error_log)
            raise error_log

    # 收集没有依赖的测试用例
    sorted_fullpaths = {name_to_fullpath[name] for name in sorted_names}
    no_deps_fullpaths = all_fullpaths - sorted_fullpaths
    # 分配从1000开始的数字
    no_deps_sorted = sorted(no_deps_fullpaths)  # 可选：按全路径排序
    for idx, fullpath in enumerate(no_deps_sorted, start=1000):
        execution_order.update({fullpath: idx})

    return execution_order

if __name__ == "__main__":
    load_dotenv(r'C:\Users\hanyan\PycharmProjects\Selenium\env\.env')
    try:
        order = generate_execution_order()
        print("测试执行顺序:")
        for item in order:
            print(item)
    except ValueError as e:
        print(e)