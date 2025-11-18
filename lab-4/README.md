# 6×6 Sudoku CSP Solver

A comprehensive Constraint Satisfaction Problem (CSP) solver for 6×6 Sudoku puzzles, implemented in C# with multiple heuristic optimizations and a random puzzle generator.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [CSP Components](#csp-components)
- [Heuristics](#heuristics)
- [Algorithm Flow](#algorithm-flow)
- [Usage](#usage)
- [Examples](#examples)

---

## 🎯 Overview

This application solves Sudoku puzzles using **Constraint Satisfaction Problem** techniques. The implementation is flexible and supports different grid sizes through configurable constants.

**Default configuration (6×6 Sudoku):**
- **6 rows** and **6 columns**
- **6 blocks** of size **2×3** (2 rows × 3 columns)
- Numbers **1-6**

**Note:** The algorithm can be extended to other dimensions (e.g., 9×9 with 3×3 blocks) by modifying the size constants in the `Sudoku` class.

The solver employs **backtracking search** enhanced with three classical CSP heuristics that can be enabled independently or in combination:

1. **MRV** (Minimum Remaining Values) - Variable selection
2. **Degree Heuristic** - Variable selection / tie-breaking
3. **LCV** (Least Constraining Value) - Value ordering

---

## 📁 Project Structure

```
SudokuCSP/
├── Models/
│   ├── Variable.cs           # Represents a Sudoku cell with domain
│   └── Sudoku.cs             # Grid management and constraint checking
├── Solver/
│   └── CspSolver.cs          # Backtracking algorithm with heuristics
├── Generator/
│   └── SudokuGenerator.cs   # Random puzzle generation
└── Program.cs                # Console application entry point
```

### File Descriptions

| File | Purpose |
|------|---------|
| **Variable.cs** | CSP variable representing each cell with coordinates, value, and domain |
| **Sudoku.cs** | Grid operations: validation, neighbor detection, printing |
| **CspSolver.cs** | Core CSP algorithm: backtracking, heuristics, domain propagation |
| **SudokuGenerator.cs** | Generates random valid puzzles with configurable difficulty |
| **Program.cs** | User interface: input handling, solver execution, result display |

---

## 🧩 CSP Components

### Variables

Each cell `(row, col)` in the 6×6 grid is a CSP variable with:

- **Coordinates**: `(Row, Col)` position in the grid
- **Value**: Current assignment (0 if unassigned)
- **Domain**: Set of possible values `{1, 2, 3, 4, 5, 6}` minus conflicting values

**Example:**
```
Cell at (2, 3):
  - Value: 0 (unassigned)
  - Domain: {1, 3, 5} (2, 4, 6 are blocked by constraints)
```

### Domains

Domains are dynamically calculated based on constraints:

```csharp
Domain = {1, 2, 3, 4, 5, 6} 
         - values_in_same_row 
         - values_in_same_column 
         - values_in_same_2×3_block
```

**Domain updates:**
- **Forward**: After assignment, remove the value from all neighbor domains
- **Backward**: On backtracking, restore saved domains

### Constraints

Three types of constraints ensure validity:

1. **Row constraint**: No duplicate values in any row
2. **Column constraint**: No duplicate values in any column
3. **Block constraint**: No duplicate values in any 2×3 block

**Block structure (6 blocks total):**
```
[Block 0] [Block 1]
[Block 2] [Block 3]
[Block 4] [Block 5]
```

Each block spans 2 rows and 3 columns.

---

## 🚀 Heuristics

### 1. MRV (Minimum Remaining Values)

**Type:** Variable selection heuristic  
**Principle:** Choose the variable with the **smallest domain** first

**Rationale:**
- Variables with fewer options are more likely to fail
- Detecting failures early reduces wasted computation
- "Fail-first" principle

**Example:**
```
Variable A: Domain = {1, 2, 3, 4}  → 4 options
Variable B: Domain = {2, 5}        → 2 options ✓ CHOOSE THIS
Variable C: Domain = {1, 3, 4, 6}  → 4 options
```

### 2. Degree Heuristic

**Type:** Variable selection heuristic / Tie-breaker  
**Principle:** Choose the variable with the **most unassigned neighbors**

**Two modes:**

#### A. Primary heuristic (when MRV is disabled)
Select the variable that constrains the most other variables

#### B. Tie-breaker (when MRV is enabled)
When multiple variables have the same minimum domain size, choose the one with highest degree

**Neighbor definition:**
A cell's neighbors are all cells in:
- Same row (5 neighbors)
- Same column (5 neighbors)  
- Same 2×3 block (5 neighbors)
- Total: up to 15 unique neighbors

**Example:**
```
Variables with domain size 2 (tie in MRV):
  - Variable A: 8 unassigned neighbors
  - Variable B: 12 unassigned neighbors ✓ CHOOSE THIS
  - Variable C: 6 unassigned neighbors
```

### 3. LCV (Least Constraining Value)

**Type:** Value ordering heuristic  
**Principle:** Try values that **eliminate fewest options** from neighbor domains first

**Rationale:**
- Leave maximum flexibility for future assignments
- Reduce likelihood of dead ends

**Example:**
```
Variable domain: {2, 4, 5}

Value 2: Would eliminate 2 from 8 neighbors  → Cost = 8
Value 4: Would eliminate 4 from 3 neighbors  → Cost = 3 ✓ TRY FIRST
Value 5: Would eliminate 5 from 10 neighbors → Cost = 10
```

### Heuristic Combinations

The solver supports all 8 possible combinations:

| MRV | Degree | LCV | Variable Selection | Value Ordering |
|-----|--------|-----|-------------------|----------------|
| ❌ | ❌ | ❌ | Row-major order | Natural order |
| ✅ | ❌ | ❌ | Smallest domain | Natural order |
| ❌ | ✅ | ❌ | Highest degree | Natural order |
| ❌ | ❌ | ✅ | Row-major order | Least constraining |
| ✅ | ✅ | ❌ | Smallest domain, ties by degree | Natural order |
| ✅ | ❌ | ✅ | Smallest domain | Least constraining |
| ❌ | ✅ | ✅ | Highest degree | Least constraining |
| ✅ | ✅ | ✅ | Smallest domain, ties by degree | Least constraining |

---

## 🔄 Algorithm Flow

### High-Level Overview

```
1. Initialize puzzle
   ├─→ Load grid (predefined or generated)
   ├─→ Create Variable objects for each cell
   └─→ Calculate initial domains

2. User selects heuristics
   ├─→ Enable/disable MRV
   ├─→ Enable/disable Degree
   └─→ Enable/disable LCV

3. Backtracking search
   ├─→ Select next unassigned variable (using heuristics)
   ├─→ Order domain values (using LCV if enabled)
   ├─→ Try each value
   │   ├─→ Assign value
   │   ├─→ Update neighbor domains
   │   ├─→ Recurse
   │   └─→ Backtrack if needed
   └─→ Return solution or failure

4. Display results
   ├─→ Show solution grid
   └─→ Print statistics
```

### Detailed Backtracking Algorithm

```csharp
bool Backtrack()
{
    // Base case: all variables assigned
    var unassignedVar = SelectNextVariable();
    if (unassignedVar == null)
        return true; // SUCCESS
    
    // Value ordering (using LCV if enabled)
    var orderedValues = OrderValues(unassignedVar);
    
    foreach (int value in orderedValues)
    {
        if (sudoku.IsValidPlacement(unassignedVar.Row, unassignedVar.Col, value))
        {
            // Make assignment
            AssignValue(unassignedVar, value);
            var savedDomains = SaveDomains();
            UpdateDomains(unassignedVar);
            
            // Recursive call
            if (Backtrack())
                return true; // SUCCESS
            
            // Undo assignment
            UnassignValue(unassignedVar);
            RestoreDomains(savedDomains);
        }
    }
    
    return false; // FAILURE
}
```

### Variable Selection Logic

```csharp
Variable SelectNextVariable()
{
    var unassigned = variables.Where(v => !v.IsAssigned).ToList();
    
    if (!unassigned.Any())
        return null;
    
    if (useMRV)
    {
        // Find variables with smallest domain
        int minDomainSize = unassigned.Min(v => v.Domain.Count);
        var candidates = unassigned.Where(v => v.Domain.Count == minDomainSize).ToList();
        
        if (useDegree && candidates.Count > 1)
        {
            // Break ties using degree heuristic
            return candidates.OrderByDescending(v => CalculateDegree(v)).First();
        }
        
        return candidates.First();
    }
    else if (useDegree)
    {
        // Use degree as primary heuristic
        return unassigned.OrderByDescending(v => CalculateDegree(v)).First();
    }
    else
    {
        // Default: row-major order
        return unassigned.OrderBy(v => v.Row).ThenBy(v => v.Col).First();
    }
}
```

### Value Ordering Logic

```csharp
IEnumerable<int> OrderValues(Variable variable)
{
    if (!useLCV)
        return variable.Domain;
    
    // Calculate constraining count for each value
    var valueCosts = variable.Domain.Select(value => new
    {
        Value = value,
        Cost = CalculateConstrainingCount(variable, value)
    }).OrderBy(x => x.Cost);
    
    return valueCosts.Select(x => x.Value);
}
```

---

## 💻 Usage

### Running the Application

1. **Compile and run:**
   ```bash
   dotnet run
   ```

2. **Choose puzzle source:**
   ```
   Generate random puzzle? (y/n): y
   ```

3. **Select difficulty** (if generating):
   ```
   Select difficulty:
     1 - Easy (42% of empty cells)
     2 - Medium (64% of empty cells)
     3 - Hard (86% of empty cells)
   Enter choice (1-3): 3
   ```

4. **Enable heuristics:**
   ```
   Enable MRV (Minimum Remaining Values)? (y/n): y
   Enable Degree heuristic? (y/n): y
   Enable LCV (Least Constraining Value)? (y/n): y
   ```

5. **View results:**
   ```
    Solution found:
    0 1 2   3 4 5
    -------------
    0|2 6 1 | 3 4 5|
    1|3 4 5 | 6 1 2|
    -------------
    2|5 3 2 | 4 6 1|
    3|4 1 6 | 2 5 3|
    -------------
    4|1 2 4 | 5 3 6|
    5|6 5 3 | 1 2 4|
    -------------

   Statistics:
     Backtracks: 8
     Max recursion depth: 31
     Time elapsed: 13ms
   ```

---

## 🎓 Key Concepts

### Forward Checking

After assigning a value to a variable:
1. Remove that value from all neighbor domains
2. Detect early failures (empty domains)
3. Prune search space

### Domain Restoration

On backtracking:
1. Save domain states before assignment
2. Restore domains when undoing assignment
3. Maintain consistency

---

## 🔧 Technical Details

### Time Complexity

- **Worst case:** O(d^n) where d=domain size and n=number of empty cells
- **With heuristics:** Significantly reduced in practice

### Space Complexity

- **Grid storage:** O(size²) for the grid
- **Domain storage:** O(n·d) where n=empty cells, d=domain size
- **Recursion stack:** O(n) for backtracking depth

---

## 🎯 Learning Outcomes

This project demonstrates:

1. ✅ **CSP modeling** - Variables, domains, constraints
2. ✅ **Backtracking search** - Systematic exploration with pruning
3. ✅ **Heuristic optimization** - Smart variable/value ordering
4. ✅ **State management** - Domain saving/restoration
5. ✅ **Clean code principles** - Separation of concerns, SOLID
6. ✅ **Algorithm analysis** - Performance measurement and comparison

---

## 👤 Author

**Yahotin Nazarii**

---

*Created as a demonstration of CSP techniques and clean code architecture in C#.*