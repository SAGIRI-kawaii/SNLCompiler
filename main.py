import time
from lexer.scanner import *
from parser.TreeNode import TreeNode
from parser.RecursiveDescentParser import RecursiveDescentParser
from pyecharts import options as opts
from pyecharts.charts import Tree


def get_dict(node: TreeNode) -> dict:
    if not node:
        return {"name": "ɛ"}
    data = {"name": node.get_value(), "children": []}
    if node.get_children():
        for child in node.get_children():
            data["children"].append(get_dict(child))
    return data


def print_tree(data: dict) -> None:
    data = [data]
    tree = (
        Tree().add("", data, orient="TB", initial_tree_depth=10).set_global_opts(title_opts=opts.TitleOpts(title="SNL语法树"))
    )
    tree.render()


logger.add("log/log_{time}.log")
# main()
with open("demo2.txt", "r", encoding="utf-8") as r:
    fp = list(r.read())
# print(''.join(fp))
lexer = Lexer()
# try:
result = lexer.get_result(fp)
if not result.get_errors():
    token_list = result.get_token_list()
    if token_list:
        # "列",
        table = PrettyTable(field_names=["行", "语义信息", "词法信息"])
        for token in token_list:
            # , token.column
            table.add_row([token.line, token.value, token.token_type])
        logger.success(f"Token:\n{table}")
        res = RecursiveDescentParser().parse_token_list(token_list)
        print_tree(get_dict(res.get_tree().get_root()))
        if res.get_errors():
            logger.error('\n'.join(res.get_errors()))
else:
    logger.error("分析错误\n" + "\n".join(result.get_errors()))
