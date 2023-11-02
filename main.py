"""runs repository search"""

from datetime import datetime
from config import ConfigHandler, ConfigManager
from logging_manager import LoggingManager
from results_writer import ResultsWriter
from searcher import RepoSearcher


if __name__ == "__main__":
    date_str = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

    logger = LoggingManager(date_str)
    config_manager = ConfigManager(logger)
    config_handler = ConfigHandler(config_manager, logger)
    config_handler.populate_config()
    writer = ResultsWriter(date_str)
    writer.write_config(config_manager)
    searcher = RepoSearcher(logger, writer, config_manager)
    searcher.search()
    writer.write_found_words()
    config_handler.write_branch_updates()
