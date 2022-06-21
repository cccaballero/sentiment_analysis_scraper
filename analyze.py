from pysentimiento import create_analyzer
from database import Article, Comment
from tqdm.auto import tqdm

sentiment_analyzer = create_analyzer(task="sentiment", lang="es")
