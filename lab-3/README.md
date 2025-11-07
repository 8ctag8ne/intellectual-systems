# 🐍 Genetic Algorithm for Snake Game

## 📋 Table of Contents
- [About the Project](#about-the-project)
- [How the System Works](#how-the-system-works)
- [Snake's Brain](#snakes-brain)
- [Genetic Algorithm](#genetic-algorithm)
- [Installation and Launch](#installation-and-launch)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

---

## 🎯 About the Project

This is an implementation of a **genetic algorithm** for training a neural network to play the classic "Snake" game. Instead of the traditional backward propagation approach, the system uses **evolutionary principles** to find an optimal gameplay strategy.

### Key Features:
- ✅ **128 snakes play simultaneously** on one field
- ✅ **Natural selection**: only the best 32 survive
- ✅ **Evolution through generations**: crossover and mutations
- ✅ **Real-time training visualization**
- ✅ **11×11 vision system** around each snake
- ✅ **Save and load** trained populations

### Why is this interesting?
Genetic algorithms demonstrate how **simple evolutionary rules** can lead to complex behavior. Snakes "don't know" the game rules at the start, but through dozens of generations, they learn to avoid walls, seek food, and survive longer.

---

## 🧠 Snake's Brain

### Decision-Making System Architecture

Each snake has a **genome** — a set of weights that determines its behavior. This is not a full neural network, but a simplified direct connection system between sensors and actions.

### 1. Sensory System (Vision)

The snake "sees" the world through an **11×11 cell grid** around its head:

```
┌─────────────────────────┐
│ · · · · · · · · · · · │  Vision radius: 5 cells
│ · · · · · · · · · · · │
│ · · · · · · · · · · · │
│ · · · · · · · · · · · │
│ · · · · · · · · · · · │
│ · · · · · 🐍 · · · · · │  🐍 = snake head (center)
│ · · · · · · · · · · · │  🍎 = food
│ · · · · 🍎 · · · · · · │  ▓ = obstacle
│ · · · ▓ · · · · · · · │
│ · · · · · · · · · · · │
│ · · · · · · · · · · · │
└─────────────────────────┘
```

**What the snake sees:**
- **121 cells** in field of view (11×11)
- **Minus the center cell** (head) = **120 positions**
- For each position **2 sensors**:
  - `sensor[0]` = is there food here? (1 or 0)
  - `sensor[1]` = is there an obstacle here? (1 or 0)

**Total number of inputs: 120 positions × 2 sensors = 240 inputs**

### 2. Genome (Weights)

The snake's genome is a weight array of size `(120, 2, 4)`:

```python
weights[position][sensor_type][direction]
```

**Breakdown:**
- `position` (0-119): position in field of view (11×11 without center)
- `sensor_type`:
  - `0` = food sensor
  - `1` = obstacle sensor
- `direction`:
  - `0` = up ↑
  - `1` = right →
  - `2` = down ↓
  - `3` = left ←

**Example:**
```python
weights[49][0][0] = +15  # If food above → strongly go up
weights[49][1][0] = -10  # If obstacle above → DON'T go up
```

**Total number of weights: 120 × 2 × 4 = 960 parameters**

### 3. Decision-Making Process

#### Step 1: Get Vision
```python
vision = snake.get_vision(environment)  # Array (11, 11, 2)
```

#### Step 2: Calculate Outputs for Each Direction
```python
outputs = [0, 0, 0, 0]  # [up, right, down, left]

for each_position in field_of_view:
    if has_food:
        outputs += genome.weights[position][0][:]  # Add food weights
    
    if has_obstacle:
        outputs += genome.weights[position][1][:]  # Add obstacle weights
```

#### Step 3: Choose Direction
```python
direction = argmax(outputs)  # Direction with highest value
```

#### Step 4: Block Opposite Direction
The snake cannot turn 180°:
```python
outputs[opposite_direction] = -∞
```

### 4. Example Scenario

**Situation:**
- Food is located above and to the right of the snake
- Wall is located to the left

**Calculation:**
```
output[up]    = +15 (food above) + 0 + ... = +15
output[right] = +12 (food right) + 0 + ... = +12
output[down]  = 0 + 0 + ... = 0
output[left]  = 0 + (-10) (wall left) + ... = -10
```

**Decision:** snake goes **up** (maximum value +15)

### 5. Initial Initialization

To prevent snakes from crashing into walls from the start, the genome has **built-in penalties**:

```python
# For neighboring cells around the head
weights[above][obstacle][go_up] = -10
weights[right][obstacle][go_right] = -10
weights[below][obstacle][go_down] = -10
weights[left][obstacle][go_left] = -10
```

This gives snakes a basic "survival instinct" from birth.

---

## 🧬 Genetic Algorithm

### Concept

The genetic algorithm mimics natural evolution:
1. **Population** — a group of individuals (snakes) with different genes
2. **Selection** — the strongest survive
3. **Reproduction** — creating offspring through crossover
4. **Mutations** — random gene changes for diversity

### One Generation Cycle

```
┌─────────────────────────────────────────────────┐
│  GENERATION N                                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. EVALUATION                                 │
│     • 128 snakes play simultaneously           │
│     • Until all die or 2000 steps              │
│     • Each receives fitness                    │
│                                                 │
│  2. SELECTION                                  │
│     • Select 32 best snakes                    │
│     • Remaining 96 "die"                       │
│                                                 │
│  3. REPRODUCTION                               │
│     • Top-4 → copied without changes (elite)   │
│     • 124 new → crossover + mutation from 32   │
│                                                 │
│  4. NEXT GENERATION                            │
│     • New population of 128 snakes             │
│     • Cycle repeats                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 1. Fitness Function

Fitness determines the "success" of a snake:

```python
fitness = (current_length)² × 10 + food_eaten × 50
```

**Why exactly this?**
- **Length squared**: non-linearly rewards long snakes
  - Length 6 → fitness = 360
  - Length 10 → fitness = 1000
  - Length 15 → fitness = 2250
- **Food bonus**: stimulates active food seeking
  - 10 food = +500 to fitness

### 2. Selection

**Method:** Direct ranking selection

```python
# Sort all 128 snakes by fitness
sorted_snakes = sort(snakes, key=lambda s: s.fitness, reverse=True)

# Take top-32
survivors = sorted_snakes[:32]  # Best survive
dead = sorted_snakes[32:]       # Rest "die"
```

**Example:**
```
Snake #1:   fitness = 2500  ✓ Survives
Snake #15:  fitness = 1800  ✓ Survives
Snake #28:  fitness = 1200  ✓ Survives
...
Snake #32:  fitness = 800   ✓ Survives (last)
-------------------------------------------
Snake #33:  fitness = 750   ✗ Dies
Snake #128: fitness = 400   ✗ Dies
```

### 3. Reproduction

#### a) Elitism
**Top-4 snakes** are copied without changes:
```python
new_population[0] = copy(survivors[0])  # Best
new_population[1] = copy(survivors[1])  # Second best
new_population[2] = copy(survivors[2])  # Third best
new_population[3] = copy(survivors[3])  # Fourth best
```

**Why?** Guarantees that the generation doesn't become worse.

#### b) Crossover
Creating a child from two parents:

```python
def crossover(parent1, parent2):
    alpha = random(0.3, 0.7)  # Mixing coefficient
    
    child_weights = alpha × parent1.weights + (1-alpha) × parent2.weights
    
    return Genome(child_weights)
```

**Example:**
```
Parent 1: weights[49][0][0] = +15
Parent 2: weights[49][0][0] = +5
Alpha = 0.6

Child:    weights[49][0][0] = 0.6×15 + 0.4×5 = 11
```

#### c) Mutation
Random changes for diversity:

```python
def mutate(genome):
    for each_weight in genome.weights:
        if random() < MUTATION_RATE:  # 5% probability
            weight += gaussian_noise(mean=0, sigma=15)
            weight = clip(weight, -99, 99)  # Limit
```

**Example:**
```
Before mutation:   weights[49][0][0] = +15
Mutation:          +15 + noise(σ=15) = +15 + (-7) = +8
After mutation:    weights[49][0][0] = +8
```

### 4. Algorithm Parameters

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `POPULATION_SIZE` | 128 | Snakes on field simultaneously |
| `SURVIVORS` | 32 | How many survive |
| `ELITE_SIZE` | 4 | How many copied unchanged |
| `MAX_STEPS` | 2000 | Steps per generation |
| `MUTATION_RATE` | 0.05 | Mutation probability (5%) |
| `MUTATION_SIGMA` | 15 | Mutation strength |
| `FOOD_COUNT` | 1000 | Food on field simultaneously |
| `GRID_SIZE` | 150 | Field size (150×150) |

### 5. Evolutionary Dynamics

**Typical training progress:**

```
Generation 1:   Max fitness = 400   (snakes move chaotically)
Generation 10:  Max fitness = 900   (learning to avoid walls)
Generation 50:  Max fitness = 1800  (actively seeking food)
Generation 100: Max fitness = 3000  (efficient strategy)
Generation 200: Max fitness = 5000+ (nearly optimal gameplay)
```

**What happens:**
- **Generation 1-20:** Eliminating "suicidal" snakes (crashing into walls)
- **Generation 20-50:** Reinforcing obstacle avoidance
- **Generation 50-100:** Developing active food seeking
- **Generation 100+:** Optimizing trajectories and long-term planning

---

## 🚀 Installation and Launch

### Requirements

```bash
Python 3.7+
numpy
pygame
```

### Installation

```bash
# Clone repository
git clone <url>
cd snake_genetic

# Install dependencies
pip install numpy pygame
```

### Launch

```bash
python main.py
```

### Program Menu

```
1. Training with visualization
   • Slow but visual
   • Shows all 128 snakes in real-time
   • Recommended for first 10-20 generations

2. Fast headless training
   • Fast (headless mode)
   • Auto-saves statistics to CSV
   • Recommended for 100+ generations

3. Watch best snake
   • Loads saved population
   • Shows best genome gameplay

4. Load population and continue
   • Continues training from saved file

5. Test system
   • Basic component tests
```

### Example Session

```bash
# 1. Fast training for 100 generations
python main.py
> 2
> 100
> y  # Save statistics

# 2. Watch result
python main.py
> 3
> 1  # Select file gen_100.csv
```

---

## 📁 Project Structure

```
snake_genetic/
├── config.py              # Constants and settings
├── genome.py              # Genome class (weights, mutation, crossover)
├── snake.py               # Snake class (movement, vision, decisions)
├── food.py                # Food class
├── environment.py         # Environment class (field, barrier, rules)
├── genetic_algorithm.py   # GeneticAlgorithm class (evolution)
├── visualizer.py          # Visualizer class (pygame)
├── main.py                # Main file with menu
├── test_basic.py          # Basic tests
├── test_genome_penalties.py  # Penalty initialization test
└── data/
    ├── populations/       # CSV with populations
    └── stats/             # Training statistics
```

### Key Classes

#### `Genome`
- Stores 960 weights in format `(120, 2, 4)`
- Methods: `mutate()`, `crossover()`, `to_flat()`, `from_flat()`

#### `Snake`
- Has genome, body, energy
- Methods: `get_vision()`, `decide_direction()`, `move()`, `eat()`
- Fitness: `(length)² × 10 + food × 50`

#### `Environment`
- Manages 150×150 field
- Barrier around perimeter
- Methods: `step()`, `spawn_food()`, `is_obstacle()`

#### `GeneticAlgorithm`
- Manages population of 128 genomes
- Methods: `evaluate_population()`, `evolve()`
- Stores statistics history

---

## ⚙️ Configuration

All parameters in `config.py`:

### Field Dimensions
```python
GRID_SIZE = 150         # Field size
CELL_SIZE = 5           # Cell size (pixels)
VISION_RADIUS = 5       # Snake vision radius
```

### Snake Parameters
```python
INITIAL_SNAKE_LENGTH = 6
ENERGY = 40             # Initial energy
MIN_LENGTH = 4          # Minimum for survival
```

### Genetic Algorithm
```python
POPULATION_SIZE = 128   # Snakes simultaneously
SURVIVORS = 32          # Best survive
MAX_STEPS = 2000        # Max steps per generation
MUTATION_RATE = 0.05    # Mutation probability
MUTATION_SIGMA = 15     # Mutation strength
ELITE_SIZE = 4          # Elite unchanged
FOOD_COUNT = 1000       # Food on field
```

### Visualization
```python
FPS = 60                # Animation speed
COLOR_SNAKE = (0, 255, 0)
COLOR_FOOD = (255, 50, 50)
COLOR_OBSTACLE = (100, 100, 100)
```

---

## 🧪 Testing

### Basic Tests
```bash
python test_basic.py
```

Checks:
- Genome (creation, mutation, crossover)
- Vision system
- Genetic algorithm

### Obstacle Penalty Test
```bash
python test_genome_penalties.py
```

Visualizes vision grid and checks weight initialization correctness.

---

## 📊 Results

### Success Metrics

The program collects statistics:
- **Max Fitness:** Best snake of generation
- **Avg Fitness:** Average across all 128
- **Best Overall:** Best in all history
- **Max Length:** Length of longest snake
- **Max Food:** Most food eaten

### Files

**Populations:**
```
data/populations/gen_10.csv   # Every 10 generations
data/populations/gen_20.csv
data/populations/final_gen_100.csv
```

**Statistics:**
```
data/stats/training_20231207_143022.csv
```

CSV Format:
```
Generation,Max_Fitness,Avg_Fitness,Best_Overall_Fitness,Max_Length,Max_Food
1,450.0,320.5,450.0,8,3
2,680.0,420.3,680.0,10,5
...
```

---

## 🎓 Educational Value

### Concepts Demonstrated:

1. **Genetic Algorithms**
   - How evolutionary optimization works
   - Balance between exploitation vs exploration

2. **Decision-Making Systems**
   - Sensory input → processing → action
   - Weight-based decision making

3. **Evolutionary Dynamics**
   - How simple rules → complex behavior
   - Role of mutations and crossover

4. **Gradient-Free Optimization**
   - Alternative to backpropagation
   - Population-based search

### Possible Improvements:

- [ ] Add obstacles on field
- [ ] Implement tournament selection instead of direct
- [ ] Add caching for speed
- [ ] Implement true neural network
- [ ] Add diversity pressure (to avoid premature convergence)
- [ ] Parallelize population evaluation

---

## 📝 License

MIT License - use freely for learning and experiments!

---

## 🙏 Acknowledgments

Project created as an educational demonstration of genetic algorithms and evolutionary learning.

**Author:** Nazarii Yahotin  
**Date:** 2025

---

## 📧 Contact

Questions? Suggestions? Create an issue or pull request!

**Happy evolving! 🐍🧬**