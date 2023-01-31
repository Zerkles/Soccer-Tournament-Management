from datetime import datetime
import random

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse
from django.utils import timezone

from .models import Tournament, Player, Score
from user.views import authorized


def create(request):
    if request.session.get('auth_user', None) is None:
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        template = loader.get_template('tournamentCreate.html')
        return HttpResponse(template.render({'auth_user': request.session.get('auth_user', None)}, request))
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET'])


def tournament(request):
    if request.method == 'GET':
        if tournament_started(Tournament.objects.all()):
            return HttpResponseRedirect('/tournament/')

        active_tournaments = Tournament.objects.filter(status='active')
        if request.session.get('auth_user', None) is not None and request.session['auth_user']['usergroup'] == 'admin':
            draft_tournaments = Tournament.objects.filter(status='draft')
            historic_tournaments = Tournament.objects.filter(status='historic')
        elif request.session.get('auth_user', None) is not None:
            owner_id = request.session['auth_user']['id']
            draft_tournaments = Tournament.objects.filter(status='draft', owner_id=owner_id)
            historic_tournaments = Tournament.objects.filter(status='historic', owner_id=owner_id)
        else:
            draft_tournaments = Tournament.objects.none()
            historic_tournaments = Tournament.objects.none()

        historic_date_start = request.GET.get('date_start', '')
        historic_date_end = request.GET.get('date_end', '')

        if historic_date_start != '':
            historic_tournaments = historic_tournaments.filter(datetime__gte=historic_date_start)

        if historic_date_end != '':
            historic_tournaments = historic_tournaments.filter(datetime__lte=historic_date_end)

        context = {'active_tournaments': active_tournaments, 'draft_tournaments': draft_tournaments,
                   'historic_tournaments': historic_tournaments, 'auth_user': request.session.get('auth_user', None)}

        template = loader.get_template('tournamentViewAll.html')
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        if request.session.get('auth_user', None) is None:
            return HttpResponse('Unauthorized', status=401)

        data = request.POST

        if datetime.strptime(data['datetime'].replace("T", " "), '%Y-%m-%d %H:%M') < timezone.now().replace(
                tzinfo=None):
            return HttpResponse("Bad request - tournament cannot start in the past.", status=400)

        new_tournament = Tournament(name=data['name'], datetime=data['datetime'], max_players=data['max_players'],
                                    owner_id=data['owner_id'], status='draft')

        new_tournament.save()
        return HttpResponseRedirect(reverse('tournament'))

    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])


def tournament_arg(request, id):
    tournament = Tournament.objects.get(id=id)

    if tournament_started([tournament]):
        return HttpResponseRedirect(f'/tournament/{id}/')

    if request.method == 'GET':
        players = Player.objects.filter(tournament_id=id)
        scores = Score.objects.filter(tournament_id=id).order_by('stage')

        context = {'tournament': tournament, 'players': players, 'scores': scores,
                   'auth_user': request.session.get('auth_user', None)}

        if authorized(session=request.session, permitted_user_id=tournament.owner_id):
            template = loader.get_template('tournamentView.html')
        else:
            template = loader.get_template('tournamentViewNotOwner.html')

        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        if tournament.status == 'active':
            return HttpResponse('Bad request - cannot modify active tournament details', status=400)

        if not authorized(session=request.session, permitted_user_id=tournament.owner_id):
            return HttpResponse('Unauthorized', status=401)

        data = request.POST
        tournament.name = data['name']
        tournament.datetime = data['datetime']
        tournament.max_players = data['max_players']
        tournament.save()

        return HttpResponseRedirect(reverse('tournament'))

    elif request.method == 'DELETE':
        if tournament.status == 'active' and not authorized(session=request.session):
            return HttpResponse('Not authorized - only admin can delete active tournament.', status=401)

        if not authorized(session=request.session, permitted_user_id=tournament.owner_id):
            return HttpResponse('Unauthorized', status=401)

        Player.objects.filter(tournament_id=id).delete()
        Score.objects.filter(tournament_id=id).delete()
        tournament.delete()
        return HttpResponseRedirect(reverse('tournament'))

    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST', 'DELETE'])


def tournament_delete(request, id):
    request.method = 'DELETE'
    return tournament_arg(request, id)


def player(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)

    if not authorized(session=request.session, permitted_user_id=tournament.owner_id):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        if tournament.max_players == len(Player.objects.filter(tournament_id=tournament_id)):
            return HttpResponse('Bad Request - reached maximum number of players.', 400)

        data = request.POST
        new_player = Player(name=data['name'], tournament_id=tournament_id)
        new_player.save()
        return HttpResponseRedirect(f'/tournament/{tournament_id}/')

    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])


def player_arg(request, tournament_id, playerID):
    player = Player.objects.get(id=playerID, tournament_id=tournament_id)
    tournament = Tournament.objects.get(id=tournament_id)

    if not authorized(session=request.session, permitted_user_id=tournament.owner_id):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'DELETE':
        player.delete()
        return HttpResponseRedirect(f'/tournament/{tournament_id}/')

    else:
        return HttpResponseNotAllowed(permitted_methods=['DELETE'])


def player_delete(request, tournament_id, playerID):
    request.method = 'DELETE'
    return player_arg(request, tournament_id, playerID)


def score_arg(request, tournament_id, scoreID):
    score = Score.objects.get(id=scoreID, tournament_id=tournament_id)
    tournament = Tournament.objects.get(id=tournament_id)

    if not authorized(session=request.session, permitted_user_id=tournament.owner_id):
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        data = request.POST

        if data['score_a'] == '':
            score.score_a = None
        else:
            score.score_a = data['score_a']

        if data['score_b'] == '':
            score.score_b = None
        else:
            score.score_b = data['score_b']
        score.save()

        if score.score_a is not None and score.score_b is not None:

            if score.stage == 1:
                t = Tournament.objects.get(id=tournament_id)
                t.status = 'historic'
                t.save()
                return HttpResponseRedirect('/tournament/')

            else:
                score_next = Score.objects.get(id=score.next_id, tournament_id=tournament_id)

                if score.score_a > score.score_b:
                    if score.next_position == 'A':
                        score_next.player_a = score.player_a
                    else:
                        score_next.player_b = score.player_a
                else:
                    if score.next_position == 'A':
                        score_next.player_a = score.player_b
                    else:
                        score_next.player_b = score.player_b

                score_next.save()

        push_odd_slots(tournament_id, score.stage)
        return HttpResponseRedirect(f'/tournament/{tournament_id}/')

    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])


def push_odd_slots(tournament_id, stage):
    scores_players = Score.objects.filter(tournament_id=tournament_id, stage=stage,
                                          player_a__isnull=False, player_b__isnull=False)
    scores_finished = scores_players.filter(score_a__isnull=False, score_b__isnull=False)

    if len(scores_players) == len(scores_finished):
        scores = Score.objects.filter(tournament_id=tournament_id, stage=stage)

        print(scores_players.values())
        print(scores_finished.values())

        for s in scores:
            print(s.next_id)
            if s.player_a is None and s.player_b is not None:
                s_next = Score.objects.get(id=s.next_id)
                if s.next_position == 'A':
                    s_next.player_a = s.player_b
                else:
                    s_next.player_b = s.player_b
                s_next.save()

            if s.player_b is None and s.player_a is not None:
                print(s.next_id)
                s_next = Score.objects.get(id=s.next_id)
                if s.next_position == 'A':
                    s_next.player_a = s.player_a
                else:
                    s_next.player_b = s.player_a
                s_next.save()


def add_scores_resursively(stage, max, next_score):
    if stage > max:
        return

    score_a = Score(tournament_id=next_score.tournament_id, stage=stage, next_id=next_score.id,
                    next_position='A')
    score_a.save()
    add_scores_resursively(stage * 2, max, score_a)

    score_b = Score(tournament_id=next_score.tournament_id, stage=stage, next_id=next_score.id,
                    next_position='B')
    score_b.save()
    add_scores_resursively(stage * 2, max, score_b)


def tournament_generate_ladder(tournament_id):
    players = [p.name for p in Player.objects.filter(tournament_id=tournament_id)]

    random.shuffle(players)

    n_players = len(players)
    while not ((n_players & (n_players - 1) == 0) and n_players != 0):  # number of players must be power of 2
        players.append(None)
        n_players += 1

    final = Score(tournament_id=tournament_id, stage=1, next_id=0)
    final.save()

    add_scores_resursively(2, len(players) / 2, final)

    first_round_scores = Score.objects.filter(tournament_id=tournament_id, stage=len(players) / 2)
    for i, s in enumerate(first_round_scores):
        s.player_a = players[i * 2]
        s.player_b = players[(i * 2) - 1]
        s.save()


def tournament_started(tournaments):
    if_redirect = False

    for t in tournaments:
        if t.status == 'draft' and t.datetime <= timezone.now():
            if len(Player.objects.filter(tournament_id=t.id)) < 2:
                t.status = 'historic'
                t.save()
            else:
                t.status = 'active'
                t.save()
                tournament_generate_ladder(t.id)
            if_redirect = True

    return if_redirect
