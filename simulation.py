"""
Monte Carlo Simulation: Chelsea vs Manchester City — FA Cup Final 2026
=======================================================================
Wembley Stadium | Saturday 16 May 2026 | 500 iterations

Model: Bivariate independent Poisson with time-weighted minute-by-minute
goal probabilities, calibrated to 2025-26 season xG / xGA data and
adjusted for the specific match context (Chelsea injuries, City form,
Rodri doubt, cup-final variance).

See simulation_assumptions.md for full methodology, data sources, and
parameter justifications.
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


# =====================================================================
# 1. MODEL PARAMETERS — tweak these to test different scenarios
# =====================================================================

# --- Manchester City attack ---
CITY_ATTACK_BASE = 1.95              # 68.1 season xG / ~35 PL games
CHELSEA_DEF_WEAKNESS_FACTOR = 1.15   # Chelsea D below City's avg opponent

# --- Chelsea attack ---
CHELSEA_ATTACK_BASE = 1.70           # 59.62 season xG / ~35 PL games
INJURY_PENALTY = 0.55                # 7 first-teamers out incl. BOTH wingers
CITY_DEF_STRENGTH = 0.88             # City's 1.12 xGA is league-best
CUP_FINAL_VARIANCE_BOOST = 1.10      # Finals slightly more unpredictable

# --- Extra time / penalties (FA Cup must produce a winner) ---
ET_CITY_PROBABILITY = 0.58           # 58% City, 42% Chelsea if drawn at 90'

# --- Simulation settings ---
N_SIMS = 500
SEED = 42

# Derived expected goals
CITY_XG = CITY_ATTACK_BASE * CHELSEA_DEF_WEAKNESS_FACTOR
CHELSEA_XG = (CHELSEA_ATTACK_BASE * INJURY_PENALTY
              * CITY_DEF_STRENGTH * CUP_FINAL_VARIANCE_BOOST)


# =====================================================================
# 2. TIME WEIGHTING — empirical curve for when goals happen
# =====================================================================

def minute_weights():
    """
    Returns normalised weights for minutes 0..89.
    Goals are not uniformly distributed — they spike near the end of
    each half and especially after the 75th minute.
    """
    w = np.ones(90)
    for m in range(90):
        if 30 <= m < 45:
            w[m] *= 1.10   # End-of-1st-half spike
        if 45 <= m < 60:
            w[m] *= 1.05   # Early 2nd half
        if 60 <= m < 75:
            w[m] *= 1.15   # Fatigue, subs
        if 75 <= m < 90:
            w[m] *= 1.30   # Late-game urgency
    return w / w.sum()


# =====================================================================
# 3. CORE SIMULATION
# =====================================================================

def run_simulation(n_sims=N_SIMS, seed=SEED):
    """
    Returns a dict of per-simulation results lists.
    """
    rng = np.random.default_rng(seed=seed)
    weights = minute_weights()

    city_minute_probs = CITY_XG * weights
    chel_minute_probs = CHELSEA_XG * weights

    results = []
    final_winner_inc_et = []
    city_goals_list = []
    chelsea_goals_list = []
    first_goal_times = []
    first_goal_scorers = []
    scorelines = []

    for _ in range(n_sims):
        city_goals = 0
        chel_goals = 0
        first_min = None
        first_team = None

        for m in range(90):
            # Bernoulli draw per minute approximates a thinned Poisson
            if rng.random() < city_minute_probs[m]:
                city_goals += 1
                if first_min is None:
                    first_min, first_team = m + 1, 'City'
            if rng.random() < chel_minute_probs[m]:
                chel_goals += 1
                if first_min is None:
                    first_min, first_team = m + 1, 'Chelsea'

        city_goals_list.append(city_goals)
        chelsea_goals_list.append(chel_goals)
        first_goal_times.append(first_min)
        first_goal_scorers.append(first_team)
        scorelines.append((city_goals, chel_goals))

        # Determine 90-minute result
        if city_goals > chel_goals:
            results.append('City')
            final_winner_inc_et.append('City')
        elif chel_goals > city_goals:
            results.append('Chelsea')
            final_winner_inc_et.append('Chelsea')
        else:
            results.append('Draw')
            # Resolve via ET/penalties coin flip
            winner = 'City' if rng.random() < ET_CITY_PROBABILITY else 'Chelsea'
            final_winner_inc_et.append(winner)

    return {
        'results': results,
        'final_winner_inc_et': final_winner_inc_et,
        'city_goals': city_goals_list,
        'chelsea_goals': chelsea_goals_list,
        'first_goal_times': first_goal_times,
        'first_goal_scorers': first_goal_scorers,
        'scorelines': scorelines,
    }


# =====================================================================
# 4. REPORTING
# =====================================================================

def print_summary(sim):
    rc = Counter(sim['results'])
    rc_et = Counter(sim['final_winner_inc_et'])
    n = len(sim['results'])

    print(f"Expected City xG:    {CITY_XG:.2f}")
    print(f"Expected Chelsea xG: {CHELSEA_XG:.2f}")
    print(f"Total expected:      {CITY_XG + CHELSEA_XG:.2f}")
    print()

    print("=" * 60)
    print(f"RESULTS AT 90 MINUTES ({n} simulations)")
    print("=" * 60)
    print(f"Man City win:  {rc['City']:>3d}  ({rc['City']/n*100:.1f}%)")
    print(f"Chelsea win:   {rc['Chelsea']:>3d}  ({rc['Chelsea']/n*100:.1f}%)")
    print(f"Draw:          {rc['Draw']:>3d}  ({rc['Draw']/n*100:.1f}%)")
    print()

    print("WINNER INCLUDING EXTRA TIME / PENALTIES")
    print("=" * 60)
    print(f"Man City lifts FA Cup: {rc_et['City']:>3d}  ({rc_et['City']/n*100:.1f}%)")
    print(f"Chelsea lifts FA Cup:  {rc_et['Chelsea']:>3d}  ({rc_et['Chelsea']/n*100:.1f}%)")
    print()

    print("GOALS PER TEAM")
    print("=" * 60)
    print(f"Avg City goals:    {np.mean(sim['city_goals']):.2f}  "
          f"(median {np.median(sim['city_goals']):.0f}, max {max(sim['city_goals'])})")
    print(f"Avg Chelsea goals: {np.mean(sim['chelsea_goals']):.2f}  "
          f"(median {np.median(sim['chelsea_goals']):.0f}, max {max(sim['chelsea_goals'])})")
    print()

    valid_first = [t for t in sim['first_goal_times'] if t is not None]
    goalless = sim['first_goal_times'].count(None)
    city_first = sum(1 for s in sim['first_goal_scorers'] if s == 'City')
    chel_first = sum(1 for s in sim['first_goal_scorers'] if s == 'Chelsea')

    print("FIRST GOAL")
    print("=" * 60)
    print(f"Avg first-goal minute:   {np.mean(valid_first):.1f}'")
    print(f"Median first-goal min:   {np.median(valid_first):.0f}'")
    print(f"Goalless final at 90':   {goalless}  ({goalless/n*100:.1f}%)")
    print(f"City scores first:       {city_first}  ({city_first/n*100:.1f}%)")
    print(f"Chelsea scores first:    {chel_first}  ({chel_first/n*100:.1f}%)")
    print()

    print("MOST COMMON SCORELINES (City - Chelsea)")
    print("=" * 60)
    score_counter = Counter(sim['scorelines'])
    for (c, ch), count in score_counter.most_common(8):
        bar = "█" * int(count / 2)
        print(f"  {c}-{ch}:  {count:>3d}  ({count/n*100:>4.1f}%)  {bar}")


# =====================================================================
# 5. VISUALISATION
# =====================================================================

def plot_results(sim, output_path='fa_cup_simulation.png'):
    rc = Counter(sim['results'])
    rc_et = Counter(sim['final_winner_inc_et'])
    score_counter = Counter(sim['scorelines'])
    n = len(sim['results'])
    valid_first = [t for t in sim['first_goal_times'] if t is not None]
    goalless = sim['first_goal_times'].count(None)
    city_first = sum(1 for s in sim['first_goal_scorers'] if s == 'City')
    chel_first = sum(1 for s in sim['first_goal_scorers'] if s == 'Chelsea')

    fig = plt.figure(figsize=(16, 10), facecolor='#0d1117')
    fig.suptitle('Chelsea vs Manchester City - FA Cup Final 2026\n'
                 f'{n}-Match Monte Carlo Simulation',
                 color='white', fontsize=16, fontweight='bold', y=0.98)

    # --- Panel 1: outcome pie ---
    ax1 = fig.add_subplot(2, 3, 1, facecolor='#0d1117')
    sizes = [rc['City'], rc['Chelsea'], rc['Draw']]
    labels = [f"Man City\n{rc['City']} ({rc['City']/n*100:.1f}%)",
              f"Chelsea\n{rc['Chelsea']} ({rc['Chelsea']/n*100:.1f}%)",
              f"Draw\n{rc['Draw']} ({rc['Draw']/n*100:.1f}%)"]
    colors = ['#6CABDD', '#034694', '#888888']
    ax1.pie(sizes, labels=labels, colors=colors, startangle=90,
            textprops={'color': 'white', 'fontsize': 10},
            wedgeprops={'edgecolor': '#0d1117', 'linewidth': 2})
    ax1.set_title('Result at 90 minutes', color='white', fontsize=12, fontweight='bold')

    # --- Panel 2: goals distribution ---
    ax2 = fig.add_subplot(2, 3, 2, facecolor='#0d1117')
    max_g = max(max(sim['city_goals']), max(sim['chelsea_goals'])) + 1
    bins = np.arange(-0.5, max_g + 0.5, 1)
    ax2.hist(sim['city_goals'], bins=bins, alpha=0.75, label='Man City',
             color='#6CABDD', edgecolor='white')
    ax2.hist(sim['chelsea_goals'], bins=bins, alpha=0.75, label='Chelsea',
             color='#034694', edgecolor='white')
    ax2.set_xlabel('Goals scored', color='white')
    ax2.set_ylabel('Frequency (sims)', color='white')
    ax2.set_title('Goals per team distribution', color='white', fontsize=12, fontweight='bold')
    ax2.legend(facecolor='#1c2128', edgecolor='white', labelcolor='white')
    ax2.tick_params(colors='white')
    for spine in ax2.spines.values():
        spine.set_color('white')
    ax2.grid(alpha=0.15)

    # --- Panel 3: first-goal histogram ---
    ax3 = fig.add_subplot(2, 3, 3, facecolor='#0d1117')
    ax3.hist(valid_first, bins=np.arange(0, 95, 5),
             color='#FFB000', edgecolor='white', alpha=0.85)
    ax3.axvline(np.mean(valid_first), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {np.mean(valid_first):.1f}\'')
    ax3.set_xlabel('Minute of first goal', color='white')
    ax3.set_ylabel('Frequency', color='white')
    ax3.set_title('When the first goal arrives', color='white', fontsize=12, fontweight='bold')
    ax3.legend(facecolor='#1c2128', edgecolor='white', labelcolor='white')
    ax3.tick_params(colors='white')
    for spine in ax3.spines.values():
        spine.set_color('white')
    ax3.grid(alpha=0.15)

    # --- Panel 4: scoreline heatmap ---
    ax4 = fig.add_subplot(2, 3, 4, facecolor='#0d1117')
    max_show = 5
    heatmap = np.zeros((max_show + 1, max_show + 1))
    for (c, ch), count in score_counter.items():
        if c <= max_show and ch <= max_show:
            heatmap[ch, c] = count
    ax4.imshow(heatmap, cmap='YlOrRd', aspect='auto')
    ax4.set_xticks(range(max_show + 1))
    ax4.set_yticks(range(max_show + 1))
    ax4.set_xticklabels(range(max_show + 1), color='white')
    ax4.set_yticklabels(range(max_show + 1), color='white')
    ax4.set_xlabel('Man City goals', color='white')
    ax4.set_ylabel('Chelsea goals', color='white')
    ax4.set_title('Scoreline frequency', color='white', fontsize=12, fontweight='bold')
    for i in range(max_show + 1):
        for j in range(max_show + 1):
            if heatmap[i, j] > 0:
                ax4.text(j, i, int(heatmap[i, j]), ha='center', va='center',
                         color='black' if heatmap[i, j] > 30 else 'white',
                         fontsize=9, fontweight='bold')
    for spine in ax4.spines.values():
        spine.set_color('white')
    ax4.tick_params(colors='white')

    # --- Panel 5: who scores first ---
    ax5 = fig.add_subplot(2, 3, 5, facecolor='#0d1117')
    first_categories = ['Man City\nfirst', 'Chelsea\nfirst', 'No goals\n(at 90)']
    first_counts = [city_first, chel_first, goalless]
    bars = ax5.bar(first_categories, first_counts,
                   color=['#6CABDD', '#034694', '#666666'], edgecolor='white')
    for bar, val in zip(bars, first_counts):
        ax5.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                 f'{val}\n({val/n*100:.1f}%)', ha='center', color='white', fontsize=10)
    ax5.set_ylabel('Simulations', color='white')
    ax5.set_title('First goal scored by', color='white', fontsize=12, fontweight='bold')
    ax5.tick_params(colors='white')
    for spine in ax5.spines.values():
        spine.set_color('white')
    ax5.grid(alpha=0.15, axis='y')

    # --- Panel 6: cup winner inc. ET ---
    ax6 = fig.add_subplot(2, 3, 6, facecolor='#0d1117')
    winner_labels = ['Man City', 'Chelsea']
    winner_counts = [rc_et['City'], rc_et['Chelsea']]
    bars = ax6.bar(winner_labels, winner_counts,
                   color=['#6CABDD', '#034694'], edgecolor='white', width=0.6)
    for bar, val in zip(bars, winner_counts):
        ax6.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                 f'{val}\n({val/n*100:.1f}%)', ha='center', color='white',
                 fontsize=11, fontweight='bold')
    ax6.set_ylabel('Simulations', color='white')
    ax6.set_title('FA Cup winner (after ET/pens)', color='white', fontsize=12, fontweight='bold')
    ax6.tick_params(colors='white')
    for spine in ax6.spines.values():
        spine.set_color('white')
    ax6.grid(alpha=0.15, axis='y')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, dpi=130, facecolor='#0d1117', bbox_inches='tight')
    print(f"\nSaved visualisation to {output_path}")


# =====================================================================
# 6. MAIN
# =====================================================================

if __name__ == '__main__':
    sim = run_simulation()
    print_summary(sim)
    plot_results(sim, output_path='fa_cup_simulation.png')
