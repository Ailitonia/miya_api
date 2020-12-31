import logging
import sys
import os
from datetime import datetime
from aiohttp.log import web_logger as logger


# 设置日志输出级别
logger.setLevel(logging.INFO)

# 增加默认命令行日志输出
default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(
    logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s'))
logger.addHandler(default_handler)

# 设置文件输出的日志
log_file_name = datetime.today().strftime('%Y-%m-%d %H-%M-%S') + '.log'
# 检查日志文件夹
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'log')):
    os.makedirs(os.path.join(os.path.dirname(__file__), 'log'))
    logger.info('未发现日志目录，已创建')
# 创建日志文件
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'log', log_file_name)):
    # 注意windowds下是没有node的，只能用open方法创建文件
    try:
        os.mknod(os.path.join(os.path.dirname(__file__), 'log', log_file_name))
        logger.info(log_file_name + ': 日志文件已创建')
    except AttributeError:
        log_path = os.path.dirname(__file__) + '/log/' + log_file_name
        with open(log_path, 'w+') as f:
            logger.info(log_file_name + ': 日志文件已创建')
f_handler = logging.FileHandler(
    os.path.join(os.path.dirname(__file__), 'log', log_file_name), encoding="utf-8")
f_handler.setFormatter(
    logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s'))
# 增加日志文件输出
logger.addHandler(f_handler)
