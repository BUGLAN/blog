from blog import app
from extensions import logger


if __name__ == '__main__':
    logger.info("web service start")
    app.run()
