from blog import create_app
from extensions import logger
from config import BaseConfig


if __name__ == '__main__':
    app = create_app(BaseConfig)
    logger.info("web service start")
    app.run()
