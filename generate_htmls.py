"""
利用 coca.txt 去直接生成整个框架目录
00000-00999
    0000-0099
        00000_00099.html
"""
import os
import re
import json
from typing import Dict, List
from jinja2 import FileSystemLoader, Environment


LOW_LEVELS = 65
MIDDLE_LEVELS = 135


def process(root: str, template_dir: str,
            template_html: str, template_index: str):
    # 加载数据
    word_objs = load_data("./data/coca.json")
    # 生成学习 html 文件
    mkfiles(root, word_objs, template_dir, template_html)
    # 生成索引 html 文件
    generate_index(root, template_dir, template_index)


def load_data(path: str) -> Dict[str, str]:
    """
    加载单词的 json 数据
    """
    return json.load(open(path, "r", encoding="utf-8"))


def mkfiles(root: str, rs: List[Dict[str, str]], template_dir: str, template_html: str):
    # 获取文件系统加载器加载模板
    env = Environment(loader=FileSystemLoader(searchpath=template_dir,
                                              encoding="utf-8"), autoescape=True)
    # 加载的模板是当前路径下的 base.html
    html_template = env.get_template(template_html)
    # 获取单词的数量
    length = len(rs)
    sum = length // 1000 + 1   # 总的外层文件夹数
    print("Total Dir: %d" % sum)
    # 生成第一层文件夹对应的元组
    first_folders = [(1+n*1000, 1000+n*1000) for n in range(sum)]
    # 生成第二层文件夹对应的元组
    second_folders = [(1+x*100, 100+x*100) for x in range(sum*10)]
    # 生成子文件
    for i, first_folder in enumerate(first_folders):
        # 第一层文件夹的名字
        first_name = f"{first_folder[0]:05}_{first_folder[1]:05}"
        for k in range(10):
            # 内层遍历的下标
            v = i * 10 + k
            # 第二层文件夹的名字
            second_name = f"{second_folders[v][0]:05}_{second_folders[v][1]:05}"
            # 文件的目录
            file_dir = os.path.join(root, first_name, second_name)
            # 文件的路径, 它的格式同第二层文件夹, 当时移除了对齐
            file_name = f"{second_folders[v][0]}_{second_folders[v][1]}.html"
            # 文件的全路径: 根目录 第一层 第二层 文件名
            file_path = os.path.join(root, first_name, second_name, file_name)
            # 需要写入的数据
            offset = second_folders[v][1]
            # 防止左边界越界了
            if offset > len(rs):
                offset = len(rs)
            r = [r for r in rs[second_folders[v][0]-1:offset]]
            # 单词列表为空的话, 直接退出执行即可.
            if not r:
                return   # 退出函数的执行
            print(
                f"Output File indexs: ({second_folders[v][0]}, {offset}) and count: {len(r)}")
            # 创建目录
            try:
                os.makedirs(file_dir)
            except:
                print(f"{file_dir} already exist!")
            # 创建文件
            with open(file_path, "w", encoding="utf-8") as file:
                # 渲染html
                html_doc = html_template.render(word_objs=r)
                # 写入文件
                file.write(html_doc)


def generate_index(root: str, template_dir: str, template_index: str) -> None:
    """
    生成 index.html, 用于目录索引. 
    """
    # 扫描指定目录的中所有的 html 文件
    catalog: List[Dict[str, str]] = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            catalog.append({
                "path": "./content" + re.sub(r"\\", r"/", os.path.join(dirpath[len(root):], filename)),
                "name": filename
            })

    # 生成索引文件
    # 获取文件系统加载器加载模板
    env = Environment(loader=FileSystemLoader(searchpath=template_dir,
                                              encoding="utf-8"), autoescape=True)
    # 加载的模板是当前路径下的 base.html
    index_template = env.get_template(template_index)
    # 字典上下文参数
    context = {
        "low_levels": catalog[:LOW_LEVELS],
        "middle_levels": catalog[LOW_LEVELS:MIDDLE_LEVELS],
        "high_levels": catalog[MIDDLE_LEVELS:]
    }

    index_html = index_template.render(context=context)
    # 索引文件的目录
    index_path = os.path.join(os.path.dirname(root), "index.html")
    with open(index_path, "w", encoding="utf-8") as file:
        file.write(index_html)


if __name__ == "__main__":
    root = "./content"   # 生成文件的根路径
    template_dir = "./"  # 模板所在文件的路径
    template_html = "base.j2"  # 模板名
    template_index = "index.j2"

    # 总的处理流程函数
    process(root, template_dir,
            template_html, template_index)
    print("Mission Successfully!")
