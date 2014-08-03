# Caveman Duels
# http://codegolf.stackexchange.com/questions/34968/caveman-duels-or-me-poke-you-with-sharp-stick


#idea: check their last n (=5?) moves. see if all but the last were blocks. this would indicate a changing strategy

import sys
import random

def main():
    if len(sys.argv) == 1:
        #myhist = hishist = ''
        submit('S') #Only reasonable thing to do on first turn
    else:
        myhist, hishist = sys.argv[1].split(',')

    turns = len(myhist)
    
    mysharp = sharpness(myhist)
    hissharp = sharpness(hishist)

    moves = analyze_hist(myhist, hishist)

    # Get more aggressive under two conditions:
    # 1. Opponent is getting nearer to a sword
    # 2. Game is nearing the end (to avoid stalemate)
    aggression = 20 * hissharp + turns

    # They should have won by now, but in case they're stupid...
    if hissharp >= 5:
        if mysharp >= 1:
            submit('P')
        else:
            submit('S')

    #play defensively -- try to build up a sword
    def low_aggression():
        prediction = predict_move(mysharp, hissharp, moves, 1.0)
        if mysharp >= 5 or (prediction == 'S' and mysharp >= 1):
            submit('P') #sword -- go for it
        elif hissharp == 0:
            if mysharp == 4:
                submit('S') # They can't stop the sword
            elif prediction == 'S' and mysharp >= 1:
                submit('P') #Confident that they'll sharpen
            else:
                submit('S')
        elif mysharp == 0:
            submit('B') #defense -- let them wear down their stick
        else:
            submit('B')

    # Still play somewhat defensively, but take more risks
    def med_aggression():
        prediction = predict_move(mysharp, hissharp, moves, 0.85)
        if mysharp >= 5:
            submit('P')
        elif hissharp == 0:
            if mysharp == 4:
                submit('S') # They can't stop the sword
            elif prediction == 'S' and mysharp >= 1: #this isn't right. why only sharpen when i'm sharp?
                submit('P')
            else:
                submit('S')
        elif mysharp == 0:
            if prediction == 'S' or prediction == 'B':
                submit('S')
            else:
                submit('B')
        elif just_blocking(hishist) and (prediction == 'S' or prediction == 'B'):
            submit('S')
        else:
            submit('B')

    # We're in a risky situation. The game might be drawing to a close, or they might be going for a sword
    def high_aggression():
        prediction = predict_move(mysharp, hissharp, moves, 0.80)
        if turns == 99:
            if mysharp >= 1:
                submit('P') # Last ditch effort
            else:
                submit('B') # Take them down with me
        elif mysharp >= 5:
            submit('P')
        elif mysharp == 0:
            if hissharp >= 4:
                submit('S') # Can't poke, so might as well sharpen
            elif hissharp == 3:
                submit('S') # Try to never get to the point where hissharp = 4 and mysharp = 0
            elif prediction == 'P':
                submit('B')
            else:
                submit('S')
        elif hissharp == 0: # We got here because the game is nearing the end
            if mysharp >= 2:
                submit('P')
            elif turns >= 90: # Very urgent, but I have only one poke
                if prediction == 'S':
                    submit('P')
                elif just_blocking(hishist) or prediction == 'B':
                    submit('S')
                else:
                    submit('B')
            else:
                submit('S') # He can't do anything
        elif hissharp == 4:
            if mysharp == 1: # This is bad: they might be crafty and expect me to poke to prevent sword
                if hishist[-1] == 'B': # They blocked last turn. Probably gonna sharpen this time
                    submit('P')
                elif random.choice([True, False]): # Leave it to the fates
                    submit('P') # Think they're gonna sharpen
                elif prediction == 'P':
                    submit('B')
                else:
                    submit('S')
            else:
                submit('P') # I have at least 2 sharpness, so I can spare one on the chance that he's sharpening again
        elif mysharp == 4:
            if turns < 90:
                submit('B') # Try to get him to whittle down his stick
            else:
                submit(random.choice(['S', 'P'])) # Hissharp is 2 or 3, and the game is almost done. Be unpredictable
        else:
            submit(random.choice(['S', 'P', 'B'])) # This will likely never happen. If it does, go wild

    if aggression < 40:
        low_aggression()
    elif aggression < 60:
        med_aggression()
    else:
        high_aggression()

# Analyze my opponent's moves
# return a 3-dimensional list: [me_s][him_s][move]
def analyze_hist(me, him):
    me_s = him_s = 0
    moves = {}

    def add_to_moves(m,h,move):
        if not m in moves:
            moves[m] = {}
        if not h in moves[m]:
            moves[m][h] = {}
        if not move in moves[m][h]:
            moves[m][h][move] = 1
        else:
            moves[m][h][move] += 1

    for m,h in zip(me,him):
        add_to_moves(me_s, him_s, h)
        if m == 'P':
            me_s = max(0, me_s - 1)
        elif m == 'S':
            me_s += 1
        if h == 'P':
            him_s = max(0, him_s - 1)
        elif h == 'S':
            him_s += 1

    return moves

# If we can predict the opponent's move with enough confidence
# (based on past experience in the same sharpness situation),
# return what we think will happen
def predict_move(me_s, him_s, moves, confidence):
    if confidence <= 0.5: # It wouldn't make a ton of sense to get a prediction with < 0.5 confidence
        return None
    try:
        hist = moves[me_s][him_s]
    except:
        return None # We haven't seen this situation before
    total = sum(hist.values()) # Number of times we've been here
    if total < 3: # We need a good sample size
        return None
    for move, count in hist.iteritems():
        if float(count)/total >= confidence:
            return move
    
    # We could not predict the move
    return None

def sharpness(s):
    #Sharpness can't be negative
    return max(0, s.count('S') - s.count('P'))

def just_blocking(s):
    return len(s) >= 5 and s[-5:] == 'BBBBB'

def submit(move):
    print move
    exit()

if __name__ == '__main__':
    main()
