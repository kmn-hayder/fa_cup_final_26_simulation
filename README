# Chelsea vs Manchester City — FA Cup Final 2026
## Monte Carlo Simulation: Assumptions & Parameters

**Match:** FA Cup Final — Saturday 16 May 2026, 15:00 BST, Wembley Stadium
**Simulations:** 500 iterations
**Random seed:** 42 (reproducible)

---

## 1. Data Sources

| Source | Used for |
|---|---|
| FotMob | Lineup confirmation, unavailable players list |
| FBref | Season xG / xGA totals |
| FootyStats | Per-match averages, over/under ratios, top scorers |
| Understat | xG validation cross-check |
| LiveScore | Premier League standings (City 75 pts, 68.1 xG) |
| Sports Mole / OneFootball / 101 Great Goals | Predicted starting XIs |
| EPL Index / 3 Added Minutes | Chelsea injury status, caretaker manager context |

---

## 2. Team Context (going into the final)

### Manchester City
- **Form:** Excellent. Back-to-back 3-0 PL wins (vs Brentford, vs Crystal Palace)
- **PL position:** 2nd, 75 pts, 2 behind Arsenal with 2 games left
- **Season xG:** 68.1 (1st in league)
- **Season xGA per game:** 1.12 (1st in league)
- **Shots per match:** 15.69 (5.51 on target)
- **Top scorers:** Haaland 26, Semenyo 15, Foden 7
- **Manager:** Pep Guardiola
- **Key absences:** Rodri doubtful (groin)
- **Predicted XI (4-3-3):** Trafford; Nunes, Stones, Aké, O'Reilly; Nico González, Bernardo Silva, Cherki; Foden, Haaland, Doku

### Chelsea
- **Form:** Poor. Lost 4 of last 6 home games. Recent 3-1 loss to Forest
- **Season xG:** 59.62 (3rd in league)
- **Season goals scored:** 55
- **Shots per match:** 13.89
- **Manager:** Calum McFarlane (caretaker — Maresca departed)
- **Key absences (7+ first-team players):**
  - Robert Sánchez (concussion, #1 GK)
  - Pedro Neto (knock, starting winger)
  - Alejandro Garnacho (knock, starting winger)
  - Estêvão (injured)
  - Jamie Gittens (injured)
  - Mykhaylo Mudryk (suspension)
  - Reece James (fitness doubt after 6 weeks out)
- **Predicted XI (4-2-3-1):** Jörgensen; James/Gusto, Fofana, Colwill, Cucurella; Caicedo, A. Santos; Palmer, Fernández, J. Pedro (out of position L); Delap

---

## 3. Core Model: Bivariate Independent Poisson with Time-Weighted Minutes

For each of 500 simulations, the match is played minute-by-minute (90 minutes). In each minute, each team has an independent probability of scoring derived from its expected goals (xG) for the match, distributed across minutes by an empirical weighting curve.

### Why this model
- **Poisson goal-scoring** is the standard, well-validated model for football match outcomes
- **Per-minute thinning** allows tracking *when* goals occur, not just the final score
- **Time weighting** reflects the empirical fact that goals are not uniformly distributed across the 90 minutes — they spike late in halves and especially after the 75th minute

---

## 4. Expected Goals (xG) Parameters

### Manchester City attacking xG → 2.24

| Component | Value | Rationale |
|---|---|---|
| Base attack | 1.95 | 68.1 season xG ÷ ~35 PL games |
| × Chelsea defensive weakness factor | 1.15 | Chelsea D is below City's average opponent; missing Sánchez; conceding heavily lately |
| **Final City xG** | **2.24** | |

### Chelsea attacking xG → 0.91

| Component | Value | Rationale |
|---|---|---|
| Base attack | 1.70 | 59.62 season xG ÷ ~35 PL games |
| × Injury penalty | 0.55 | Missing 7 first-teamers including BOTH wingers; J. Pedro out of position; no width in attack |
| × City defensive strength | 0.88 | City's xGA of 1.12 is league-best (~12% better than average) |
| × Cup-final variance boost | 1.10 | Finals historically produce slightly more upsets / unpredictable outputs |
| **Final Chelsea xG** | **0.91** | |

**Expected match total: 3.15 goals** (matches well with bookmaker O/U 2.5 implied probability)

---

## 5. Time-Weighting of Goal Probability

Each minute m ∈ [0, 89] has a weight w(m) applied to that team's xG, normalised so weights sum to 1 across the 90 minutes:

| Minutes | Multiplier | Reason |
|---|---|---|
| 0 – 29 | 1.00 (base) | Sides feeling each other out |
| 30 – 44 | 1.10 | End-of-first-half spike |
| 45 – 59 | 1.05 | Tactical adjustments early in 2nd half |
| 60 – 74 | 1.15 | Fatigue effects, subs, more open play |
| 75 – 89 | 1.30 | Late-game urgency, tiring legs, biggest empirical spike |

Goal probability in minute m for City = `CITY_XG × w(m)` (and likewise Chelsea). Since w(m) values are small (≪ 1), a Bernoulli draw per minute closely approximates the Poisson process.

---

## 6. Extra Time / Penalties

FA Cup finals must produce a winner, so draws at 90' are resolved with a single weighted coin flip:

- **58% Man City** wins in ET/pens
- **42% Chelsea** wins in ET/pens

This reflects City's superior squad depth and rested players but acknowledges that penalty shootouts in particular are highly variable. No separate ET goal-scoring simulation — kept simple to avoid compounding assumptions.

---

## 7. Output Metrics Tracked

For each simulation:
1. Final goals (City, Chelsea)
2. Result at 90 minutes (City win / Chelsea win / Draw)
3. Cup winner including ET/pens
4. Minute of the first goal (or `None` if goalless)
5. Team that scored first
6. Full scoreline as `(city_goals, chelsea_goals)`

Aggregated across 500 sims to produce:
- Win/draw/loss percentages
- Average and median goals per side
- First-goal minute distribution
- Most common scorelines (top 8)
- Scoreline heatmap (0-5 goals each)

---

## 8. Known Limitations

1. **Independent Poisson** assumes goals are uncorrelated. In reality, going 1-0 down changes the second team's behaviour (more attacking) and affects subsequent goal rates. Not modelled.
2. **No red cards / injuries during the match** — a single red card would meaningfully shift the result distribution.
3. **Haaland in finals:** he has 0 goals in 15 semis/finals for City. Pure xG model can't capture this anti-pattern.
4. **Rodri fitness:** modelled as out. If he plays, City's xG should rise ~0.1 and Chelsea's drop ~0.1.
5. **No tactical interaction:** real managers adapt to opposition. McFarlane vs Guardiola knowledge asymmetry is implicit only in the injury penalty.
6. **Mental factors:** Chelsea morale (caretaker manager, losing streak) is captured via the injury penalty but not as a separate variable.
7. **Wembley as neutral venue:** no home advantage applied to either side, though City fans typically outnumber Chelsea at finals.
8. **Variance boost (×1.10) for cup final** is judgment-based, not empirically calibrated.

---

## 9. Headline Results (seed = 42)

| Metric | Value |
|---|---|
| City win at 90' | 63.0% |
| Chelsea win at 90' | 15.6% |
| Draw at 90' | 21.4% |
| **City lifts the trophy (inc. ET/pens)** | **75.0%** |
| **Chelsea lifts the trophy (inc. ET/pens)** | **25.0%** |
| Avg City goals | 2.22 |
| Avg Chelsea goals | 1.02 |
| Avg first-goal minute | 26.1' |
| Median first-goal minute | 20' |
| Goalless at 90' | 4.4% |
| City scores first | 64.6% |
| Chelsea scores first | 31.0% |
| Most likely scoreline | 1-1 (11.0%) |

---

## 10. How to Re-run with Different Assumptions

Edit these constants near the top of `simulation.py`:

| Variable | Default | Try changing to... |
|---|---|---|
| `CITY_ATTACK_BASE` | 1.95 | 2.10 if you think they're peaking |
| `CHELSEA_ATTACK_BASE` | 1.70 | 1.50 to model deeper malaise |
| `INJURY_PENALTY` | 0.55 | 0.75 if James + Neto return |
| `CITY_DEF_STRENGTH` | 0.88 | 1.00 if Rodri sits and back line is shaky |
| `ET_CITY_PROBABILITY` (implicit 0.58) | — | 0.50 for true coin flip |
| `N_SIMS` | 500 | 5000 for tighter estimates |
| `seed=42` | — | Any integer for a different sample |
