using System.Collections.Generic;

namespace SudokuCSP.Models
{
    /// <summary>
    /// Represents a single cell/variable in the Sudoku grid
    /// </summary>
    public class Variable
    {
        public int Row { get; set; }
        public int Col { get; set; }
        public int Value { get; set; }
        public List<int> Domain { get; set; }

        public Variable(int row, int col, int value = 0)
        {
            Row = row;
            Col = col;
            Value = value;
            Domain = new List<int>();
        }

        public bool IsAssigned => Value != 0;

        public Variable Clone()
        {
            return new Variable(Row, Col, Value)
            {
                Domain = new List<int>(Domain)
            };
        }
    }
}