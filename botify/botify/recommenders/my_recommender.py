from .toppop import TopPop
from .recommender import Recommender
import random


class MyRecommender(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, catalog, favourite_song, listened):
        self.tracks_redis = tracks_redis
        self.fallback = TopPop(tracks_redis, catalog.top_tracks[:100])
        self.catalog = catalog
        self.favourite_song = favourite_song
        self.listened = listened

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        # Добавление последнего трека в историю прослушивания
        if user not in self.listened:
            self.listened[user] = []
        self.listened[user].append(prev_track)

        # Запоминание трека, который пользователь сам выбрал, т.е. первый
        if user not in self.favourite_song:
            self.favourite_song[user] = prev_track

        # Получение последнего трека с наибольшей оценкой
        good_track = self.favourite_song[user]

        # Получение рекомендаций для трека
        previous_track = self.tracks_redis.get(good_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        # Выбор трека, которого еще не было в истории прослушивания, если все треки были, рекомендуем самый первый

        all_recommendations = list(recommendations)
        for i in range(0, len(all_recommendations)):
            if not all_recommendations[i] in self.listened[user]:
                return all_recommendations[i]
        return all_recommendations[0]

