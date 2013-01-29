import os, logging



yalogname = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs/yafunc.log" ))

logging.basicConfig(filename=yalogname,
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%m-%d %H:%M:%S',
            level=logging.INFO)


yaLog = logging.getLogger('yafunc')
