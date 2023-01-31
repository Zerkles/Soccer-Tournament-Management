from django.db import models


class Tournament(models.Model):
    owner_id = models.IntegerField()
    name = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    max_players = models.IntegerField()
    status = models.CharField(max_length=255)


class Player(models.Model):
    tournament_id = models.IntegerField()
    name = models.CharField(max_length=255)


class Score(models.Model):
    tournament_id = models.IntegerField()
    player_a = models.CharField(max_length=255, default=None, null=True)
    player_b = models.CharField(max_length=255, default=None, null=True)
    score_a = models.IntegerField(default=None, null=True)
    score_b = models.IntegerField(default=None, null=True)
    next_id = models.IntegerField()
    next_position = models.CharField(max_length=255)
    stage = models.IntegerField()
