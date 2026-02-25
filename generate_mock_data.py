import pandas as pd
import numpy as np
import random

def generate_valorant_data(num_events=6000):
    # Map range: 0 to 1000 for both X and Y
    # Define hotspots (A Site, B Site, Mid)
    sites = {
        'A_Site': (800, 800),
        'B_Site': (200, 200),
        'Mid': (500, 500),
        'A_Link': (650, 600),
        'B_Link': (350, 400),
        'Spawn_Attacker': (500, 50),
        'Spawn_Defender': (500, 950)
    }
    
    event_types = ['Move', 'Kill', 'Death', 'Utility']
    players = [f'Player_{i}' for i in range(1, 11)]
    teams = {'Player_1': 'ATK', 'Player_2': 'ATK', 'Player_3': 'ATK', 'Player_4': 'ATK', 'Player_5': 'ATK',
             'Player_6': 'DEF', 'Player_7': 'DEF', 'Player_8': 'DEF', 'Player_9': 'DEF', 'Player_10': 'DEF'}
    
    data = []
    
    for round_id in range(1, 13): # Simulate 12 rounds
        for _ in range(num_events // 12):
            timestamp = round_id * 100 + random.randint(0, 99)
            player = random.choice(players)
            event = random.choice(event_types)
            
            # Weighted coordinate selection based on "tactical hot zones"
            if random.random() < 0.7:
                # Close to a site or mid
                hotspot = random.choice(['A_Site', 'B_Site', 'Mid', 'A_Link', 'B_Link'])
                base_x, base_y = sites[hotspot]
                x = np.clip(base_x + random.normalvariate(0, 80), 0, 1000)
                y = np.clip(base_y + random.normalvariate(0, 80), 0, 1000)
            else:
                # Random rotation/flank
                x = random.randint(0, 1000)
                y = random.randint(0, 1000)
            
            # Logic for Kills/Deaths (usually happen near sites)
            if event in ['Kill', 'Death']:
                # Bias kills towards actual combat zones
                hotspot = random.choice(['A_Site', 'B_Site', 'Mid'])
                base_x, base_y = sites[hotspot]
                x = np.clip(base_x + random.normalvariate(0, 50), 0, 1000)
                y = np.clip(base_y + random.normalvariate(0, 50), 0, 1000)

            data.append({
                'round_id': round_id,
                'timestamp': timestamp,
                'player_id': player,
                'team': teams[player],
                'event_type': event,
                'x': round(x, 2),
                'y': round(y, 2)
            })
            
    df = pd.DataFrame(data)
    df = df.sort_values(by=['round_id', 'timestamp'])
    
    output_file = 'gameplay_data.csv'
    df.to_csv(output_file, index=False)
    print(f"Successfully generated {len(df)} events in {output_file}")

if __name__ == "__main__":
    generate_valorant_data()
