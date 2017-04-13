#!/usr/bin/env python
from stravalib.client import Client
from flask import Flask, jsonify, make_response

app = Flask(__name__)

#Set up auth
client = Client("28f91e91169eb2966a9f24e99946cda12729d1fc")

#Set bounds and limits
BOUNDS_OF_IST = [40.8027, 27.9985, 41.5252, 29.9297]
RIDER_LIMIT = 50

def get_leaders():	
	leaders = []
	segments = client.explore_segments(BOUNDS_OF_IST)
	for segment in segments:
		leaderboard = client.get_segment_leaderboard(segment.id, top_results_limit=RIDER_LIMIT)
		leaders.extend(leaderboard.entries)				
	return leaders

#Calculate scores for each athlete
#Rules: according to the rank in a leaderboard, athelete gets 50..1 points
#Rules: the athlete ranks 1st: score is multiplied by 10 (megaboost)
#Rules: the athlete ranks 2nd: score is multiplied by 8 (way to go boost)
#Rules: the athlete ranks 3rd: score is multiplied by 7 (not bad boost)
#Rules: the athlete ranks between 4...10 (included): score is multiplied by 5 (keep going boost)
#Rules: the athlete ranks between 11...20: score is multiplied by 2 (eehh boost)
#Rules: the athlete appeared in multiple leaderboards: gets boosted again (up to 2 times)
def calc_score(rank, number_of_boards = 1):
	score = (RIDER_LIMIT - rank + 1)	
	if rank == 1:
		score *= 10
	elif rank == 2:
		score *= 8
	elif rank == 3:
		score *= 7
	elif rank <= 10:
		score *= 5
	elif rank <= 20:
		score *= 2
	if (1 < number_of_boards < 4):
		score *= number_of_boards
	return score	

#Errors
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#Get athletes and how many times they've been listed in the most popular segments in Istanbul
@app.route("/riders")
def get_riders():	
	riders = dict()
	leaders = get_leaders()
	name = ""
	for leader in leaders:
		name = leader.athlete_name
		if name in riders:
			riders[name] += 1
		else:
			riders[name] = 1
	return jsonify(riders)

#Get scoreboard
@app.route("/leaderboard")
def get_scores():
	riders = dict()
	leaders = get_leaders()
	name = ""
	for leader in leaders:
		name = leader.athlete_name
		if name in riders:			
			riders[name] += calc_score(leader.rank, riders[name])
		else:
			riders[name] = calc_score(leader.rank)
	riders_list = sorted(riders, key=riders.get, reverse=True)	
	return jsonify(riders_list)

if __name__ == "__main__":
	app.run()