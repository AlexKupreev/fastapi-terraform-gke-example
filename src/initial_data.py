import logging

from src.adapters.init_db import init_db
from src.services import unit_of_work


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    init_db(unit_of_work.SqlAlchemyUnitOfWork())


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
