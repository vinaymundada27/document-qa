from os.path import join, expanduser, dirname

"""
Global config options
"""

VEC_DIR = join(expanduser("~"), "data", "glove")
SQUAD_SOURCE_DIR = join(expanduser("~"), "data", "squad")
SQUAD_TRAIN = join(SQUAD_SOURCE_DIR, "train-v1.1.json")
SQUAD_DEV = join(SQUAD_SOURCE_DIR, "dev-v1.1.json")


TRIVIA_QA = join(expanduser("~"), "data", "trivia-qa")
TRIVIA_QA_UNFILTERED = join(expanduser("~"), "data", "triviaqa-unfiltered")

DOCUMENT_READER_DB = join(expanduser("~"), "data", "doc-rd", "docs.db")


_BASE = dirname(__file__)
CORPUS_DIR = join(_BASE, "data")
