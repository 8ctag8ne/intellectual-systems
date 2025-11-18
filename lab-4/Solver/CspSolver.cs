using System;
using System.Collections.Generic;
using System.Linq;
using SudokuCSP.Models;

namespace SudokuCSP.Solver
{
    /// <summary>
    /// CSP Solver implementing backtracking with MRV, Degree, and LCV heuristics
    /// </summary>
    public class CspSolver
    {
        private Sudoku sudoku;
        private List<Variable> variables;
        private bool useMRV;
        private bool useDegree;
        private bool useLCV;
        
        // Statistics
        private int backtrackCount;
        private int maxDepth;
        private int currentDepth;

        public CspSolver(Sudoku sudoku, bool useMRV, bool useDegree, bool useLCV)
        {
            this.sudoku = sudoku;
            this.useMRV = useMRV;
            this.useDegree = useDegree;
            this.useLCV = useLCV;
            this.variables = new List<Variable>();
            
            InitializeVariables();
        }

        private void InitializeVariables()
        {
            for (int row = 0; row < Sudoku.Size; row++)
            {
                for (int col = 0; col < Sudoku.Size; col++)
                {
                    int value = sudoku.GetValue(row, col);
                    var variable = new Variable(row, col, value);
                    
                    if (value == 0)
                        variable.Domain = CalculateDomain(row, col);
                    
                    variables.Add(variable);
                }
            }
        }

        private List<int> CalculateDomain(int row, int col)
        {
            var domain = new List<int>();
            for (int value = 1; value <= Sudoku.Size; value++)
            {
                if (sudoku.IsValidPlacement(row, col, value))
                    domain.Add(value);
            }
            return domain;
        }

        public bool Solve()
        {
            backtrackCount = 0;
            maxDepth = 0;
            currentDepth = 0;
            
            bool result = Backtrack();
            
            Console.WriteLine($"\nStatistics:");
            Console.WriteLine($"  Backtracks: {backtrackCount}");
            Console.WriteLine($"  Max recursion depth: {maxDepth}");
            
            return result;
        }

        private bool Backtrack()
        {
            currentDepth++;
            maxDepth = Math.Max(maxDepth, currentDepth);

            var unassignedVar = SelectNextVariable();
            
            if (unassignedVar == null)
            {
                currentDepth--;
                return true; // All variables assigned
            }

            var orderedValues = OrderValues(unassignedVar);

            foreach (int value in orderedValues)
            {
                if (sudoku.IsValidPlacement(unassignedVar.Row, unassignedVar.Col, value))
                {
                    // Make assignment
                    AssignValue(unassignedVar, value);
                    
                    // Save domains for backtracking
                    var savedDomains = SaveDomains();
                    
                    // Update domains after assignment
                    UpdateDomains(unassignedVar);

                    if (Backtrack())
                    {
                        currentDepth--;
                        return true;
                    }

                    // Backtrack
                    backtrackCount++;
                    UnassignValue(unassignedVar);
                    RestoreDomains(savedDomains);
                }
            }

            currentDepth--;
            return false;
        }

        private Variable? SelectNextVariable()
        {
            var unassigned = variables.Where(v => !v.IsAssigned).ToList();
            
            if (unassigned.Count == 0)
                return null;

            if (useMRV)
            {
                // Find minimum domain size
                int minDomainSize = unassigned.Min(v => v.Domain.Count);
                var candidates = unassigned.Where(v => v.Domain.Count == minDomainSize).ToList();

                if (useDegree && candidates.Count > 1)
                {
                    // Break ties with degree heuristic
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

        private int CalculateDegree(Variable variable)
        {
            int degree = 0;
            var neighbors = sudoku.GetNeighbors(variable.Row, variable.Col);
            
            foreach (var (row, col) in neighbors.Distinct())
            {
                var neighborVar = variables.FirstOrDefault(v => v.Row == row && v.Col == col);
                if (neighborVar != null && !neighborVar.IsAssigned)
                    degree++;
            }
            
            return degree;
        }

        private IEnumerable<int> OrderValues(Variable variable)
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

        private int CalculateConstrainingCount(Variable variable, int value)
        {
            int count = 0;
            var neighbors = sudoku.GetNeighbors(variable.Row, variable.Col);

            foreach (var (row, col) in neighbors.Distinct())
            {
                var neighborVar = variables.FirstOrDefault(v => v.Row == row && v.Col == col);
                if (neighborVar != null && !neighborVar.IsAssigned && neighborVar.Domain.Contains(value))
                    count++;
            }

            return count;
        }

        private void AssignValue(Variable variable, int value)
        {
            variable.Value = value;
            sudoku.SetValue(variable.Row, variable.Col, value);
        }

        private void UnassignValue(Variable variable)
        {
            variable.Value = 0;
            sudoku.SetValue(variable.Row, variable.Col, 0);
        }

        private Dictionary<Variable, List<int>> SaveDomains()
        {
            return variables
                .Where(v => !v.IsAssigned)
                .ToDictionary(v => v, v => new List<int>(v.Domain));
        }

        private void RestoreDomains(Dictionary<Variable, List<int>> savedDomains)
        {
            foreach (var kvp in savedDomains)
            {
                kvp.Key.Domain = kvp.Value;
            }
        }

        private void UpdateDomains(Variable assignedVar)
        {
            var neighbors = sudoku.GetNeighbors(assignedVar.Row, assignedVar.Col);

            foreach (var (row, col) in neighbors.Distinct())
            {
                var neighborVar = variables.FirstOrDefault(v => v.Row == row && v.Col == col);
                if (neighborVar != null && !neighborVar.IsAssigned)
                {
                    neighborVar.Domain.Remove(assignedVar.Value);
                }
            }
        }
    }
}
